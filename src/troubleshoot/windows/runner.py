"""Run only packaged workers; model text is never a command line."""

import json
import os
import subprocess
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
        if os.name != "nt":
            raise NativeError("unsupported_platform", "Windows interactive session required")
        scripts = {
            "diagnostics": Path(__file__).with_name("diagnostics.ps1"),
            "desktop": Path(__file__).parent.parent / "desktop" / "worker.ps1",
        }
        operations = {
            "diagnostics": {"system_snapshot", "network_snapshot", "spooler_status", "start_spooler", "restore_spooler_stopped"},
            "desktop": {"list_targets", "observe", "capture", "toggle_checkbox", "graceful_close"},
        }
        if worker not in scripts or operation not in operations[worker]:
            raise NativeError("unregistered_operation")
        executable = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        command = [str(executable), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                   "-File", str(scripts[worker]), "-Operation", operation]
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
