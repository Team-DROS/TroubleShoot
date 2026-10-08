"""Explicit native read-only smoke; provider decision is SYNTHETIC, never inference.

No fault injection, UI input or service mutation. Prints only checks/statuses,
not raw system facts or window titles. Run with PYTHONPATH=src.
"""

import asyncio
import json

from troubleshoot.agent.runtime_adapter import local_adapter_from_env
from troubleshoot.contracts import RunRequest
from troubleshoot.runtime.native import native_executor_from_env
from troubleshoot.runtime.session import SessionManager


class SyntheticReadOnlyProvider:
    def status(self):
        return {"configured": True, "readiness": "fixture", "model": "SYNTHETIC", "images": False}

    async def decide(self, payload):
        observation = payload["observation"]["observation"]
        return {"summary": "SYNTHETIC decision for an actual read-only native service check",
                "action": {"action_id": "readonly-smoke", "operation": "spooler_status", "arguments": {},
                           "target": observation["target"], "observation_id": observation["observation_id"]}}


async def main():
    status = await asyncio.to_thread(local_adapter_from_env().status)
    print(json.dumps({"local_model_readiness": status["readiness"], "model": status["model"]}))
    executor = native_executor_from_env()
    if executor is None:
        raise SystemExit("Windows native smoke unavailable on this platform")
    manager = SessionManager({"ollama": SyntheticReadOnlyProvider()}, executor,
                             simulation=True, tool_seconds=45)
    try:
        run = manager.create(RunRequest("Read-only native service evidence", mode="diagnose"), executor.system_target)
        await run.task
        print(json.dumps({"label": "REAL native read-only workers; SYNTHETIC provider; no mutation",
            "events": [e["type"] for e in run.events],
            "errors": [e["payload"]["code"] for e in run.events if e["type"] == "error"],
            "complete": run.events[-1]["payload"]}))
        if any(e["type"] == "error" for e in run.events):
            raise SystemExit(1)
    finally:
        await manager.close()


if __name__ == '__main__':
    asyncio.run(main())
