# Member 3 backend and browser setup

Implemented on `member-3/backend-hosted-api`, 8 October 2026. This is fresh
implementation from the current requirements. No earlier prototype source,
prompts, tests or dependency files were used.

## Run from this checkout (Windows PowerShell)

Prerequisites: Git, Python 3.11+ and Node.js for the optional UI tests. Verified
here with Python 3.14.3 and Node.js 24.18.0. The UI itself has no npm dependencies
or build step. The fresh backend dependency resolution is in `requirements.lock`.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.lock
.\scripts\start.ps1
```

Open `http://127.0.0.1:8765`. Paste the **local session token** printed by the
launcher into the UI. That token is distinct from a hosted API key. It stays in
tab memory, is sent in an Authorization header, and is not stored in localStorage
or URLs. Restarting generates a new token unless explicitly configured.

The supported launcher binds only `127.0.0.1`; do not run it behind a public
proxy or with multiple workers. Use the literal address, not `localhost`, because
the API validates the exact Host/Origin and port. A custom port can be supplied
with `scripts/start.ps1 -Port 8767`.

No provider is assumed available. Local Gemma is the UI/API default, but Member
2's adapter is not present in this branch and no local inference is attempted.
The hosted adapter reports unavailable until a key is configured. Neither path
silently substitutes fixtures or falls back to another provider.

## Optional hosted Gemma

Export `GEMMA_API_KEY` privately in the backend environment before starting. Do
not paste it into the UI or commit it. `.env.example` contains placeholders;
dotenv files are **not automatically loaded**. `GEMMA_API_MODEL` optionally
selects `gemma-4-26b-a4b-it` (default) or `gemma-4-31b-it`.

Select Hosted Gemma and explicitly check text-sharing consent for the run.
Configured means only that key/model settings exist. Readiness becomes responding
only after a valid response; it is not a continuous health check. This environment
had no configured key, so account access, quota and real inference remain untested.

Official reference checked 8 October 2026:
[Run Gemma with the Gemini API](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api).
The adapter uses that service's REST endpoint and keeps the key in an HTTP header.
It uses bounded JSON text output with validation; it does not assume guaranteed
schema-constrained generation. There is no retry, model substitution or fallback.

The hosted transport accepts one bounded PNG/JPEG only with separate image and
vision consent. Transport tests are synthetic. The API/UI currently reject vision
because selected-window capture and scoped image storage have not been integrated.

## Checks without keys, models or a VM

```powershell
.\scripts\test.ps1
```

This runs the original and new contract/hosted tests, API/runtime tests, then five
Node UI behavior tests. The latter use a synthetic DOM/transport, not a real browser.
FastAPI's TestClient currently emits a non-failing Starlette/httpx deprecation
warning with this resolution; dependency compatibility checks pass.

For an explicit manual browser fixture:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
.\.venv\Scripts\python tests/e2e/web/serve_fixture.py
```

Open port 8766 and use the printed test token. Connect, select the SYNTHETIC
target, enter a synthetic complaint and start diagnosis. The UI must identify
the fixture and end **unresolved**, because no symptom was repaired or verified.
The production launcher never imports these fixtures. Ctrl+C stops either server.

## Packaging

```powershell
.\.venv\Scripts\python -m pip wheel --no-deps . --wheel-dir .venv/wheels
.\.venv\Scripts\python -m pip install --no-deps .venv/wheels/troubleshoot_agent-0.1.0-py3-none-any.whl
.\.venv\Scripts\troubleshoot.exe
```

Install `requirements.lock` first. The wheel includes browser assets under
`share/troubleshoot/web`. Source execution and installed execution are supported.
The dependency lock is an exact version resolution, not a hash-verified lock.

## Integration limits

- One action per run; four concurrent runs, at most 100 retained runs. Completed
  runs without pending/failed recovery are evicted oldest first. Recovery blockers
  are retained. Events and approvals are process-local memory.
- Overall run budget: 90 seconds. Hosted transport: 25-second network timeout.
  Tool calls: 10 seconds. Approval expires after 60 seconds, but the observed
  target must still satisfy the existing **five-second** freshness policy.
  Slow approvals therefore fail closed and require a new run. Refresh/reproposal
  UX is pending; do not weaken freshness to make a demo pass.
- Stop cancels inference and prevents subsequent actions. A running tool receives
  a cooperative cancellation event; cancellation is not evidence of restoration.
  Async timeouts cannot stop a non-cooperative native thread/process. Native
  adapters must independently bound work, revalidate input and honor cancellation.
- Recovery is reported and pending/failed recovery blocks further mutations.
  No native recovery implementation, persistent recovery journal or recovery
  endpoint exists yet. Do not attach a mutating production executor until those
  machine-specific recovery requirements are implemented with Member 1.
- No selected-window images, real native tools, UAC handling or local-model
  coordinator are bundled. The current launcher supports hosted **text diagnosis**
  when configured, and reports unresolved without deterministic postchecks.
- This is a local single-user integration build, not a hardened multi-user server.
  The bearer token grants access to all runs in this one process. There is no
  remote deployment, publication or event submission in this work.

See `docs/CONTRACTS.md` for endpoint samples and proposed Member 1/2 hooks.
