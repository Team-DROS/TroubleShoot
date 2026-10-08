"""Provider protocol shared by local and hosted Gemma adapters.

A provider turns a bounded request into one parsed JSON object. It never
executes anything: the agent validates the object against its decision schema
and the executor registry decides what is runnable. Errors are explicit; no
adapter may substitute another provider or canned text when it fails.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

ERROR_CODES = frozenset({
    "unavailable",    # runtime not reachable
    "model_missing",  # runtime reachable, configured model not installed
    "timeout",        # request exceeded its time budget
    "malformed",      # reply is not one JSON object / truncated / wrong envelope
    "too_large",      # request or reply exceeds a size bound
    "capability",     # e.g. images sent to a text-only model
    "configuration",  # invalid adapter settings
    "http",           # other runtime error response
    "cancelled",      # caller cancelled before the request was sent
})

MAX_IMAGE_BYTES = 4 * 1024 * 1024
IMAGE_TYPES = frozenset({"image/png", "image/jpeg"})


class ProviderError(RuntimeError):
    """A bounded, user-reportable provider failure."""

    def __init__(self, code: str, message: str):
        if code not in ERROR_CODES:
            raise ValueError(f"Unknown provider error code {code!r}")
        super().__init__(message)
        self.code = code

    def to_dict(self) -> dict:
        return {"code": self.code, "message": str(self)}


@dataclass(frozen=True)
class Capabilities:
    text: bool = True
    vision: bool = False
    structured_output: bool = False
    thinking: bool = False


@dataclass(frozen=True)
class ProviderStatus:
    """Configuration is not proof of inference: `reachable` and `model_present`
    come from live runtime queries, and `last_inference_ok` only from a reply."""

    provider: str
    model: str
    locality: str                  # "local" | "lan" | "hosted"
    configured: bool
    reachable: bool
    model_present: bool
    capabilities: Capabilities
    runtime_version: str | None = None
    detail: str | None = None
    last_inference_ok: bool | None = None

    def to_dict(self) -> dict:
        data = dict(self.__dict__)
        data["capabilities"] = dict(self.capabilities.__dict__)
        return data


@dataclass(frozen=True)
class ImageInput:
    """Consented selected-window capture. Bytes stay in memory; logs use `ref`."""

    ref: str
    media_type: str
    data: bytes = field(repr=False)

    def __post_init__(self):
        if not isinstance(self.ref, str) or not self.ref or len(self.ref) > 128:
            raise ValueError("Invalid image reference")
        if self.media_type not in IMAGE_TYPES:
            raise ValueError("Unsupported image type")
        if not isinstance(self.data, bytes) or not 0 < len(self.data) <= MAX_IMAGE_BYTES:
            raise ValueError("Image is empty or too large")


@dataclass(frozen=True)
class ModelRequest:
    system: str
    user: str
    schema: dict                      # JSON schema the reply must follow
    images: tuple[ImageInput, ...] = ()
    max_output_tokens: int = 512
    timeout_seconds: float = 90.0


@dataclass(frozen=True)
class ModelReply:
    data: dict                        # parsed JSON object, not yet agent-validated
    provider: str
    model: str
    latency_ms: int
    prompt_tokens: int | None = None
    output_tokens: int | None = None

    def metrics(self) -> dict:
        return {"provider": self.provider, "model": self.model, "latency_ms": self.latency_ms,
                "prompt_tokens": self.prompt_tokens, "output_tokens": self.output_tokens}


@runtime_checkable
class Provider(Protocol):
    name: str
    model: str

    def status(self) -> ProviderStatus:
        """Query the runtime; never raises for an unreachable runtime."""

    def decide(self, request: ModelRequest) -> ModelReply:
        """Return one JSON object or raise ProviderError."""


def parse_json_object(content: Any) -> dict:
    """Strictly parse model text into one JSON object.

    The only normalisation is removing one surrounding Markdown code fence,
    which some models add even under structured output. Anything else fails.
    """
    import json

    if not isinstance(content, str) or not content.strip():
        raise ProviderError("malformed", "Model returned empty content")
    text = content.strip()
    if text.startswith("```") and text.endswith("```") and text.count("```") == 2:
        text = text[3:-3]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError("malformed", "Model reply is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ProviderError("malformed", "Model reply is not a JSON object")
    return value
