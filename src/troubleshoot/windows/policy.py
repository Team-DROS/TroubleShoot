"""Executor-side consent boundary; API token storage belongs to Member 3."""

import hashlib
import json
from dataclasses import dataclass
from threading import Event
from typing import Callable

from troubleshoot.contracts import ContractError, text


@dataclass(frozen=True)
class AuthorizationRequest:
    run_id: str
    action_id: str
    operation: str
    fingerprint: str
    summary: str


@dataclass
class ExecutionContext:
    run_id: str
    action_id: str
    mode: str
    cancelled: Event
    consume_authorization: Callable[[AuthorizationRequest], bool] | None = None

    def require_mutation(self, operation: str, arguments: dict, observed_state: dict, summary: str):
        text(self.run_id, "run_id", 128)
        text(self.action_id, "action_id", 128)
        if self.mode != "repair":
            raise ContractError("Diagnose-only prohibits mutation")
        if self.cancelled.is_set():
            raise ContractError("Run cancelled")
        body = {"run_id": self.run_id, "action_id": self.action_id, "operation": operation,
                "arguments": arguments, "observed_state": observed_state}
        fingerprint = hashlib.sha256(json.dumps(body, sort_keys=True, allow_nan=False).encode()).hexdigest()
        request = AuthorizationRequest(self.run_id, self.action_id, operation, fingerprint, summary)
        if self.consume_authorization is None or self.consume_authorization(request) is not True:
            raise ContractError("Specific authorization required")
        if self.cancelled.is_set():
            raise ContractError("Run cancelled during approval")
        return request


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    evidence: dict
    changed: bool | None = False
    limitations: tuple[str, ...] = ()
