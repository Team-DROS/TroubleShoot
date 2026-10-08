"""Local Gemma through the Ollama HTTP API, using only the standard library.

Defaults to loopback. A non-loopback runtime (for example the host seen from a
VirtualBox guest) must be enabled explicitly and is reported as "lan", never as
local. There is no hosted fallback: every failure raises ProviderError.
"""

import base64
import ipaddress
import json
import os
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from .base import Capabilities, ModelReply, ModelRequest, ProviderError, ProviderStatus, parse_json_object

DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "gemma4:e2b"
MAX_REPLY_BYTES = 2 * 1024 * 1024
MAX_PROMPT_CHARS = 48_000
STATUS_TIMEOUT = 5.0


def _is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_URL, *,
                 allow_non_loopback: bool = False, temperature: float = 0.0, seed: int | None = 7,
                 context_tokens: int = 8192, keep_alive: str = "10m", think: bool = False):
        parts = urlsplit(base_url)
        if parts.scheme not in {"http", "https"} or not parts.hostname or parts.path not in {"", "/"}:
            raise ProviderError("configuration", "Ollama URL must be http(s)://host:port")
        if not isinstance(model, str) or not model.strip() or len(model) > 128:
            raise ProviderError("configuration", "Invalid model tag")
        self.locality = "local" if _is_loopback(parts.hostname) else "lan"
        if self.locality != "local" and not allow_non_loopback:
            raise ProviderError("configuration", "Non-loopback Ollama URL needs explicit opt-in")
        self.model = model.strip()
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.seed = seed
        self.context_tokens = context_tokens
        self.keep_alive = keep_alive
        self.think = think
        self._capabilities: Capabilities | None = None
        self._last_ok: bool | None = None

    @classmethod
    def from_env(cls, environ=os.environ) -> "OllamaProvider":
        return cls(
            model=environ.get("TROUBLESHOOT_OLLAMA_MODEL", DEFAULT_MODEL),
            base_url=environ.get("TROUBLESHOOT_OLLAMA_URL", DEFAULT_URL),
            allow_non_loopback=environ.get("TROUBLESHOOT_OLLAMA_ALLOW_LAN") == "1",
        )

    # transport

    def _call(self, method: str, path: str, payload: dict | None, timeout: float) -> dict:
        body = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(self.base_url + path, data=body, method=method,
                                         headers={"Content-Type": "application/json"})
        # A proxy must never silently carry local prompts/images off the machine.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(request, timeout=timeout) as response:
                raw = response.read(MAX_REPLY_BYTES + 1)
        except urllib.error.HTTPError as exc:
            detail = self._error_text(exc)
            if exc.code == 404 and "not found" in detail.lower():
                raise ProviderError("model_missing", f"Model {self.model} is not installed: {detail}") from None
            raise ProviderError("http", f"Ollama HTTP {exc.code}: {detail}") from None
        except (TimeoutError, socket.timeout) as exc:
            raise ProviderError("timeout", f"Ollama did not answer within {timeout:g}s") from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise ProviderError("timeout", f"Ollama did not answer within {timeout:g}s") from exc
            raise ProviderError("unavailable", f"Ollama is not reachable at {self.base_url}") from exc
        except (ConnectionError, OSError) as exc:
            raise ProviderError("unavailable", f"Ollama connection failed: {exc.__class__.__name__}") from exc
        if len(raw) > MAX_REPLY_BYTES:
            raise ProviderError("too_large", "Ollama reply exceeded the size bound")
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProviderError("malformed", "Ollama returned a non-JSON envelope") from exc
        if not isinstance(data, dict):
            raise ProviderError("malformed", "Ollama envelope is not an object")
        return data

    @staticmethod
    def _error_text(exc: urllib.error.HTTPError) -> str:
        try:
            data = json.loads(exc.read(4096))
            return str(data.get("error", ""))[:300]
        except Exception:
            return exc.reason if isinstance(exc.reason, str) else ""

    # capability discovery

    def capabilities(self) -> Capabilities:
        if self._capabilities is None:
            info = self._call("POST", "/api/show", {"model": self.model}, STATUS_TIMEOUT)
            declared = info.get("capabilities")
            if not isinstance(declared, list):
                # Older runtimes do not report capabilities: assume text only.
                declared = ["completion"]
            self._capabilities = Capabilities(
                text="completion" in declared,
                vision="vision" in declared,
                structured_output=True,
                thinking="thinking" in declared,
            )
        return self._capabilities

    def _installed(self) -> list[str]:
        tags = self._call("GET", "/api/tags", None, STATUS_TIMEOUT).get("models", [])
        return [m.get("name", "") for m in tags if isinstance(m, dict)]

    def _model_present(self, names: list[str]) -> bool:
        wanted = self.model if ":" in self.model else self.model + ":latest"
        return wanted in names

    def status(self) -> ProviderStatus:
        common = dict(provider=self.name, model=self.model, locality=self.locality, configured=True,
                      last_inference_ok=self._last_ok)
        try:
            version = self._call("GET", "/api/version", None, STATUS_TIMEOUT).get("version")
        except ProviderError as exc:
            return ProviderStatus(**common, reachable=False, model_present=False,
                                  capabilities=Capabilities(text=False), detail=str(exc))
        try:
            present = self._model_present(self._installed())
            caps = self.capabilities() if present else Capabilities(text=False)
            detail = None if present else f"Model {self.model} is not installed"
        except ProviderError as exc:
            present, caps, detail = False, Capabilities(text=False), str(exc)
        return ProviderStatus(**common, reachable=True, model_present=present, capabilities=caps,
                              runtime_version=version, detail=detail)

    # inference

    def decide(self, request: ModelRequest) -> ModelReply:
        if len(request.system) + len(request.user) > MAX_PROMPT_CHARS:
            raise ProviderError("too_large", "Prompt exceeds the local context budget")
        if not 0 < request.max_output_tokens <= 4096 or not 0 < request.timeout_seconds <= 600:
            raise ProviderError("configuration", "Invalid output or time budget")
        caps = self.capabilities()
        if request.images and not caps.vision:
            raise ProviderError("capability", f"{self.model} does not declare image input support")
        user = {"role": "user", "content": request.user}
        if request.images:
            user["images"] = [base64.b64encode(image.data).decode("ascii") for image in request.images]
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": request.system}, user],
            "stream": False,
            "format": request.schema,
            "keep_alive": self.keep_alive,
            "options": {"temperature": self.temperature, "num_predict": request.max_output_tokens,
                        "num_ctx": self.context_tokens},
        }
        if self.seed is not None:
            payload["options"]["seed"] = self.seed
        if caps.thinking:
            # Only sent to models that declare thinking; others reject the field.
            payload["think"] = self.think
        started = time.monotonic()
        try:
            data = self._call("POST", "/api/chat", payload, request.timeout_seconds)
            reply = self._reply(data, started)
        except ProviderError:
            self._last_ok = False
            raise
        self._last_ok = True
        return reply

    def _reply(self, data: dict, started: float) -> ModelReply:
        if data.get("error"):
            raise ProviderError("http", str(data["error"])[:300])
        if data.get("done") is not True:
            raise ProviderError("malformed", "Ollama reply is incomplete")
        if data.get("done_reason") == "length":
            raise ProviderError("malformed", "Model output hit the token limit before finishing")
        message = data.get("message")
        if not isinstance(message, dict):
            raise ProviderError("malformed", "Ollama reply has no message")
        parsed = parse_json_object(message.get("content"))
        count = lambda key: data[key] if type(data.get(key)) is int else None
        return ModelReply(parsed, self.name, str(data.get("model") or self.model),
                          int((time.monotonic() - started) * 1000),
                          count("prompt_eval_count"), count("eval_count"))
