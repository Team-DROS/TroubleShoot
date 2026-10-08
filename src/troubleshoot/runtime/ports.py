"""Proposed DI hooks for Member 1/2 review, not their provider protocol implementation.

All hooks are asynchronous and must honor cancellation/deadlines. Native adapters
must independently revalidate identity, geometry, foreground and policy at input.
"""

from dataclasses import dataclass, field
from typing import Any

from troubleshoot.contracts import ArgumentValidator, Observation


@dataclass(frozen=True)
class Operation:
    validate: ArgumentValidator
    mutates: bool
    expected: str
    recovery: str


@dataclass(frozen=True)
class Snapshot:
    observation: Observation
    facts: dict[str, Any] = field(default_factory=dict)


class RuntimeFailure(Exception):
    """Only predefined safe codes cross the API boundary."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
