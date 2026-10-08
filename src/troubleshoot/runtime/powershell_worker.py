"""Serialized persistent transport; invokes only unchanged owner worker scripts.

One process caches native assemblies/types, avoiding process startup between
fresh observation and input. Every request remains bounded; failures are never
automatically retried. Mouse primitives remain unavailable in this transport.
"""

import json
import os
import queue
import subprocess
import threading
from pathlib import Path

from troubleshoot.windows.runner import NativeError


class PersistentPowerShellWorker:
    operations = {
        "diagnostics": {"system_snapshot", "network_snapshot", "spooler_status", "start_spooler", "restore_spooler_stopped"},
        "desktop": {"list_targets", "observe", "capture", "toggle_checkbox", "graceful_close"},
    }

    def __init__(self, timeout=20):
        if not 1 <= timeout <= 45:
            raise ValueError("Worker timeout must be 1–45 seconds")
        self.timeout = timeout
        self.lock = threading.Lock()
        self.process = None
        self.replies = None
        self.reader = None

    def _start(self):
        if os.name != "nt":
            raise NativeError("unsupported_platform")
        executable = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        command = [str(executable), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                   "-File", str(Path(__file__).with_name("persistent-worker.ps1"))]
        try:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, encoding="utf-8", shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW)
        except OSError as exc:
            raise NativeError("worker_unavailable") from exc
        replies = queue.Queue(maxsize=1)

        def read():
            try:
                while True:
                    line = process.stdout.readline(12_000_002)
                    replies.put(line)
                    if not line or len(line) > 12_000_000:
                        return
            except (OSError, ValueError):
                pass

        self.process, self.replies = process, replies
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def _close(self):
        process, reader = self.process, self.reader
        self.process = None
        if process is None:
            return
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
        if reader:
            reader.join(timeout=1)
        process.stdin.close()
        process.stdout.close()

    def close(self):
        with self.lock:
            self._close()

    def run(self, worker, operation, payload):
        if operation not in self.operations.get(worker, set()):
            raise NativeError("unregistered_operation")
        wire = json.dumps({"worker": worker, "operation": operation,
                           "payload": json.dumps(payload, allow_nan=False)}, allow_nan=False)
        if len(wire) > 1_000_000:
            raise NativeError("oversized_request")
        with self.lock:
            if self.process is None:
                self._start()
            try:
                self.process.stdin.write(wire + "\n")
                self.process.stdin.flush()
                line = self.replies.get(timeout=self.timeout)
                if not line or len(line) > 12_000_000:
                    raise NativeError("invalid_output")
                reply = json.loads(line)
                if not isinstance(reply, dict):
                    raise NativeError("invalid_output")
                if reply.get("ok") is not True:
                    # Preserve only owner machine-readable codes; never raw output.
                    code = reply.get("code", "native_failure")
                    if not isinstance(code, str) or len(code) > 80 or not all(c.isalnum() or c == '_' for c in code):
                        code = "native_failure"
                    raise NativeError(code)
                if not isinstance(reply.get("evidence"), dict):
                    raise NativeError("invalid_output")
                return reply["evidence"]
            except queue.Empty as exc:
                self._close()
                raise NativeError("timeout") from exc
            except (OSError, ValueError) as exc:
                self._close()
                raise NativeError("invalid_output") from exc
            except NativeError:
                self._close()
                raise
