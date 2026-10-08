"""Run only packaged workers; model text is never a command line."""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path


class NativeError(RuntimeError):
    def __init__(self, code: str, message: str = "Native worker failed"):
        super().__init__(message)
        self.code = code


class PowerShellWorker:
    def __init__(self, timeout: float = 20):
        if not 1 <= timeout <= 45:
            raise ValueError("Worker timeout must be 1–45 seconds")
        self.timeout = timeout

    def run(self, worker: str, operation: str, payload: dict) -> dict:
        command = self._command(worker, operation)
        try:
            completed = subprocess.run(
                command, input=json.dumps(payload, allow_nan=False), text=True,
                encoding="utf-8", capture_output=True, timeout=self.timeout, shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except subprocess.TimeoutExpired as exc:
            raise NativeError("timeout", "Native worker timed out; mutation outcome may need inspection") from exc
        except OSError as exc:
            raise NativeError("worker_unavailable") from exc
        return self._decode(completed)

    def run_cancellable(self, worker, operation, payload, cancelled):
        command = self._command(worker, operation)
        if cancelled.is_set():
            raise NativeError('mouse_input_cancelled')
        with tempfile.TemporaryDirectory(prefix='troubleshoot-mouse-') as directory:
            marker = Path(directory) / 'cancel'
            wire = json.dumps({**payload, 'cancel_file': str(marker)}, allow_nan=False)
            input_file = Path(directory) / 'input.json'
            input_file.write_text(wire, encoding='utf-8')
            input_stream = input_file.open('rb')
            try:
                process = subprocess.Popen(command, stdin=input_stream, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, encoding='utf-8', shell=False,
                    creationflags=subprocess.CREATE_NO_WINDOW)
            except OSError as exc:
                input_stream.close()
                raise NativeError('worker_unavailable') from exc
            deadline = time.monotonic() + self.timeout
            try:
                while True:
                    if cancelled.is_set():
                        marker.touch(exist_ok=True)
                    try:
                        stdout, stderr = process.communicate(timeout=0.05)
                        break
                    except subprocess.TimeoutExpired:
                        if time.monotonic() >= deadline:
                            process.kill()
                            process.communicate()
                            raise NativeError('timeout')
                return self._decode(subprocess.CompletedProcess(command, process.returncode, stdout, stderr))
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
                input_stream.close()

    def _command(self, worker, operation):
        if os.name != "nt":
            raise NativeError("unsupported_platform", "Windows interactive session required")
        scripts = {
            "diagnostics": Path(__file__).with_name("diagnostics.ps1"),
            "desktop": Path(__file__).parent.parent / "desktop" / "worker.ps1",
        }
        operations = {
            "diagnostics": {"system_snapshot", "network_snapshot", "spooler_status", "start_spooler", "restore_spooler_stopped"},
            "desktop": {"list_targets", "observe", "capture", "toggle_checkbox", "graceful_close",
                        "mouse_move", "mouse_click", "mouse_double_click", "mouse_scroll", "mouse_drag"},
        }
        if worker not in scripts or operation not in operations[worker]:
            raise NativeError("unregistered_operation")
        executable = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        return [str(executable), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                   "-File", str(scripts[worker]), "-Operation", operation]

    def _decode(self, completed):
        if len(completed.stdout) > 12_000_000:
            raise NativeError("oversized_output")
        try:
            reply = json.loads(completed.stdout.lstrip("\ufeff").strip())
        except (ValueError, TypeError) as exc:
            raise NativeError("invalid_output", "Native worker did not return structured evidence") from exc
        if not isinstance(reply, dict) or reply.get("ok") is not True:
            raise NativeError(str(reply.get("code", "native_failure")) if isinstance(reply, dict) else "native_failure")
        if completed.returncode:
            raise NativeError("worker_exit")
        if not isinstance(reply.get("evidence"), dict):
            raise NativeError("invalid_output")
        return reply["evidence"]
