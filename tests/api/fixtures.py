"""Explicit synthetic fixtures. No host changes and no model inference."""

import asyncio
from dataclasses import asdict
from datetime import datetime, timezone

from troubleshoot.contracts import Check, ExecutionResult, Observation, Target, fields
from troubleshoot.runtime.ports import Operation, Snapshot


def now():
    return datetime.now(timezone.utc).isoformat()


class FixtureProvider:
    def __init__(self, *, action=True, delay=0, error=False):
        self.action, self.delay, self.error = action, delay, error
        self.calls = 0

    def status(self):
        return {"configured": True, "readiness": "fixture", "model": "SYNTHETIC", "images": False}

    async def decide(self, request):
        self.calls += 1
        await asyncio.sleep(self.delay)
        if self.error:
            raise ValueError("secret that must not be disclosed")
        observation = request["observation"]
        return {"summary": "SYNTHETIC test proposal; no real troubleshooting.",
                "action": {"action_id": "fixture-action", "operation": "fixture_toggle",
                           "arguments": {}, "target": observation["observation"]["target"],
                           "observation_id": observation["observation"]["observation_id"]}
                    if self.action else None}


class FixtureExecutor:
    operations = {"fixture_toggle": Operation(lambda args: fields(args, set()), True,
                   "Synthetic symptom flag is clear", "Reset synthetic flag")}

    def __init__(self):
        self.target = Target(1, 2, now())
        self.executions = 0
        self.observations = 0
        self.changed = False
        self.error = False
        self.recovery = "none"
        self.result_status = "ok"
        self.passes = [True]
        self.delay = 0
        self.started = asyncio.Event()

    async def targets(self):
        return [{"label": "SYNTHETIC target", "target": asdict(self.target)}]

    async def observe(self, target):
        self.observations += 1
        bounds = (0, 0, 200 if self.changed and self.observations > 1 else 100, 100)
        return Snapshot(Observation("fixture-observation", now(), self.target, bounds, 96),
                        {"synthetic": True})

    async def execute(self, action, observation, mode, cancelled):
        self.executions += 1
        self.started.set()
        await asyncio.sleep(self.delay)
        if self.error:
            raise ValueError("private executor detail")
        return ExecutionResult(self.result_status, self.recovery)

    async def verify(self, action, complaint):
        return [Check(f"synthetic-{i}", "clear", "clear" if passed else "fault",
                      passed, now()) for i, passed in enumerate(self.passes)]
