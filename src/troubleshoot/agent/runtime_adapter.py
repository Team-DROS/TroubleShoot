"""Adapter from Member 3's session runtime provider hook to local Gemma.

Member 3's SessionManager calls `status() -> dict` and
`await decide({request, observation, operations}) -> {summary, action}` and
then re-validates the action with the native validators itself. This adapter
keeps Member 2's guarantees on the model side: constrained decoding over the
operations the runtime offers (filtered by mode), untrusted-evidence prompts and
strict decision parsing. It makes one decision per call, matching that
runtime's single-action runs; it never executes anything.
"""

import asyncio
import time
import uuid

from troubleshoot.providers.base import ModelRequest, Provider

from .catalog import Catalog, ToolSpec
from .decision import decision_schema, parse_decision
from .prompts import SYSTEM, build_user_prompt

EMPTY_ARGUMENTS = {"type": "object", "properties": {}, "additionalProperties": False}

# Argument schemas and plain descriptions for Member 1's registered operations
# (member-1/windows-desktop-vm). Validators stay with Member 1; these only shape
# what the model may emit. An operation missing here is offered with no arguments,
# so a wrong guess fails closed in the runtime validator.
MEMBER1_OPERATIONS = {
    "system_snapshot": ("Read OS version, uptime, CPU, memory and system drive space.", EMPTY_ARGUMENTS),
    "network_snapshot": ("Read adapter, IP, gateway and DNS configuration and reachability.", EMPTY_ARGUMENTS),
    "spooler_status": ("Read the Print Spooler service state and start type.", EMPTY_ARGUMENTS),
    "start_spooler": ("Start the Print Spooler service when it is confirmed stopped.", EMPTY_ARGUMENTS),
    "inspect_target": ("Read the selected window's title, process and visible controls.", EMPTY_ARGUMENTS),
    "capture_target": ("Capture an image of the selected window (needs capture consent).", EMPTY_ARGUMENTS),
    "toggle_checkbox": ("Set one checkbox in the selected window, by control_id from the observation, to On or Off.", {
        "type": "object",
        "properties": {"control_id": {"type": "string", "maxLength": 256},
                       "state": {"type": "string", "enum": ["On", "Off"]}},
        "required": ["control_id", "state"], "additionalProperties": False}),
    "graceful_close": ("Ask the selected window to close normally (unsaved work prompts are not answered).",
                       EMPTY_ARGUMENTS),
}


def _mouse_schema(*extra: str) -> dict:
    coordinate = {"type": "integer", "minimum": 0, "maximum": 32767}
    properties = {"control_id": {"type": "string", "maxLength": 256}, "x": coordinate, "y": coordinate}
    for name in extra:
        properties[name] = ({"type": "integer", "minimum": -5, "maximum": 5} if name == "ticks" else coordinate)
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


_POINT = ("x and y are pixels from the selected window's top-left corner and must fall inside the bounds of "
          "control_id from the observation.")
MEMBER1_OPERATIONS.update({
    "mouse_move": ("Move the pointer over one observed control. " + _POINT, _mouse_schema()),
    "mouse_click": ("Click one observed button, checkbox, radio button, list item or tab. " + _POINT, _mouse_schema()),
    "mouse_double_click": ("Double-click one observed button or list item. " + _POINT, _mouse_schema()),
    "mouse_scroll": ("Scroll one observed list by ticks (-5 to 5, not 0). " + _POINT, _mouse_schema("ticks")),
    "mouse_drag": ("Drag one observed slider from x,y to to_x,to_y (different points). " + _POINT,
                   _mouse_schema("to_x", "to_y")),
})

SINGLE_ACTION_NOTE = ("This run allows at most one action. Choose the single most useful action for the "
                      "complaint, or conclude if no listed tool fits.")
NO_TARGET_NOTE = "No window or system target is selected, so no tool can run. Conclude from the complaint."


def _passthrough(arguments: dict) -> dict:
    # The runtime applies the authoritative native validator after this adapter.
    return dict(arguments)


class LocalGemmaAdapter:
    """Implements Member 3's proposed provider hook on top of a Member 2 Provider."""

    def __init__(self, provider: Provider, operations: dict | None = None, *,
                 max_output_tokens: int = 400, timeout_seconds: float = 150.0, status_ttl: float = 5.0):
        # 150 s covers a cold model load plus one CPU decision and still fits
        # inside Member 3's default 180 s run budget.
        self.provider = provider
        self.operations = dict(MEMBER1_OPERATIONS if operations is None else operations)
        self.max_output_tokens = max_output_tokens
        self.timeout_seconds = timeout_seconds
        self.status_ttl = status_ttl
        self._status_cache: tuple[float, dict] | None = None
        self.last_metrics: dict | None = None

    # status

    def status(self) -> dict:
        now = time.monotonic()
        if self._status_cache and now - self._status_cache[0] < self.status_ttl:
            return dict(self._status_cache[1])
        live = self.provider.status()
        if not (live.reachable and live.model_present):
            readiness = "unavailable"
        elif live.last_inference_ok:
            readiness = "responding"
        else:
            readiness = "unverified"
        result = {"configured": live.configured, "readiness": readiness, "model": live.model,
                  "images": live.capabilities.vision, "locality": live.locality,
                  "structured_output": "json-schema constrained decoding" if live.capabilities.structured_output
                  else None, "detail": live.detail}
        self._status_cache = (now, result)
        return dict(result)

    # decision

    def catalog(self, offered: dict) -> Catalog:
        tools = []
        for name, info in offered.items():
            description, arguments = self.operations.get(name, (info.get("expected") or name, EMPTY_ARGUMENTS))
            mutates = info.get("mutates") is True
            tools.append(ToolSpec(name, description, mutates, arguments, _passthrough,
                                  info.get("expected") or "The expected postcondition is met"))
        return Catalog(tools)

    def build(self, payload: dict) -> tuple[ModelRequest, Catalog | None, dict | None]:
        request = payload["request"]
        mode = request["mode"]
        snapshot = payload.get("observation")
        offered = payload.get("operations") or {}
        if offered:
            catalog = self.catalog(offered)
        else:
            catalog = None
        usable = catalog is not None and snapshot is not None and bool(catalog.available(mode))
        facts = {} if snapshot is None else dict(snapshot.get("facts") or {})
        notes = [SINGLE_ACTION_NOTE if usable else NO_TARGET_NOTE]
        # Catalog needs at least one tool even when only `conclude` is allowed.
        prompt_catalog = catalog if usable else Catalog([ToolSpec("none", "No tool available.", False,
                                                                  EMPTY_ARGUMENTS, _passthrough)])
        prompt = build_user_prompt(request["complaint"], mode, prompt_catalog, facts, [], 1, run_status=notes)
        schema = decision_schema(prompt_catalog, mode, conclude_only=not usable)
        return (ModelRequest(SYSTEM, prompt, schema, (), self.max_output_tokens, self.timeout_seconds),
                prompt_catalog, snapshot)

    async def decide(self, payload: dict) -> dict:
        model_request, catalog, snapshot = self.build(payload)
        reply = await asyncio.to_thread(self.provider.decide, model_request)
        self.last_metrics = reply.metrics()
        decision = parse_decision(reply.data, catalog, payload["request"]["mode"])
        if decision.next != "run_tool":
            return {"summary": decision.message, "action": None}
        observation = snapshot["observation"]
        summary = decision.assessment
        if decision.expected_change:
            summary += f" Expected change: {decision.expected_change}"
        return {"summary": summary[:2000], "action": {
            "action_id": uuid.uuid4().hex,
            "operation": decision.operation,
            "arguments": decision.arguments,
            "target": dict(observation["target"]),
            "observation_id": observation["observation_id"],
        }}


def local_adapter_from_env() -> LocalGemmaAdapter:
    """Convenience for Member 3's startup: `providers={"ollama": local_adapter_from_env()}`."""
    import os

    from troubleshoot.providers.ollama import OllamaProvider
    timeout = float(os.environ.get("TROUBLESHOOT_OLLAMA_TIMEOUT", "150"))
    if not 5 <= timeout <= 600:
        raise ValueError("TROUBLESHOOT_OLLAMA_TIMEOUT must be 5 to 600 seconds")
    return LocalGemmaAdapter(OllamaProvider.from_env(), timeout_seconds=timeout)
