"""Bounded single-action runs with explicit provider and executor injection."""

import asyncio
import copy
import hashlib
import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from time import monotonic

from troubleshoot.contracts import (
    Check, ContractError, ExecutionResult, RunRequest, Target, event,
    parse_action, parse_decision, require_target, timestamp, verdict,
)
from troubleshoot.runtime.ports import RuntimeFailure


def utcnow():
    return datetime.now(timezone.utc)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass
class Run:
    id: str
    request: RunRequest
    target: Target | None
    events: list = field(default_factory=list)
    state: str = "running"
    recovery: str = "none"
    cancelled: asyncio.Event = field(default_factory=asyncio.Event)
    choice: asyncio.Future | None = None
    approval: dict | None = None
    task: asyncio.Task | None = None


class SessionManager:
    def __init__(self, providers=None, executor=None, *, simulation=False,
                 approval_seconds=60, run_seconds=90, tool_seconds=10):
        self.providers = dict(providers or {})
        self.executor = executor
        self.simulation = simulation
        self.runs = {}
        self.approval_seconds = approval_seconds
        self.run_seconds = run_seconds
        self.tool_seconds = tool_seconds
        self.tool_lock = asyncio.Lock()

    def status(self):
        return {
            "default_provider": "ollama", "simulation": self.simulation,
            "providers": {name: (self.providers[name].status() if name in self.providers else
                {"configured": False, "readiness": "unavailable", "model": None,
                 "images": False}) for name in ("ollama", "gemma_api")},
            "executor_available": self.executor is not None,
            "vision_available": False,
        }

    def get(self, run_id):
        if run_id not in self.runs:
            raise RuntimeFailure("run_not_found")
        return self.runs[run_id]

    def emit(self, run, kind, payload):
        run.events.append(event(str(len(run.events) + 1), kind, copy.deepcopy(payload)))

    def finish(self, run, result, limitation):
        if run.state == "complete":
            return
        run.approval = None
        self.emit(run, "complete", {"verdict": result, "recovery": run.recovery,
                  "limitations": [limitation], "simulation": self.simulation})
        run.state = "complete"

    def create(self, request, target=None):
        if request.mode == "repair" and any(r.recovery in {"pending", "failed"} for r in self.runs.values()):
            raise RuntimeFailure("recovery_required")
        if request.provider not in self.providers:
            raise RuntimeFailure("provider_unavailable")
        if not self.providers[request.provider].status()["configured"]:
            raise RuntimeFailure("provider_unavailable")
        if request.vision_enabled:
            raise RuntimeFailure("vision_unavailable")
        if target and self.executor is None:
            raise RuntimeFailure("executor_unavailable")
        if sum(r.state != "complete" for r in self.runs.values()) >= 4:
            raise RuntimeFailure("run_capacity")
        if len(self.runs) >= 100:
            old = next((key for key, r in self.runs.items() if r.state == "complete"), None)
            if old is None:
                raise RuntimeFailure("run_capacity")
            del self.runs[old]
        run = Run(secrets.token_urlsafe(18), request, target)
        self.runs[run.id] = run
        run.task = asyncio.create_task(self._drive(run))
        return run

    def cancel(self, run_id):
        run = self.get(run_id)
        if run.state != "complete":
            run.cancelled.set()
            run.approval = None
            if run.choice and not run.choice.done():
                run.choice.set_result(False)
        return {"state": run.state, "cancel_requested": run.cancelled.is_set(), "recovery": run.recovery}

    def decide(self, run_id, token, action_id, approve):
        run = self.get(run_id)
        approval = run.approval
        if (type(approve) is not bool or not isinstance(token, str) or not approval
                or run.cancelled.is_set() or run.choice.done()
                or monotonic() > approval["deadline"]
                or not secrets.compare_digest(token, approval["token"])
                or action_id != approval["action"]["action_id"]
                or digest({"run": run.id, "action": approval["action"]}) != approval["digest"]):
            raise RuntimeFailure("invalid_approval")
        run.approval = None  # consume before releasing the waiting worker
        run.choice.set_result(approve)
        return {"accepted": True}

    async def _drive(self, run):
        try:
            async with asyncio.timeout(self.run_seconds):
                await self._work(run)
        except TimeoutError:
            self.emit(run, "error", {"code": "run_timeout"})
            self.finish(run, "error", "Time budget exhausted; inspect recovery state.")
        except asyncio.CancelledError:
            self.finish(run, "cancelled", "Shutdown; in-flight changes may need recovery.")
        except Exception as exc:
            code = exc.code if isinstance(exc, RuntimeFailure) else (
                "policy_rejected" if isinstance(exc, ContractError) else "component_failure")
            # Never expose exception text: it can contain credentials/private model input.
            self.emit(run, "error", {"code": code})
            self.finish(run, "error", "No verified repair; see error code and recovery state.")

    def stopped(self, run):
        if run.cancelled.is_set():
            self.finish(run, "cancelled", "Cancellation requested; no further actions will start.")
            return True
        return False

    async def _tool(self, awaitable):
        async with asyncio.timeout(self.tool_seconds):
            return await awaitable

    async def _work(self, run):
        snapshot = None
        if run.target:
            snapshot = await self._tool(self.executor.observe(run.target))
            if snapshot.observation.target != run.target:
                raise ContractError("Wrong observation target")
            snapshot.observation.require_fresh(utcnow())
            self.emit(run, "observation", asdict(snapshot))
        if self.stopped(run):
            return
        operations = self.executor.operations if self.executor else {}
        registry = {name: op.validate for name, op in operations.items()}
        provider_request = {
            "request": asdict(run.request),
            "observation": asdict(snapshot) if snapshot else None,
            "operations": {name: {"mutates": op.mutates, "expected": op.expected,
                                   "recovery": op.recovery} for name, op in operations.items()},
        }
        decision = parse_decision(await self.providers[run.request.provider].decide(provider_request), registry)
        if self.stopped(run):
            return
        self.emit(run, "plan", decision)
        if decision["action"] is None:
            self.finish(run, "unresolved", "Diagnosis only; no symptom postcondition was measured.")
            return
        action = parse_action(decision["action"], registry)
        if snapshot is None:
            raise ContractError("An action needs an observation")
        require_target(action, snapshot.observation, utcnow())
        operation = operations[action.operation]
        if run.request.mode == "diagnose" and operation.mutates:
            raise ContractError("Diagnose-only cannot mutate")
        bound_action = copy.deepcopy(action.to_dict())
        bound_digest = digest({"run": run.id, "action": bound_action})
        if operation.mutates:
            run.state = "awaiting_approval"
            run.choice = asyncio.get_running_loop().create_future()
            token = secrets.token_urlsafe(32)
            run.approval = {"token": token, "action": bound_action,
                            "digest": bound_digest,
                            "deadline": monotonic() + self.approval_seconds}
            self.emit(run, "approval", {"token": token, "action": bound_action,
                      "expires_in_seconds": self.approval_seconds,
                      "expected": operation.expected, "recovery": operation.recovery})
            try:
                approved = await asyncio.wait_for(run.choice, self.approval_seconds)
            except TimeoutError:
                self.finish(run, "unresolved", "Approval expired; start a new run for fresh evidence.")
                return
            if self.stopped(run):
                return
            if not approved:
                self.finish(run, "unresolved", "Action rejected; no action executed.")
                return
        async with self.tool_lock:
            if self.stopped(run):
                return
            if operation.mutates and any(r.recovery in {"pending", "failed"} for r in self.runs.values()):
                raise RuntimeFailure("recovery_required")
            if digest({"run": run.id, "action": action.to_dict()}) != bound_digest:
                raise ContractError("Action changed after approval")
            # Old observations cannot authorize delayed or queued input.
            require_target(action, snapshot.observation, utcnow())
            fresh = await self._tool(self.executor.observe(run.target))
            fresh.observation.require_fresh(utcnow())
            if (fresh.observation.target != action.target
                    or fresh.observation.bounds != snapshot.observation.bounds
                    or fresh.observation.dpi != snapshot.observation.dpi):
                raise ContractError("Target changed; new run/approval required")
            if self.stopped(run):
                return
            require_target(action, snapshot.observation, utcnow())
            run.state = "executing"
            run.recovery = "pending" if operation.mutates else "none"
            result = await self._tool(self.executor.execute(
                action, fresh.observation, run.request.mode, run.cancelled))
            if not isinstance(result, ExecutionResult):
                raise ContractError("Invalid executor result")
            run.recovery = result.recovery
            self.emit(run, "action", asdict(result))
            if self.stopped(run):
                return
            if result.status != "ok":
                self.finish(run, "cancelled" if result.status == "cancelled" else "unresolved",
                            "Action did not complete successfully.")
                return
            verification_start = utcnow()
            checks = await self._tool(self.executor.verify(action, run.request.complaint))
            now = utcnow()
            if (not isinstance(checks, list) or len(checks) > 20
                    or any(not isinstance(c, Check) or not
                           verification_start <= timestamp(c.observed_at) <= now for c in checks)):
                raise ContractError("Verification evidence is not fresh")
            self.emit(run, "verification", {"checks": [asdict(c) for c in checks]})
            if not self.stopped(run):
                self.finish(run, verdict(checks), "Only the listed symptom checks were verified.")

    async def close(self):
        tasks = [r.task for r in self.runs.values() if r.task and not r.task.done()]
        for run in self.runs.values():
            self.cancel(run.id)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
