"""Think / Act / Verify coordination over injected hooks.

The coordinator owns reasoning only. Member 3's runtime supplies approval,
cancellation and events; Member 1's executor supplies fresh observations,
execution and postchecks. Every boundary re-validates: the model's choice is
schema-checked, arguments go through the executor's validator, the target is
re-observed before execution and the verdict comes from fresh checks.
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

from troubleshoot.contracts import ActionProposal, ContractError, Observation, parse_action, require_target
from troubleshoot.providers.base import ImageInput, ModelRequest, Provider, ProviderError

from .catalog import Catalog, ToolSpec
from .decision import Decision, DecisionError, decision_schema, parse_decision
from .prompts import SYSTEM, build_user_prompt, suspicious_text
from .verdict import EXECUTION_STATUSES, Check, Verdict, judge

STATUSES = ("diagnosed", "completed", "needs_user", "denied", "cancelled", "error", "budget_exhausted")
EVENT_TYPES = ("observation", "plan", "approval", "action", "verification", "complete", "error")


@dataclass(frozen=True)
class Budget:
    max_steps: int = 6              # model decisions per run
    max_mutations: int = 1          # approved system changes per run
    max_invalid: int = 2            # consecutive rejected decisions before giving up
    max_seconds: float = 300.0      # wall clock for the whole run
    step_timeout: float = 120.0     # one model request
    max_output_tokens: int = 400


@dataclass(frozen=True)
class FreshObservation:
    observation: Observation
    facts: dict
    image: ImageInput | None = None


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    evidence: dict = field(default_factory=dict)
    error: str | None = None

    def __post_init__(self):
        if self.status not in EXECUTION_STATUSES:
            raise ValueError("Unknown execution status")


class Hooks(Protocol):
    def observe(self) -> FreshObservation: ...
    def authorize(self, proposal: ActionProposal, tool: ToolSpec) -> bool: ...
    def execute(self, proposal: ActionProposal, fresh: FreshObservation) -> ExecutionResult: ...
    def postcheck(self, proposal: ActionProposal, result: ExecutionResult) -> list[Check]: ...
    def cancelled(self) -> bool: ...
    def emit(self, kind: str, payload: dict) -> None: ...


@dataclass
class Outcome:
    status: str
    message: str
    mode: str
    verdict: Verdict | None = None
    steps: list = field(default_factory=list)
    limitations: list = field(default_factory=list)
    untrusted_instructions: list = field(default_factory=list)
    metrics: list = field(default_factory=list)
    error: dict | None = None

    def to_dict(self) -> dict:
        data = dict(self.__dict__)
        data["verdict"] = None if self.verdict is None else self.verdict.to_dict()
        return data


class Coordinator:
    def __init__(self, provider: Provider, catalog: Catalog, budget: Budget = Budget(),
                 clock=time.monotonic, now=lambda: datetime.now(timezone.utc)):
        self.provider = provider
        self.catalog = catalog
        self.budget = budget
        self.clock = clock
        self.now = now

    def run(self, complaint: str, mode: str, hooks: Hooks, vision: bool = False) -> Outcome:
        if mode not in ("diagnose", "repair"):
            raise ContractError("Invalid mode")
        if not isinstance(complaint, str) or not complaint.strip():
            raise ContractError("Complaint is required")
        state = _RunState(self, complaint.strip(), mode, hooks, vision)
        outcome = state.loop()
        hooks.emit("complete", {"status": outcome.status, "message": outcome.message,
                                "verdict": None if outcome.verdict is None else outcome.verdict.to_dict()})
        return outcome


class _RunState:
    def __init__(self, owner: Coordinator, complaint, mode, hooks, vision):
        self.o, self.complaint, self.mode, self.hooks = owner, complaint, mode, hooks
        self.budget = owner.budget
        self.vision = vision
        self.history: list[dict] = []
        self.seen: set[str] = set()
        self.used: dict[str, list[dict]] = {}
        self.mutations = 0
        self.outcome = Outcome("error", "", mode)
        self.run_status: list[str] = []
        self.started = owner.clock()

    def emit(self, kind, payload):
        assert kind in EVENT_TYPES
        self.hooks.emit(kind, payload)

    def finish(self, status, message, error=None) -> Outcome:
        self.outcome.status, self.outcome.message, self.outcome.error = status, message, error
        if error:
            self.emit("error", error)
        return self.outcome

    def loop(self) -> Outcome:
        invalid = 0
        for step in range(1, self.budget.max_steps + 1):
            self.step = step
            if self.hooks.cancelled():
                return self.finish("cancelled", "Stopped by the user.")
            if self.o.clock() - self.started > self.budget.max_seconds:
                break
            fresh = self.hooks.observe()
            self._record_observation(fresh)
            try:
                reply = self.o.provider.decide(self._request(fresh, step))
            except ProviderError as exc:
                return self.finish("error", "The model could not be used; nothing was changed.", exc.to_dict())
            self.outcome.metrics.append(reply.metrics())
            if self.hooks.cancelled():
                return self.finish("cancelled", "Stopped by the user.")
            try:
                decision = self._accept(reply.data)
                if decision.next == "run_tool":
                    proposal, current = self._propose(decision, fresh)
            except ContractError as exc:
                invalid += 1
                self.history.append({"step": step, "rejected_decision": str(exc)})
                self.emit("error", {"code": "invalid_decision", "message": str(exc), "recoverable": True})
                if invalid > self.budget.max_invalid:
                    if self.outcome.verdict is not None:
                        return self._verified_summary()
                    return self.finish("error", "The model kept producing invalid decisions; nothing further was run.",
                                       {"code": "invalid_decision", "message": str(exc)})
                continue
            invalid = 0
            self.emit("plan", {"step": step, "decision": decision.to_dict(), "metrics": reply.metrics()})
            if decision.next == "conclude":
                return self._conclude(decision)
            if decision.next == "ask_user":
                return self.finish("needs_user", decision.message)
            done = self._act(step, decision, proposal)
            if done is not None:
                return done
        if self.outcome.verdict is not None:
            return self._verified_summary()
        return self.finish("budget_exhausted",
                           "Step or time budget reached before a conclusion.",
                           {"code": "budget_exhausted", "message": "Run stopped at its budget"})

    def _record_observation(self, fresh: FreshObservation):
        flagged = suspicious_text(fresh.facts)
        for snippet in flagged:
            if snippet not in self.outcome.untrusted_instructions:
                self.outcome.untrusted_instructions.append(snippet)
        self.emit("observation", {"observation_id": fresh.observation.observation_id,
                                  "observed_at": fresh.observation.observed_at,
                                  "image_ref": fresh.image.ref if fresh.image else None,
                                  "untrusted_instructions": flagged})

    @property
    def allow_mutation(self) -> bool:
        return self.mutations < self.budget.max_mutations

    @property
    def conclude_only(self) -> bool:
        return self.outcome.verdict is not None and self.outcome.verdict.verdict == "resolved"

    def _request(self, fresh: FreshObservation, step: int) -> ModelRequest:
        images = ()
        if self.vision and fresh.image is not None:
            images = (fresh.image,)
        last_step = step == self.budget.max_steps
        status = list(self.run_status)
        if self.used:
            done = "; ".join(f"{op} {json.dumps(args)}" for op, calls in self.used.items() for args in calls)
            status.append(f"Already ran (results in HISTORY, do not repeat): {done}")
        if last_step and not self.conclude_only:
            status.append("This is the last step: conclude with what the evidence shows.")
        prompt = build_user_prompt(self.complaint, self.mode, self.o.catalog, fresh.facts, self.history,
                                   self.budget.max_steps - step + 1, image_attached=bool(images),
                                   run_status=status, allow_mutation=self.allow_mutation)
        schema = decision_schema(self.o.catalog, self.mode, self.allow_mutation,
                                 self.conclude_only or last_step, self.used)
        return ModelRequest(SYSTEM, prompt, schema, images,
                            self.budget.max_output_tokens, self.budget.step_timeout)

    def _accept(self, data) -> Decision:
        decision = parse_decision(data, self.o.catalog, self.mode)
        if (self.conclude_only or self.step == self.budget.max_steps) and decision.next != "conclude":
            raise DecisionError("The change is verified; conclude and explain the result")
        if decision.next != "run_tool":
            return decision
        key = decision.operation + json.dumps(decision.arguments, sort_keys=True)
        if key in self.seen:
            raise DecisionError(f"Repeated {decision.operation} with the same arguments; use HISTORY")
        tool = self.o.catalog.get(decision.operation)
        if tool.mutates and self.mutations >= self.budget.max_mutations:
            raise DecisionError("Change budget used; conclude from the verification result")
        return decision

    def _verified_summary(self) -> Outcome:
        """The model failed to summarise after a verified change: report the checks themselves."""
        verdict = self.outcome.verdict
        passed = [c.name for c in verdict.checks if c.passed]
        failed = [c.name for c in verdict.checks if not c.passed]
        message = f"Change verified as {verdict.verdict}."
        if passed:
            message += " Passed: " + ", ".join(passed) + "."
        if failed:
            message += " Failed: " + ", ".join(failed) + "."
        self.outcome.limitations.append("The model did not write a final summary; this message was generated from the checks")
        return self.finish("completed", message)

    def _conclude(self, decision: Decision) -> Outcome:
        if self.outcome.verdict is not None:
            # The model writes the explanation; the checks decide the verdict.
            return self.finish("completed", decision.message)
        if self.mode == "repair":
            self.outcome.limitations.append("No change was made, so nothing was verified as fixed")
        return self.finish("diagnosed", decision.message)

    def _propose(self, decision: Decision, seen_by_model: FreshObservation) -> tuple[ActionProposal, FreshObservation]:
        """Model inference outlasts the freshness window, so bind the proposal to a
        new observation of the same target taken after the decision."""
        current = self.hooks.observe()
        if current.observation.target != seen_by_model.observation.target:
            raise ContractError("Target changed while the model was deciding")
        payload = {"action_id": uuid.uuid4().hex, "operation": decision.operation,
                   "arguments": decision.arguments,
                   "target": dict(current.observation.target.__dict__),
                   "observation_id": current.observation.observation_id}
        proposal = parse_action(payload, self.o.catalog.registry(self.mode))
        require_target(proposal, current.observation, self.o.now())
        return proposal, current

    def _act(self, step: int, decision: Decision, proposal: ActionProposal) -> Outcome | None:
        tool = self.o.catalog.get(decision.operation)
        self.seen.add(decision.operation + json.dumps(decision.arguments, sort_keys=True))
        self.used.setdefault(decision.operation, []).append(proposal.arguments)
        approved = self.hooks.authorize(proposal, tool)
        self.emit("approval", {"action_id": proposal.action_id, "operation": proposal.operation,
                               "mutates": tool.mutates, "approved": bool(approved)})
        if approved is not True:
            self.outcome.steps.append({"step": step, "operation": proposal.operation, "approved": False})
            return self.finish("denied", f"{proposal.operation} was not approved; nothing was changed.")
        if self.hooks.cancelled():
            return self.finish("cancelled", "Stopped by the user before the action ran.")
        current = self.hooks.observe()
        if current.observation.target != proposal.target:
            return self.finish("error", "The target changed after approval; the action was not run.",
                               {"code": "target_changed", "message": "Target identity changed"})
        result = self.hooks.execute(proposal, current)
        record = {"step": step, "operation": proposal.operation, "arguments": proposal.arguments,
                  "status": result.status, "evidence": result.evidence, "error": result.error}
        self.emit("action", {"action_id": proposal.action_id, **record})
        if tool.mutates:
            self.mutations += 1
            verdict = judge(result.status, self.hooks.postcheck(proposal, result))
            self.outcome.verdict = verdict
            self.outcome.limitations.extend(n for n in verdict.limitations if n not in self.outcome.limitations)
            record["verification"] = {"verdict": verdict.verdict, "checks": [
                f"{c.name}: expected {c.expected}, actual {c.actual}, {'PASS' if c.passed else 'FAIL'}"
                for c in verdict.checks]}
            record["expected_change"] = decision.expected_change
            self.run_status.append(f"Change made: {proposal.operation} {json.dumps(proposal.arguments)}. "
                                   f"Fresh checks verdict: {verdict.verdict.upper()}.")
            if verdict.verdict == "resolved":
                self.run_status.append("All symptom checks passed. Conclude now: tell the user what was done "
                                       "and what the checks showed.")
            else:
                limit = "" if self.allow_mutation else " No further changes are allowed."
                self.run_status.append("The symptom is NOT confirmed fixed." + limit +
                                       " Use read-only tools to explain why, or conclude honestly that it is not fixed.")
            self.emit("verification", {"action_id": proposal.action_id, **verdict.to_dict()})
        self.outcome.steps.append(record)
        self.history.append(record)
        if result.status == "cancelled":
            return self.finish("cancelled", "The action was cancelled.")
        return None
