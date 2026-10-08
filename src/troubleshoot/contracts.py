"""Provider-independent wire contracts; this module executes no Windows actions."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Callable, Mapping


class ContractError(ValueError):
    """An input violates the shared protocol."""


def text(value: Any, field: str, maximum: int = 2000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ContractError(f"Invalid {field}")
    return value


def fields(payload: Any, expected: set[str]) -> dict:
    if not isinstance(payload, dict) or set(payload) != expected:
        raise ContractError("Missing or unexpected fields")
    return payload


def positive_integer(value: Any, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise ContractError(f"Invalid {field}")
    return value


def timestamp(value: Any) -> datetime:
    text(value, "timestamp", 64)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("Invalid timestamp") from exc
    if parsed.utcoffset() is None:
        raise ContractError("Timestamp must include timezone")
    return parsed


@dataclass(frozen=True)
class RunRequest:
    complaint: str
    mode: str = "diagnose"
    provider: str = "ollama"
    vision_enabled: bool = False
    cloud_consent: bool = False
    cloud_images_consent: bool = False

    def __post_init__(self):
        text(self.complaint, "complaint")
        if self.mode not in {"diagnose", "repair"}:
            raise ContractError("Invalid mode")
        if self.provider not in {"ollama", "gemma_api"}:
            raise ContractError("Invalid provider")
        for value in (self.vision_enabled, self.cloud_consent, self.cloud_images_consent):
            if type(value) is not bool:
                raise ContractError("Consent and vision fields must be boolean")
        if self.provider == "gemma_api" and not self.cloud_consent:
            raise ContractError("Hosted inference requires cloud consent")
        if self.provider == "gemma_api" and self.vision_enabled and not self.cloud_images_consent:
            raise ContractError("Hosted images require image consent")


@dataclass(frozen=True)
class Target:
    handle: int
    pid: int
    started: str

    def __post_init__(self):
        positive_integer(self.handle, "handle")
        positive_integer(self.pid, "pid")
        timestamp(self.started)

    @classmethod
    def from_dict(cls, payload: Any):
        return cls(**fields(payload, {"handle", "pid", "started"}))


@dataclass(frozen=True)
class Observation:
    observation_id: str
    observed_at: str
    target: Target

    def __post_init__(self):
        text(self.observation_id, "observation_id", 128)
        timestamp(self.observed_at)
        if not isinstance(self.target, Target):
            raise ContractError("Invalid observation target")

    def require_fresh(self, now: datetime, max_age_seconds: float = 5):
        if (now.utcoffset() is None or type(max_age_seconds) not in (int, float)
                or not isfinite(max_age_seconds) or max_age_seconds <= 0):
            raise ContractError("Invalid freshness policy")
        age = (now - timestamp(self.observed_at)).total_seconds()
        if age < 0 or age > max_age_seconds:
            raise ContractError("Observation is stale or from the future")


@dataclass(frozen=True)
class ActionProposal:
    action_id: str
    operation: str
    arguments: dict
    target: Target
    observation_id: str

    def to_dict(self) -> dict:
        return asdict(self)


ArgumentValidator = Callable[[dict], dict]


def parse_action(payload: Any, registry: Mapping[str, ArgumentValidator]) -> ActionProposal:
    """Reject unknown operations and require the executor's argument validator."""
    fields(payload, {"action_id", "operation", "arguments", "target", "observation_id"})
    operation = text(payload["operation"], "operation", 64)
    if operation not in registry:
        raise ContractError("Unregistered operation")
    if not isinstance(payload["arguments"], dict):
        raise ContractError("Arguments must be an object")
    validated = registry[operation](dict(payload["arguments"]))
    if not isinstance(validated, dict):
        raise ContractError("Argument validator must return an object")
    return ActionProposal(
        text(payload["action_id"], "action_id", 128), operation, validated,
        Target.from_dict(payload["target"]),
        text(payload["observation_id"], "observation_id", 128),
    )


def require_target(action: ActionProposal, observation: Observation, now: datetime):
    observation.require_fresh(now)
    if action.target != observation.target or action.observation_id != observation.observation_id:
        raise ContractError("Action does not match observed target")


def event(event_id: str, kind: str, payload: dict) -> dict:
    text(event_id, "event_id", 128)
    if kind not in {"observation", "plan", "approval", "action", "verification", "complete", "error"}:
        raise ContractError("Invalid event type")
    if not isinstance(payload, dict):
        raise ContractError("Event payload must be an object")
    return {"id": event_id, "type": kind,
            "timestamp": datetime.now(timezone.utc).isoformat(), "payload": payload}
