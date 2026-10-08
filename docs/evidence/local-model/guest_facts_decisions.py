"""REAL gemma4:e2b decisions on facts from Member 1's RECORDED guest evidence. Nothing is executed."""
import asyncio, json, subprocess, sys
from dataclasses import asdict
from datetime import datetime, timezone
from troubleshoot.agent.runtime_adapter import LocalGemmaAdapter
from troubleshoot.contracts import Observation, Target
from troubleshoot.providers.ollama import OllamaProvider

desktop, service = (json.load(open(p)) for p in sys.argv[1:3])
os_facts = desktop["os"]
ops = {n: {"mutates": m, "expected": e, "recovery": "see Member 1 registry"} for n, m, e in [
    ("system_snapshot", False, "System facts are read"), ("network_snapshot", False, "Network facts are read"),
    ("spooler_status", False, "Spooler state is read"),
    ("start_spooler", True, "Spooler is Running; actual printing still needs a separate check")]}
cases = [
    ("printer_guest_fault", "repair", "Documents are stuck and nothing prints.",
     {"os": os_facts, "spooler": {"name": "Spooler", "status": service["fault_status"]}},
     {"spooler_status", "start_spooler"}),
    ("slow_guest_diagnose", "diagnose", "This PC feels slow and is running out of space.",
     {"os": os_facts}, {"system_snapshot"}),
    ("printer_guest_diagnose", "diagnose", "Documents are stuck and nothing prints.",
     {"os": os_facts, "spooler": {"name": "Spooler", "status": service["fault_status"]}}, {"spooler_status"}),
]
adapter = LocalGemmaAdapter(OllamaProvider())
results = []
for name, mode, complaint, facts, expected in cases:
    obs = Observation("guest-facts", datetime.now(timezone.utc).isoformat(), Target(1, 2, os_facts["observed_at"]))
    payload = {"request": {"complaint": complaint, "mode": mode, "provider": "ollama", "vision_enabled": False,
                           "cloud_consent": False, "cloud_images_consent": False},
               "observation": {"observation": asdict(obs), "facts": facts}, "operations": ops}
    out = asyncio.run(adapter.decide(payload))
    op = out["action"]["operation"] if out["action"] else None
    results.append({"case": name, "mode": mode, "complaint": complaint, "chosen_operation": op,
                    "acceptable": sorted(expected), "passed": op in expected,
                    "summary": out["summary"], "metrics": adapter.last_metrics})
    print(json.dumps({k: results[-1][k] for k in ("case", "chosen_operation", "passed")}), flush=True)
rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
report = {"kind": "local-gemma-guest-facts",
          "label": "REAL local inference on facts copied from Member 1's RECORDED Windows guest evidence "
                   "(desktop-2026-10-08.json source_commit f4d5838, service-2026-10-08.json source_matching_commit 6ad86df). "
                   "Decisions only; nothing was executed and this is not a live guest run.",
          "recorded_at": datetime.now(timezone.utc).isoformat(), "revision": rev,
          "provider": adapter.status(), "passed": sum(r["passed"] for r in results), "total": len(results),
          "results": results}
path = f"docs/evidence/local-model/local-gemma-guest-facts-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
open(path, "w").write(json.dumps(report, indent=2) + "\n")
print(report["passed"], "/", report["total"], "->", path)
