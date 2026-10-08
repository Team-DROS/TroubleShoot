"""Desktop boundary with fresh target binding and injected runtime approval."""

import base64
from dataclasses import dataclass
from datetime import datetime, timezone

from troubleshoot.contracts import ContractError, Observation, Target, fields
from troubleshoot.windows.policy import ExecutionContext, ExecutionResult
from troubleshoot.windows.runner import NativeError, PowerShellWorker
from .mouse import MOUSE_VALIDATORS, require_control, validate_point


def no_arguments(payload: dict) -> dict:
    return dict(fields(payload, set()))


def toggle_arguments(payload: dict) -> dict:
    fields(payload, {"control_id", "state"})
    if not isinstance(payload["control_id"], str) or not 1 <= len(payload["control_id"]) <= 256:
        raise ContractError("Invalid control ID")
    if payload["state"] not in {"On", "Off"}:
        raise ContractError("Checkbox state must be On or Off")
    return dict(payload)


DESKTOP_VALIDATORS = {
    "inspect_target": no_arguments,
    "capture_target": no_arguments,
    "toggle_checkbox": toggle_arguments,
    "graceful_close": no_arguments,
}
DESKTOP_VALIDATORS.update(MOUSE_VALIDATORS)


@dataclass(frozen=True)
class WindowObservation:
    observation: Observation
    metadata: dict

    def wire(self) -> dict:
        import copy
        return {**copy.deepcopy(self.metadata), "observation_id": self.observation.observation_id}


@dataclass(frozen=True)
class WindowCapture:
    snapshot: WindowObservation
    png: bytes


class DesktopExecutor:
    def __init__(self, worker=None, clock=None):
        self.worker = worker if worker is not None else PowerShellWorker()
        self.clock = clock if clock is not None else lambda: datetime.now(timezone.utc)

    def list_targets(self) -> list[dict]:
        return self.worker.run("desktop", "list_targets", {})["targets"]

    def mouse_action(self, operation: str, snapshot: WindowObservation, arguments: dict,
                     context: ExecutionContext) -> ExecutionResult:
        if operation not in MOUSE_VALIDATORS:
            raise ContractError('Unregistered mouse operation')
        arguments = MOUSE_VALIDATORS[operation](arguments)
        try:
            current = self._ready(snapshot)
            for key in ('client_bounds', 'virtual_screen', 'cursor'):
                if current.metadata.get(key) != snapshot.metadata.get(key) or key not in current.metadata:
                    raise ContractError('Client/monitor/cursor state changed')
            observed = next((c for c in snapshot.metadata['controls'] if c['control_id'] == arguments['control_id']), None)
            actual = next((c for c in current.metadata['controls'] if c['control_id'] == arguments['control_id']), None)
            if observed is None or actual != observed:
                raise ContractError('Mouse control changed')
            require_control(operation, actual)
            validate_point(snapshot, actual, arguments['x'], arguments['y'])
            if operation == 'mouse_drag':
                validate_point(snapshot, actual, arguments['to_x'], arguments['to_y'])
            context.require_mutation(operation, arguments, snapshot.wire(),
                f"{operation} on selected {actual['type']} '{actual['name']}' at image pixel ({arguments['x']}, {arguments['y']}).")
            snapshot.observation.require_fresh(self.clock())
            result = self.worker.run_cancellable('desktop', operation,
                {'snapshot': snapshot.wire(), 'control': observed, 'arguments': arguments}, context.cancelled)
            if context.cancelled.is_set() or result.get('cancelled') is True:
                return ExecutionResult('cancelled', result, None,
                    ('An input may have occurred; obtain a fresh observation before recovery.',))
            # Delivery is NOT application/symptom success, even when SendInput succeeds.
            return ExecutionResult('partial' if result.get('input_delivered') is True else 'failed', result, None,
                ('Mouse delivery/cursor position only; independently verify the control and original symptom.',))
        except ContractError as exc:
            return ExecutionResult('blocked', {'reason': str(exc)})
        except NativeError as exc:
            return ExecutionResult('cancelled' if exc.code in {'mouse_input_cancelled', 'emergency_stop'} else 'failed', {'error': exc.code}, None,
                ('Input outcome may be uncertain; no automatic retry or semantic undo.',))

    def observe(self, target: Target) -> WindowObservation:
        import uuid
        from dataclasses import asdict
        evidence = self.worker.run("desktop", "observe", {"target": asdict(target)})
        current = Target.from_dict(evidence["target"])
        if current != target:
            raise ContractError("Target was replaced")
        return WindowObservation(Observation(str(uuid.uuid4()), evidence["observed_at"], current), evidence)

    def capture(self, snapshot: WindowObservation, *, consent: bool = False) -> WindowCapture:
        if consent is not True:
            raise ContractError("Selected-window capture consent required")
        snapshot.observation.require_fresh(self.clock())
        evidence = self.worker.run("desktop", "capture", {"snapshot": snapshot.wire(), "capture_consent": True})
        png = base64.b64decode(evidence["png_base64"], validate=True)
        if not png.startswith(b"\x89PNG\r\n\x1a\n") or len(png) > 8_000_000:
            raise NativeError("invalid_capture")
        # Image bytes stay in memory; the API owns session-scoped image storage/auth.
        return WindowCapture(snapshot, png)

    def _ready(self, snapshot: WindowObservation):
        snapshot.observation.require_fresh(self.clock())
        current = self.observe(snapshot.observation.target)
        for key in ("bounds", "dpi"):
            if current.metadata[key] != snapshot.metadata[key]:
                raise ContractError("Window geometry or DPI changed")
        if current.metadata.get("foreground") is not True:
            raise ContractError("Selected window is not foreground")
        return current

    def toggle_checkbox(self, snapshot: WindowObservation, arguments: dict, context: ExecutionContext) -> ExecutionResult:
        arguments = toggle_arguments(arguments)
        try:
            current = self._ready(snapshot)
            match = next((item for item in current.metadata["controls"] if item["control_id"] == arguments["control_id"]), None)
            observed = next((item for item in snapshot.metadata["controls"] if item["control_id"] == arguments["control_id"]), None)
            if match is None or match != observed or match.get("type") != "CheckBox" or not match.get("enabled"):
                raise ContractError("Selected checkbox changed or is unavailable")
            if match.get("toggle_state") == arguments["state"]:
                return ExecutionResult("ok", {"postcondition_met": True, "already_selected": True})
            context.require_mutation("toggle_checkbox", arguments, snapshot.wire(),
                                     f"Set selected checkbox '{match['name']}' to {arguments['state']}.")
            # Approval can take time: fail stale, never use it for a new observation.
            snapshot.observation.require_fresh(self.clock())
            result = self.worker.run("desktop", "toggle_checkbox", {
                "snapshot": snapshot.wire(), "control": observed, "desired_state": arguments["state"],
            })
            if context.cancelled.is_set():
                return ExecutionResult("cancelled", result, None,
                                       ("Input may have occurred; reobserve the checkbox before continuing.",))
            return ExecutionResult("ok" if result.get("postcondition_met") is True else "failed", result, True,
                                   ("Only this selected checkbox state was checked; verify the original symptom separately.",))
        except ContractError as exc:
            return ExecutionResult("blocked", {"reason": str(exc)})
        except NativeError as exc:
            return ExecutionResult("failed", {"error": exc.code}, None,
                                   ("Reobserve before retrying; an interrupted input may already have happened.",))

    def graceful_close(self, snapshot: WindowObservation, arguments: dict, context: ExecutionContext) -> ExecutionResult:
        no_arguments(arguments)
        try:
            self._ready(snapshot)
            context.require_mutation("graceful_close", {}, snapshot.wire(),
                                     "Request graceful close of the selected application. Unsaved work may prompt; never force-close.")
            snapshot.observation.require_fresh(self.clock())
            result = self.worker.run("desktop", "graceful_close", {"snapshot": snapshot.wire()})
            if context.cancelled.is_set():
                return ExecutionResult("cancelled", result, None,
                                       ("Close request may have occurred; reobserve the application.",))
            return ExecutionResult("ok" if result.get("postcondition_met") is True else "failed", result, True,
                                   ("Closure alone does not prove the original app symptom is fixed; reopening is not implemented.",))
        except ContractError as exc:
            return ExecutionResult("blocked", {"reason": str(exc)})
        except NativeError as exc:
            return ExecutionResult("failed", {"error": exc.code}, None)
