"""Fixed operation registry and an approved stopped-Spooler recovery action."""

import json
import uuid
from pathlib import Path

from troubleshoot.contracts import ContractError, fields
from .policy import ExecutionContext, ExecutionResult
from .runner import NativeError, PowerShellWorker


def empty_arguments(payload: dict) -> dict:
    return dict(fields(payload, set()))


WINDOWS_VALIDATORS = {
    name: empty_arguments for name in ("system_snapshot", "network_snapshot", "spooler_status", "start_spooler")
}


class WindowsExecutor:
    def __init__(self, worker=None, recovery_dir: Path | None = None):
        self.worker = worker if worker is not None else PowerShellWorker()
        self.recovery_dir = recovery_dir

    def diagnose(self, operation: str, arguments: dict) -> ExecutionResult:
        if operation not in {"system_snapshot", "network_snapshot", "spooler_status"}:
            raise ContractError("Unregistered read-only operation")
        WINDOWS_VALIDATORS[operation](arguments)
        try:
            return ExecutionResult("ok", self.worker.run("diagnostics", operation, {}),
                                   limitations=("Diagnostic facts alone do not establish a root cause.",))
        except NativeError as exc:
            return ExecutionResult("failed", {"error": exc.code})

    def start_spooler(self, arguments: dict, context: ExecutionContext) -> ExecutionResult:
        empty_arguments(arguments)
        try:
            before = self.worker.run("diagnostics", "spooler_status", {})
            if before.get("status") != "Stopped":
                return ExecutionResult("blocked", {"before": before, "reason": "Spooler must be confirmed stopped"})
            context.require_mutation("start_spooler", {}, before,
                                     "Start Spooler; restore stopped state if verification fails or the run is cancelled.")
            if self.recovery_dir is None:
                raise ContractError("Durable recovery directory required")
            self.recovery_dir.mkdir(parents=True, exist_ok=True)
            record = self.recovery_dir / f"{uuid.uuid4()}.json"
            record.write_text(json.dumps({"operation": "start_spooler", "before": before,
                                          "run_id": context.run_id, "state": "pending"}), encoding="utf-8")
        except ContractError as exc:
            return ExecutionResult("blocked", {"reason": str(exc)})
        except NativeError as exc:
            return ExecutionResult("failed", {"error": exc.code})
        except OSError:
            return ExecutionResult("blocked", {"reason": "Cannot persist recovery record; no mutation performed"})
        started = False
        try:
            mutation = self.worker.run("diagnostics", "start_spooler", {"expected_status": "Stopped"})
            started = mutation.get("changed") is True
            after = self.worker.run("diagnostics", "spooler_status", {})
            if after.get("status") != "Running" or context.cancelled.is_set():
                raise NativeError("cancelled_or_verification_failed")
            record.unlink()
            return ExecutionResult("ok", {"before": before, "after": after, "postcondition_met": True}, True,
                                   ("Spooler running is partial evidence; an actual print still needs verification.",))
        except NativeError as exc:
            if exc.code in {"elevation_required", "service_state_changed"}:
                record.unlink()
                return ExecutionResult("blocked", {"error": exc.code, "reason": "No mutation performed; refresh state or obtain human elevation"})
            if not started:
                return ExecutionResult("failed", {"error": exc.code, "recovered": False,
                                                   "pending_recovery": record.name}, None,
                                       ("Mutation outcome is uncertain; retain the record and inspect before recovery.",))
            try:
                self.worker.run("diagnostics", "restore_spooler_stopped", {})
                restored = self.worker.run("diagnostics", "spooler_status", {})
                if restored.get("status") != "Stopped":
                    raise NativeError("recovery_verification_failed")
                record.unlink()
                return ExecutionResult("cancelled" if context.cancelled.is_set() else "failed",
                                       {"error": exc.code, "recovered": True, "after": restored}, False)
            except NativeError as recovery_error:
                return ExecutionResult("failed", {"error": exc.code, "recovered": False,
                                                   "recovery_error": recovery_error.code,
                                                   "pending_recovery": record.name}, None,
                                       ("Retain the durable record and inspect the service before a new repair.",))
