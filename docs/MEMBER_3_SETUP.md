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

Local Gemma is the UI/API default. The launcher now uses Member 2's unchanged
`local_adapter_from_env()`; it queries the configured Ollama runtime and reports
unavailable if the runtime/model is absent. Neither provider substitutes fixtures
or silently falls back. Optional hosted Gemma is still separate and consented.

## Local Gemma and native Windows integration

The integrated source comes from Member 2 revision `6ed184b` and Member 1 revision
`3edf350`, merged with their history intact. The startup configuration is:

```env
TROUBLESHOOT_OLLAMA_URL=http://127.0.0.1:11434
TROUBLESHOOT_OLLAMA_MODEL=gemma4:e2b
TROUBLESHOOT_OLLAMA_ALLOW_LAN=0
TROUBLESHOOT_OLLAMA_TIMEOUT=150
TROUBLESHOOT_DESKTOP_REPAIRS=0
```

Use the already-installed model on a teammate's machine; startup does not download
one. See [Member 2 setup and measured results](LOCAL_GEMMA.md). Configuration is
separate from proof of inference. Local provider status queries run outside the
event loop so they cannot freeze approval/cancellation processing.

On Windows the launcher attaches `NativeExecutorAdapter`, which wraps Member 1's
unchanged `WindowsExecutor` and `DesktopExecutor`. Select **This computer (system
diagnostics)** for OS/network/Spooler operations, or a permitted window for
inspection. The computer entry is explicitly a logical backend-session scope,
not a window handle. Native window identity and metadata remain server-side.

After inference the runtime obtains fresh evidence and compares identity, bounds
and DPI with the initial observation before rebinding the action. A changed target
fails closed. **After human approval, old evidence is not silently refreshed**.
Approval must finish within the bound observation's five-second freshness window.
The UI shows the remaining window; native startup/checks may shorten it. If it
expires, start a new run. This follows Member 1's current native approval policy.

Native mutations request their exact `AuthorizationRequest` fingerprint from the
UI at the executor's authorization boundary. Tokens are single-use and bound to
run/action/arguments/target/observation; the native fingerprint identifies the
specific observed state. There is no automatic native approver. The native worker
independently checks freshness and identity immediately before input.

Stopped-Spooler start is registered; `restore_spooler_stopped` is never available
to the model. Service mutation needs a human-elevated process; the application
does not bypass UAC. Do not stop the host service to test a repair: fault/repair
validation belongs in a disposable guest with recovery.

Recovery files default to `data/recovery` relative to the launch directory. Set
`TROUBLESHOOT_RECOVERY_DIR` to a stable private path for an installed deployment.
The bridge restricts Windows directory ACLs and checks its machine marker before
mutation; Member 1's executor refuses service changes if persistence fails.
Pending JSON records are reported in `/api/status` and block new repairs at
startup. They require operator inspection; there is no automatic startup restore
or API to dismiss/delete records. Keep this path stable across restarts.

The launcher keeps desktop changes disabled even if `TROUBLESHOOT_DESKTOP_REPAIRS=1`.
No real application symptom verifier is integrated. Programmatic injection of an
explicit symptom verifier can expose only `toggle_checkbox`, wrapped in Member 1's
`CheckboxRecovery`; its durable baseline remains a blocker until separately
approved restoration/operator inspection. There is no recovery API yet. Mouse
and close primitives are merged but not exposed by this production runtime.
Screenshot
capture/model image transfer remains unavailable in the API/UI; no unconsented
`capture_target` is offered to a model.

The bridge verifies fresh native service/control/diagnostic facts and includes a
failing original-symptom check until a real symptom verifier is supplied. Thus
Spooler Running alone can produce **partial**, never a claim of restored printing.

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
.\.venv\Scripts\python tests/e2e/console/serve_fixture.py
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

Install `requirements.lock` first. The wheel includes the operator console as
package data under `troubleshoot/api/console`, and includes `windows/diagnostics.ps1`,
`desktop/worker.ps1`, `desktop/mouse-native.ps1`, and the Member 3 persistent
transport as package data. Source and installed execution are supported.
The dependency lock is an exact version resolution, not a hash-verified lock.

## Integration limits

- One action per run; four concurrent runs, at most 100 retained runs. Completed
  runs without pending/failed recovery are evicted oldest first. Recovery blockers
  are retained. Events and approvals are process-local memory.
- Production overall run budget: 300 seconds. Local adapter inference limit:
  150 seconds by default, configurable with `TROUBLESHOOT_OLLAMA_TIMEOUT` (5–600).
  Longer model limits can still hit the overall run budget.
  Hosted transport: 25-second network timeout. The production launcher gives
  observation/verification calls 45 seconds; native workers have their own bounded
  20-second calls. A serialized persistent PowerShell process invokes unchanged
  owner scripts and caches native types between observations/actions. Errors and
  timeouts discard the process with no automatic retry. It is closed on shutdown.
  Recovery ACL preparation occurs before starting a repair run, outside the
  freshness window. Guest latency still requires measurement; slow/changed
  observations continue to fail closed. Approval expires after at most 60 seconds, but the observed
  target must still satisfy the existing **five-second** freshness policy.
  Slow approvals therefore fail closed and require a new run. Refresh/reproposal
  UX is pending; do not weaken freshness to make a demo pass.
- Stop cancels the inference wait and prevents later actions. A synchronous local
  HTTP call may continue until its own timeout. Native actions receive a bridged
  threading cancellation event; the adapter drains their bounded worker before
  releasing the execution lock. Cancellation is not evidence of restoration.
- Recovery is reported and pending/failed recovery blocks further mutations.
  Native service recovery and durable blockers are integrated; a recovery endpoint
  and generic desktop rollback remain unavailable.
- Real Gemma plus native checkbox input/verification/restoration passed Member 1's
  guest developer harness using a synthetic UI. Combined authenticated API/UI
  guest execution remains pending. Live vision returned unknown and blocked input;
  print verification is blocked because no printer is installed. No model/VM is
  required to run tests.
- This is a local single-user integration build, not a hardened multi-user server.
  The bearer token grants access to all runs in this one process. There is no
  remote deployment, publication or event submission in this work.

See `docs/CONTRACTS.md` for endpoint samples and proposed Member 1/2 hooks.
