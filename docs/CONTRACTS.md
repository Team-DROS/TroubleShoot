# Shared protocol v1 — first implementation

Implemented module: `src/troubleshoot/contracts.py`. This is a validation foundation; it provides no model client, Windows executor, API server, UI or repair behavior.

- Member 3 owns shared contracts/API/session consent and hosted transport; `RunRequest` is the initial request policy. `parse_action(payload, registry)` requires executor argument validators and rejects unregistered operations/extra proposal fields.
- Member 1 owns the registry of operation names to strict validators and the Windows/desktop executor. Each validator returns a validated object or raises `ContractError`. Execution rechecks approval/mode/geometry/foreground/identity/freshness independently; parsing is not authorization.
- Member 2 owns provider protocol, local Ollama transport and agent decisions. Consume these schemas and propose additions to Member 3 rather than making competing shapes.
- Member 3 also owns the minimal UI. Synthetic events have `id`, `type`, `timestamp`, `payload`; types are observation/plan/approval/action/verification/complete/error. No endpoint is live yet.

`Target` identity is handle/PID/process start timestamp. `Observation` binds it to an ID and timezone-aware capture time; default permitted age is five seconds. `require_target` checks identity, observation ID and age. Geometry/DPI/control metadata, authenticated image references, approval tokens, budgets and verdict schemas are next work, not implemented protection.

Windows executors must obtain process creation time consistently. Identity/freshness checks here do not eliminate a race between validation and native input; the executor revalidates as close as possible to execution and reports uncertainty.

Synthetic fixture is in `docs/fixtures/inspect_target.json`. It is not a live window/action, inference response or successful repair. Its timestamp is fixed for display/tests; runtime freshness checks will reject it now.

Run fresh contract tests without installing packages:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests/unit -v
```

These checks validate trust boundaries in the contracts, not model performance or Windows behavior. Member 3 supplies follow-up API schemas/samples, Member 2 supplies provider protocol, and Member 1 supplies executor hooks before runtime integration.
