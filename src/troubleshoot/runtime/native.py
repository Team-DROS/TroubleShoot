"""Member 3 bridge to the unchanged Member 1 executors.

No desktop input or service mutation happens without an exact native approval.
Model-facing actions exclude capture without consent and the recovery worker.
"""

import asyncio
import copy
import hashlib
import json
import os
import subprocess
import threading
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from troubleshoot.contracts import Check, ContractError, ExecutionResult, Observation, Target, require_target
from troubleshoot.desktop.executor import DESKTOP_VALIDATORS, DesktopExecutor
from troubleshoot.desktop.recovery import CheckboxRecovery
from troubleshoot.windows.policy import ExecutionContext
from troubleshoot.windows.registry import WINDOWS_VALIDATORS, WindowsExecutor
from troubleshoot.runtime.ports import Operation, RuntimeFailure, Snapshot
from troubleshoot.runtime.powershell_worker import PersistentPowerShellWorker


def now():
    return datetime.now(timezone.utc).isoformat()


class NativeExecutorAdapter:
    native_authorization = True

    def __init__(self, windows=None, desktop=None, *, recovery_dir=None, desktop_repairs=False,
                 symptom_verifier=None, worker=None):
        self.recovery_dir = Path(recovery_dir or Path.cwd() / "data" / "recovery")
        self.worker = worker
        self.windows = windows if windows is not None else WindowsExecutor(worker=worker, recovery_dir=self.recovery_dir)
        self.desktop = desktop if desktop is not None else DesktopExecutor(worker=worker)
        self.checkbox_recovery = CheckboxRecovery(self.desktop, self.recovery_dir)
        self.symptom_verifier = symptom_verifier
        self.permissions_ready = False
        # This is an explicitly logical system scope, not a fabricated HWND.
        self.system_target = Target(1, os.getpid(), now())
        self.machine = hashlib.sha256((os.environ.get("COMPUTERNAME", "") + "|" + str(Path.home())).encode()).hexdigest()
        # An environment switch alone cannot establish a real symptom verifier.
        self.desktop_repairs = desktop_repairs and callable(symptom_verifier)
        self.operations = {name: Operation(validate, name == "start_spooler",
            "Spooler service state only; actual printing remains unverified" if name in {"start_spooler", "spooler_status"}
            else "Fresh diagnostic evidence; original symptom remains unverified",
            "Conditional service restoration; uncertain outcomes require operator inspection" if name == "start_spooler" else "No mutation")
            for name, validate in WINDOWS_VALIDATORS.items()}
        for name, validate in DESKTOP_VALIDATORS.items():
            if name != "inspect_target" and not (name == "toggle_checkbox" and self.desktop_repairs):
                continue
            self.operations[name] = Operation(validate, name != "inspect_target",
                "Selected control/window state only; original symptom remains unverified",
                "Durable checkbox baseline; restoration requires fresh target checks and a new approval")
        self.snapshots = {}

    def status(self):
        try:
            pending = len(list(self.recovery_dir.glob("*.json"))) if self.recovery_dir.exists() else 0
        except OSError:
            pending = -1
        return {"platform": "windows", "desktop_repairs": self.desktop_repairs,
                "capture_available": False, "pending_recovery_records": pending,
                "worker_transport": "persistent" if self.worker else "injected_or_owner_default",
                "operations": list(self.operations)}

    async def prepare_repair(self):
        await asyncio.to_thread(self._private_recovery_directory)

    async def close(self):
        if self.worker:
            await asyncio.to_thread(self.worker.close)

    def require_recovery_ready(self):
        if self.status()["pending_recovery_records"] != 0:
            raise RuntimeFailure("recovery_required")

    def operations_for(self, target):
        names = WINDOWS_VALIDATORS if target == self.system_target else DESKTOP_VALIDATORS
        return {name: op for name, op in self.operations.items() if name in names}

    async def targets(self):
        items = await asyncio.to_thread(self.desktop.list_targets)
        return [{"label": "This computer (system diagnostics)", "target": asdict(self.system_target), "scope": "system"}] + [
            {"label": str(item.get("title", "Selected window"))[:120], "target": item["target"], "scope": "window"}
            for item in items[:32]]

    async def observe(self, target):
        if target == self.system_target:
            facts = {}
            for operation, key in (("system_snapshot", "os"), ("spooler_status", "spooler")):
                result = await asyncio.to_thread(self.windows.diagnose, operation, {})
                if result.status != "ok":
                    raise RuntimeFailure("native_observation_failed")
                facts[key] = copy.deepcopy(result.evidence)
            observation = Observation(uuid.uuid4().hex, facts["spooler"]["observed_at"], target)
            snapshot = Snapshot(observation, facts)
            raw = None
        else:
            raw = await asyncio.to_thread(self.desktop.observe, target)
            bounds = raw.metadata["bounds"]
            if isinstance(bounds, dict):
                bounds = (bounds["left"], bounds["top"], bounds["left"] + bounds["width"], bounds["top"] + bounds["height"])
            observation = Observation(raw.observation.observation_id, raw.observation.observed_at,
                                      raw.observation.target, tuple(bounds), raw.metadata["dpi"])
            snapshot = Snapshot(observation, copy.deepcopy(raw.metadata))
        self.snapshots[observation.observation_id] = (snapshot, raw)
        while len(self.snapshots) > 100:
            del self.snapshots[next(iter(self.snapshots))]
        return snapshot

    def _private_recovery_directory(self):
        """Restrict Windows ACLs before the owner executor persists a mutation."""
        self.require_recovery_ready()
        if self.permissions_ready:
            return
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        marker = self.recovery_dir / ".machine"
        if marker.exists() and marker.read_text(encoding="utf-8") != self.machine:
            raise RuntimeFailure("recovery_machine_mismatch")
        if os.name == "nt":
            powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
            reply = subprocess.run([str(powershell), "-NoProfile", "-NonInteractive", "-Command",
                "[Security.Principal.WindowsIdentity]::GetCurrent().User.Value"],
                capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            sid = reply.stdout.strip()
            if reply.returncode or not sid.startswith("S-1-"):
                raise RuntimeFailure("recovery_permissions_failed")
            icacls = Path(os.environ["SystemRoot"]) / "System32/icacls.exe"
            acl = subprocess.run([str(icacls), str(self.recovery_dir), "/inheritance:r", "/grant:r",
                f"*{sid}:(OI)(CI)F", "*S-1-5-18:(OI)(CI)F"], capture_output=True,
                timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            if acl.returncode:
                raise RuntimeFailure("recovery_permissions_failed")
        else:
            self.recovery_dir.chmod(0o700)
        marker.write_text(self.machine, encoding="utf-8")
        self.permissions_ready = True

    async def execute_authorized(self, action, observation, mode, cancelled, run_id, authorize):
        snapshot, raw = self.snapshots[observation.observation_id]
        require_target(action, snapshot.observation, datetime.now(timezone.utc))
        if action.operation not in self.operations_for(action.target):
            raise ContractError("Operation does not belong to selected scope")
        self.operations[action.operation].validate(action.arguments)
        loop = asyncio.get_running_loop()
        stop = threading.Event()
        consumed = threading.Event()
        desktop_record = []

        def consume(request):
            if stop.is_set() or consumed.is_set() or (request.run_id, request.action_id, request.operation) != (
                    run_id, action.action_id, action.operation):
                return False
            future = asyncio.run_coroutine_threadsafe(authorize(request), loop)
            try:
                accepted = future.result(timeout=6) is True
            except Exception:
                future.cancel()
                accepted = False
            if accepted:
                if action.operation == "graceful_close":
                    record = self.recovery_dir / f"{uuid.uuid4()}.json"
                    try:
                        record.write_text(json.dumps({"state": "pending", "machine": self.machine,
                            "run_id": run_id, "action": action.to_dict(),
                            "authorization_fingerprint": request.fingerprint}), encoding="utf-8")
                    except OSError:
                        return False
                    desktop_record.append(record)
                consumed.set()
            return accepted and not stop.is_set()

        context = ExecutionContext(run_id, action.action_id, mode, stop, consume)

        def dispatch():
            if cancelled.is_set():
                stop.set()
            if stop.is_set():
                from troubleshoot.windows.policy import ExecutionResult as NativeResult
                return NativeResult("cancelled", {})
            if action.operation == "start_spooler":
                self._private_recovery_directory()
                return self.windows.start_spooler(action.arguments, context)
            if action.operation in WINDOWS_VALIDATORS:
                return self.windows.diagnose(action.operation, action.arguments)
            if action.operation == "inspect_target":
                from troubleshoot.windows.policy import ExecutionResult as NativeResult
                return NativeResult("ok", self.desktop.observe(action.target).metadata)
            if action.operation == "toggle_checkbox":
                self._private_recovery_directory()
                return self.checkbox_recovery.apply(raw, action.arguments, context)
            if action.operation == "graceful_close":
                self._private_recovery_directory()
                return self.desktop.graceful_close(raw, action.arguments, context)
            raise ContractError("Operation unavailable")

        async def relay_cancel():
            await cancelled.wait()
            stop.set()

        worker = asyncio.create_task(asyncio.to_thread(dispatch))
        monitor = asyncio.create_task(relay_cancel())
        try:
            result = await asyncio.shield(worker)
        except asyncio.CancelledError:
            # Drain the bounded native worker before the session releases its lock.
            stop.set()
            await asyncio.shield(worker)
            raise
        finally:
            monitor.cancel()
            await asyncio.gather(monitor, return_exceptions=True)
        if result.changed is False:
            for record in desktop_record:
                record.unlink(missing_ok=True)
        recovery = "none"
        if result.evidence.get("recovered") is True:
            recovery = "restored"
        elif result.changed is None or result.evidence.get("pending_recovery"):
            recovery = "pending"
        elif action.operation in {"toggle_checkbox", "graceful_close"} and result.changed is True:
            recovery = "pending"  # baseline retained until separately approved restoration
        return ExecutionResult(result.status, recovery)

    async def verify(self, action, complaint):
        """Fresh facts, with an explicit failing symptom check until a real verifier exists."""
        checks = []
        if action.operation in {"start_spooler", "spooler_status"}:
            current = await asyncio.to_thread(self.windows.diagnose, "spooler_status", {})
            actual = str(current.evidence.get("status", "unavailable"))
            checks.append(Check("Spooler service state", "Running", actual,
                                current.status == "ok" and actual == "Running", now()))
        elif action.operation == "toggle_checkbox":
            current = await asyncio.to_thread(self.desktop.observe, action.target)
            control = next((c for c in current.metadata.get("controls", [])
                            if c["control_id"] == action.arguments["control_id"]), {})
            actual = str(control.get("toggle_state", "unavailable"))
            checks.append(Check("Selected checkbox state", action.arguments["state"], actual,
                                actual == action.arguments["state"], now()))
        elif action.operation == "graceful_close":
            targets = await asyncio.to_thread(self.desktop.list_targets)
            present = any(item["target"]["handle"] == action.target.handle for item in targets)
            checks.append(Check("Selected window in permitted inventory", "Absent",
                                "Present" if present else "Absent", not present, now()))
        elif action.operation == "inspect_target":
            current = await asyncio.to_thread(self.desktop.observe, action.target)
            checks.append(Check("Selected window identity", "Same identity",
                                "Same identity", current.observation.target == action.target, now()))
        elif action.operation in {"system_snapshot", "network_snapshot"}:
            current = await asyncio.to_thread(self.windows.diagnose, action.operation, {})
            checks.append(Check("Fresh native diagnostic", "Collected", current.status,
                                current.status == "ok", now()))
        # Neither OS facts, adapter state, service state nor control state proves the complaint.
        if action.operation == "toggle_checkbox" and self.symptom_verifier:
            checks.extend(await self.symptom_verifier(action, complaint))
        else:
            checks.append(Check("Original symptom", "Measured symptom restored",
                                "No symptom-specific verifier is integrated", False, now()))
        return checks


def native_executor_from_env():
    if os.name != "nt":
        return None
    return NativeExecutorAdapter(
        recovery_dir=Path(os.getenv("TROUBLESHOOT_RECOVERY_DIR") or str(Path.cwd() / "data" / "recovery")),
        worker=PersistentPowerShellWorker(), desktop_repairs=False)
