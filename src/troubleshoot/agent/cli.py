"""Local Gemma checks for developers.

  python -m troubleshoot.agent.cli status
  python -m troubleshoot.agent.cli smoke  [--record DIR]
  python -m troubleshoot.agent.cli eval   [--only NAME] [--record DIR]

`smoke` and `eval` use REAL inference against SIMULATED tools/facts. Exit code
is non-zero when the model is unreachable or a scenario fails.
"""

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from troubleshoot.providers.base import ProviderError
from troubleshoot.providers.ollama import DEFAULT_MODEL, DEFAULT_URL, OllamaProvider

from .coordinator import Budget, Coordinator
from .simulation import SCENARIOS, SimulatedHooks, build_machine, simulated_catalog


def _revision() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def run_scenario(provider, scenario, budget: Budget) -> dict:
    hooks = SimulatedHooks(build_machine(scenario))
    started = time.monotonic()
    outcome = Coordinator(provider, simulated_catalog(), budget).run(scenario.complaint, scenario.mode, hooks)
    verdict = outcome.verdict.verdict if outcome.verdict else None
    failures = []
    if outcome.status not in scenario.expect_status:
        failures.append(f"status {outcome.status} not in {scenario.expect_status}")
    if verdict not in scenario.expect_verdict:
        failures.append(f"verdict {verdict} not in {scenario.expect_verdict}")
    for op in scenario.forbid_ops:
        if op in hooks.executed:
            failures.append(f"forbidden {op} executed")
    for op in scenario.require_ops:
        if op not in hooks.executed:
            failures.append(f"expected {op} was not executed")
    plans = [p for k, p in hooks.events if k == "plan"]
    rejected = [p for k, p in hooks.events if k == "error" and p.get("recoverable")]
    return {
        "scenario": scenario.name, "mode": scenario.mode, "passed": not failures, "failures": failures,
        "status": outcome.status, "verdict": verdict, "message": outcome.message,
        "executed": hooks.executed, "valid_decisions": len(plans), "rejected_decisions": len(rejected),
        "untrusted_instructions_flagged": len(outcome.untrusted_instructions),
        "seconds": round(time.monotonic() - started, 1),
        "latency_ms": [m["latency_ms"] for m in outcome.metrics],
        "output_tokens": [m["output_tokens"] for m in outcome.metrics],
        "decisions": [p["decision"] for p in plans],
        "error": outcome.error,
    }


def _record(directory: str, name: str, payload: dict) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = path / f"{name}-{stamp}.json"
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="troubleshoot.agent.cli")
    parser.add_argument("command", choices=["status", "smoke", "eval"])
    parser.add_argument("--model", default=None, help=f"Ollama tag (default {DEFAULT_MODEL} or env)")
    parser.add_argument("--url", default=None, help=f"Ollama URL (default {DEFAULT_URL} or env)")
    parser.add_argument("--only", default=None, help="Run one named scenario")
    parser.add_argument("--record", default=None, help="Write sanitized JSON evidence to this directory")
    parser.add_argument("--step-timeout", type=float, default=Budget.step_timeout)
    args = parser.parse_args(argv)

    provider = OllamaProvider.from_env()
    if args.model or args.url:
        provider = OllamaProvider(args.model or provider.model, args.url or provider.base_url,
                                  allow_non_loopback=provider.locality != "local")
    status = provider.status()
    print(json.dumps(status.to_dict(), indent=2))
    if args.command == "status":
        return 0 if status.reachable and status.model_present else 1
    if not (status.reachable and status.model_present):
        print("Model not available; no simulated substitute will be used.", file=sys.stderr)
        return 1

    budget = Budget(step_timeout=args.step_timeout, max_seconds=max(300.0, args.step_timeout * 6))
    chosen = [s for s in SCENARIOS if args.command == "eval" and (args.only in (None, s.name))]
    if args.command == "smoke":
        chosen = [SCENARIOS[0]]
    if not chosen:
        print(f"No scenario named {args.only}", file=sys.stderr)
        return 2
    results = []
    for scenario in chosen:
        try:
            result = run_scenario(provider, scenario, budget)
        except ProviderError as exc:
            result = {"scenario": scenario.name, "passed": False, "error": exc.to_dict()}
        results.append(result)
        print(json.dumps({k: result.get(k) for k in
                          ("scenario", "passed", "status", "verdict", "executed", "failures", "seconds")}))
    report = {
        "kind": "local-gemma-" + args.command,
        "label": "REAL local inference; SIMULATED tools and machine facts (not Windows evidence)",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "revision": _revision(),
        "host": {"system": platform.system(), "machine": platform.machine(), "python": platform.python_version()},
        "provider": status.to_dict(),
        "settings": {"temperature": provider.temperature, "seed": provider.seed, "num_ctx": provider.context_tokens,
                     "think": provider.think, "budget": budget.__dict__},
        "passed": sum(r["passed"] for r in results), "total": len(results),
        "results": results,
    }
    print(f"{report['passed']}/{report['total']} scenarios passed")
    if args.record:
        print(f"Evidence written to {_record(args.record, report['kind'], report)}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
