"""REAL gemma4:e2b through Member 3's SessionManager; SIMULATED spooler executor."""
import asyncio, json, sys, time
from dataclasses import asdict
from datetime import datetime, timezone
from troubleshoot.contracts import Check, ExecutionResult, Observation, RunRequest, Target, fields
from troubleshoot.runtime.ports import Operation, Snapshot
from troubleshoot.runtime.session import SessionManager
from troubleshoot.agent.runtime_adapter import LocalGemmaAdapter
from troubleshoot.providers.ollama import OllamaProvider

now = lambda: datetime.now(timezone.utc).isoformat()
empty = lambda a: fields(a, set())

class SimSpooler:
    operations = {
        "spooler_status": Operation(empty, False, "Spooler state is read", "none"),
        "start_spooler": Operation(empty, True, "Spooler is Running and queued jobs drain", "Stop Spooler again"),
    }
    def __init__(self): self.state, self.jobs, self.target = "Stopped", 3, Target(10, 20, now())
    async def targets(self): return [{"label": "SIMULATED system", "target": asdict(self.target)}]
    async def observe(self, target):
        return Snapshot(Observation(f"obs-{time.monotonic_ns()}", now(), self.target),
                        {"simulated": True, "spooler": self.state, "print_queue_jobs": self.jobs})
    async def execute(self, action, observation, mode, cancelled):
        if action.operation == "start_spooler": self.state, self.jobs = "Running", 0
        return ExecutionResult("ok", "pending" if action.operation == "start_spooler" else "none")
    async def verify(self, action, complaint):
        return [Check("print queue drains", "0 jobs", f"{self.jobs} jobs", self.jobs == 0, now())]

async def main(mode):
    adapter = LocalGemmaAdapter(OllamaProvider())
    manager = SessionManager({"ollama": adapter}, SimSpooler(), simulation=True, run_seconds=170)
    print("status:", json.dumps(manager.status()["providers"]["ollama"]))
    run = manager.create(RunRequest("My printer stopped working, documents sit in the queue.", mode),
                         target=manager.executor.target)
    seen = 0
    while run.state != "complete":
        await asyncio.sleep(0.2)
        for ev in run.events[seen:]:
            seen += 1
            p = ev["payload"]
            print(ev["type"], json.dumps(p)[:300])
            if ev["type"] == "approval":
                print("  -> approving after", round(time.monotonic() - t0, 1), "s")
                manager.decide(run.id, p["token"], p["action"]["action_id"], True)
    for ev in run.events[seen:]: print(ev["type"], json.dumps(ev["payload"])[:300])
    print("metrics:", adapter.last_metrics)

t0 = time.monotonic()
asyncio.run(main(sys.argv[1]))
