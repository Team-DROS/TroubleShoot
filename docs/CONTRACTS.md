# Shared protocol v1 — first implementation

Implemented module: `src/troubleshoot/contracts.py`. This is a validation foundation; it provides no model client, Windows executor, API server, UI or repair behavior.

- Member 1: use `RunRequest` for normalized provider/consent policy. `parse_action(payload, registry)` requires the concrete executor registry's argument validator and rejects unregistered operations and extra proposal fields.
- Member 2: export a registry mapping operation names to strict argument validators. Each validator returns a validated argument object or raises `ContractError`. Windows execution must independently enforce approval, mode, geometry/foreground, target identity and freshness immediately before acting; parsing is not authorization.
- Member 3: use the synthetic fixture below to develop observation/action presentation. Events have `id`, `type`, `timestamp` and `payload`. No endpoint is live yet; field `type` uses observation/plan/approval/action/verification/complete/error.

`Target` identity is handle/PID/process start timestamp. `Observation` binds it to an ID and timezone-aware capture time; default permitted age is five seconds. `require_target` checks identity, observation ID and age. Geometry/DPI/control metadata, authenticated image references, approval tokens, budgets and verdict schemas are next work, not implemented protection.

Windows executors must obtain process creation time consistently. Identity/freshness checks here do not eliminate a race between validation and native input; the executor revalidates as close as possible to execution and reports uncertainty.

Synthetic fixture is in `docs/fixtures/inspect_target.json`. It is not a live window/action, inference response or successful repair. Its timestamp is fixed for display/tests; runtime freshness checks will reject it now.

Run fresh contract tests without installing packages:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests/unit -v
```

These checks validate trust boundaries in the contracts, not model performance or Windows behavior. Person 1 supplies follow-up typed schemas and API samples before Members 2/3 wire their components.
