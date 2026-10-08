"""The thinker's structured decision: one JSON schema for constrained decoding
and one strict validator that treats any deviation as a failure, never a command."""

from dataclasses import dataclass

from troubleshoot.contracts import ContractError

from .catalog import Catalog

NEXT_STEPS = ("run_tool", "conclude", "ask_user")
LIKELIHOOD = ("high", "medium", "low")
KEYS = {"assessment", "hypotheses", "next", "tool", "expected_change", "message"}
TOOL_KEYS = {"operation", "arguments", "reason"}
MAX_TEXT = 400
MAX_HYPOTHESES = 3


class DecisionError(ContractError):
    """Model output violated the decision schema or policy."""


@dataclass(frozen=True)
class Hypothesis:
    cause: str
    likelihood: str


@dataclass(frozen=True)
class Decision:
    assessment: str
    hypotheses: tuple[Hypothesis, ...]
    next: str
    operation: str | None
    arguments: dict | None
    reason: str | None
    expected_change: str | None
    message: str | None

    def to_dict(self) -> dict:
        return {
            "assessment": self.assessment,
            "hypotheses": [h.__dict__ for h in self.hypotheses],
            "next": self.next,
            "tool": None if self.operation is None else
            {"operation": self.operation, "arguments": self.arguments, "reason": self.reason},
            "expected_change": self.expected_change,
            "message": self.message,
        }


def _string(limit=MAX_TEXT):
    return {"type": "string", "maxLength": limit}


def _nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def _unused_arguments(arguments: dict, used: list[dict]) -> dict | None:
    """Narrow an argument schema so calls already made cannot be emitted again.

    Handles the two shapes small tool schemas use: no arguments (drop the tool
    once used) and one enum-valued argument (drop used values). Other shapes are
    left alone; repeated calls are still rejected by the coordinator.
    """
    if not used:
        return arguments
    props = arguments.get("properties", {})
    if not props:
        return None
    if len(props) == 1:
        (key, prop), = props.items()
        if isinstance(prop.get("enum"), list):
            remaining = [v for v in prop["enum"] if v not in {u.get(key) for u in used}]
            if not remaining:
                return None
            return {**arguments, "properties": {key: {**prop, "enum": remaining}}}
    return arguments


def decision_schema(catalog: Catalog, mode: str, allow_mutation: bool = True,
                    conclude_only: bool = False, used: dict[str, list[dict]] | None = None) -> dict:
    """JSON schema passed to the runtime for constrained decoding.

    Each available tool becomes its own branch, so the operation name and its
    argument shape are tied together and unknown operations cannot be emitted.
    Calls already made are pruned; after the change budget is used, mutating
    tools disappear; after a verified fix or on the last step only `conclude`
    remains.
    """
    used = used or {}
    tools = [] if conclude_only else [t for t in catalog.available(mode) if allow_mutation or not t.mutates]
    branches = []
    for tool in tools:
        arguments = _unused_arguments(tool.arguments, used.get(tool.name, []))
        if arguments is None:
            continue
        branches.append({
            "type": "object",
            "properties": {"operation": {"type": "string", "enum": [tool.name]},
                           "arguments": arguments, "reason": _string(160)},
            "required": ["operation", "arguments", "reason"],
            "additionalProperties": False,
        })
    conclude_only = conclude_only or not branches
    steps = ["conclude"] if conclude_only else list(NEXT_STEPS)
    if conclude_only:
        branches = []
    return {
        "type": "object",
        "properties": {
            "assessment": _string(300),
            "hypotheses": {"type": "array", "maxItems": MAX_HYPOTHESES, "items": {
                "type": "object",
                "properties": {"cause": _string(120), "likelihood": {"type": "string", "enum": list(LIKELIHOOD)}},
                "required": ["cause", "likelihood"], "additionalProperties": False}},
            "next": {"type": "string", "enum": steps},
            "tool": {"anyOf": [*branches, {"type": "null"}]},
            "expected_change": _nullable(_string(200)),
            "message": _nullable(_string()),
        },
        "required": sorted(KEYS),
        "additionalProperties": False,
    }


def _text(value, field, limit=MAX_TEXT, optional=False):
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise DecisionError(f"Invalid {field}")
    return value.strip()


def parse_decision(data, catalog: Catalog, mode: str) -> Decision:
    """Validate shape and internal consistency. Tool arguments are checked
    later by the executor's validator through contracts.parse_action."""
    if not isinstance(data, dict) or set(data) != KEYS:
        raise DecisionError("Decision has missing or unexpected fields")
    nxt = data["next"]
    if nxt not in NEXT_STEPS:
        raise DecisionError("Invalid next step")
    hyps = data["hypotheses"]
    if not isinstance(hyps, list) or len(hyps) > MAX_HYPOTHESES:
        raise DecisionError("Invalid hypotheses")
    parsed_hyps = []
    for h in hyps:
        if not isinstance(h, dict) or set(h) != {"cause", "likelihood"} or h["likelihood"] not in LIKELIHOOD:
            raise DecisionError("Invalid hypothesis")
        parsed_hyps.append(Hypothesis(_text(h["cause"], "hypothesis", 120), h["likelihood"]))
    expected = _text(data["expected_change"], "expected_change", 200, optional=True)
    message = _text(data["message"], "message", optional=True)
    tool = data["tool"]
    operation = arguments = reason = None
    if nxt == "run_tool":
        if not isinstance(tool, dict) or set(tool) != TOOL_KEYS:
            raise DecisionError("run_tool requires exactly operation, arguments and reason")
        operation = _text(tool["operation"], "operation", 64)
        if operation not in catalog.registry(mode):
            raise DecisionError(f"Operation {operation!r} is not available in {mode} mode")
        if not isinstance(tool["arguments"], dict):
            raise DecisionError("Tool arguments must be an object")
        arguments = tool["arguments"]
        reason = _text(tool["reason"], "reason", 160)
        if catalog.get(operation).mutates and expected is None:
            raise DecisionError("A system change must state the expected observable change")
    else:
        if tool is not None:
            raise DecisionError(f"{nxt} must not include a tool")
        if message is None:
            raise DecisionError(f"{nxt} requires a message")
    return Decision(_text(data["assessment"], "assessment", 300), tuple(parsed_hyps), nxt,
                    operation, arguments, reason, expected, message)
