"""What the model may choose from: registered tools with argument schemas.

Member 1's executor owns the real registry and validators. The agent only
exposes what that registry provides, filtered by mode, so a diagnose run never
even offers a mutating operation to the model.
"""

import json
from dataclasses import dataclass
from typing import Callable

from troubleshoot.contracts import ContractError

ArgumentValidator = Callable[[dict], dict]
MODES = ("diagnose", "repair")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    mutates: bool
    arguments: dict                # JSON schema for the arguments object
    validator: ArgumentValidator   # authoritative strict validator from the executor
    postcondition: str = ""        # what a fresh check should show after a change

    def __post_init__(self):
        if not self.name.isidentifier() or len(self.name) > 64:
            raise ContractError(f"Invalid tool name {self.name!r}")
        if self.arguments.get("type") != "object":
            raise ContractError(f"Tool {self.name} arguments schema must be an object")
        if self.mutates and not self.postcondition:
            raise ContractError(f"Mutating tool {self.name} needs a postcondition")


class Catalog:
    def __init__(self, tools):
        self._tools = {}
        for tool in tools:
            if tool.name in self._tools:
                raise ContractError(f"Duplicate tool {tool.name}")
            self._tools[tool.name] = tool
        if not self._tools:
            raise ContractError("Catalog is empty")

    def get(self, name: str) -> ToolSpec:
        return self._tools[name]

    def available(self, mode: str) -> list[ToolSpec]:
        if mode not in MODES:
            raise ContractError("Invalid mode")
        return [t for t in self._tools.values() if mode == "repair" or not t.mutates]

    def registry(self, mode: str) -> dict[str, ArgumentValidator]:
        """Mapping for contracts.parse_action, restricted to the mode."""
        return {t.name: t.validator for t in self.available(mode)}

    def describe(self, mode: str) -> str:
        lines = []
        for t in self.available(mode):
            kind = "CHANGES SYSTEM, needs approval" if t.mutates else "read-only"
            args = json.dumps(t.arguments.get("properties", {}), separators=(",", ":"))
            lines.append(f"- {t.name} ({kind}): {t.description} Arguments: {args}")
        return "\n".join(lines)
