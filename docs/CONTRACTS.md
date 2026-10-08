# Shared protocol v1 — Member 3 integration surface

Member 3's branch now includes a loopback API, session coordinator, hosted Gemma
transport and browser UI. The original foundation notes below describe the shared
starting point. This section supersedes their "next work" and "no endpoint" status.
Member 2's provider hook and Member 1's native executors are now merged and wired
through `runtime/native.py`. Their source files are unchanged. Native approval
uses the owner's exact state fingerprint; live combined guest validation remains
pending. The integration update below supersedes the original proposal notes.

## HTTP and authentication

Every `/api/` request requires `Authorization: Bearer <local-session-token>`.
The server accepts only its configured `127.0.0.1:port` Host and same-origin
browser Origin. CLI requests without Origin still require the token. No CORS
allowlist, cookie authentication, token query parameters or public bind is used.

| Method/path | Input/output |
|---|---|
| `GET /api/status` | Default provider, provider configuration/readiness/model/capabilities, executor and vision availability, simulation label |
| `GET /api/targets` | `{targets:[{label,target}],available}`; bounded to 50 entries |
| `POST /api/runs` | RunRequest fields plus optional `target`; returns 202 `{run_id,simulation}` |
| `GET /api/runs/{id}` | `{run_id,state,recovery,cancel_requested}` |
| `GET /api/runs/{id}/events` | SSE with event id/type/data; accepts `Last-Event-ID` cursor, ends after complete |
| `POST /api/runs/{id}/decision` | Exactly `{token,action_id,approve}`; approve is a boolean |
| `POST /api/runs/{id}/cancel` | Empty JSON object; cooperative stop request and current recovery |

JSON bodies are limited to 16 KiB. Unknown fields and missing consent fail with
400 `invalid_request`. Missing/invalid bearer token: 401. Wrong Origin/Host: 403.
Unknown run: 404. Invalid/expired/replayed approval: 409. Missing component or
capacity/recovery blocker: 503. Error responses contain safe codes, not exception
messages, API keys or upstream response bodies. There is no screenshot endpoint.

Example request (the hosted variant also needs `provider:"gemma_api"` and
`cloud_consent:true`):

```json
{"complaint":"The selected application is not responding","mode":"diagnose","provider":"ollama","vision_enabled":false,"cloud_consent":false,"cloud_images_consent":false,"target":null}
```

Example terminal SSE frame (illustrative values, not measured repair evidence):

```text
id: 3
event: complete
data: {"id":"3","type":"complete","timestamp":"2026-10-08T06:00:00+00:00","payload":{"verdict":"unresolved","recovery":"none","limitations":["Diagnosis only; no symptom postcondition was measured."],"simulation":true}}

```

## Provider hook to agree with Member 2

Integration update: startup imports `local_adapter_from_env` from
`agent/runtime_adapter.py`. Its hook matches the documented runtime shape.
`providers/base.py`, `providers/ollama.py`, and `agent/` are imported unchanged
from Member 2 `6ed184b`. Local decision timeout now defaults to 150 seconds.
Provider failures surface safe `local_<code>` errors and
never select hosted/fixture alternatives. The single-action runtime uses the
adapter, not the separate multi-step Coordinator.

`SessionManager(providers={"ollama": adapter, "gemma_api": adapter}, executor=...)`
injects components explicitly. No automatic import/fallback to missing providers.
Proposed adapter methods used by this branch:

```python
def status() -> dict:
    # configured: bool; readiness: unavailable|unverified|responding|fixture;
    # model: str|None; images: bool; optional structured_output description
    ...

async def decide(request: dict) -> dict:
    # request = {request: asdict(RunRequest), observation: asdict(Snapshot)|None,
    #            operations: {name: {mutates, expected, recovery}}}
    # output = {summary: str, action: None|ActionProposal.to_dict()}
    ...
```

Output is revalidated by the runtime using native operation argument validators.
Unknown operations, shell extras and malformed decisions fail closed. No model
verdict is accepted as verification. The hosted adapter additionally accepts an
optional `images` array directly through dependency injection; the API currently
blocks vision. Agree any conversion to Member 2's eventual protocol in an adapter
without editing that owner's files silently.

## Executor hook to agree with Member 1

Integration update: `runtime/native.py` routes the window/system scopes to the
unchanged owner executors, retaining authoritative metadata by observation ID.
`operations_for(target)` limits the offered registry to the selected scope.
`execute_authorized` supplies a threading cancellation event and bridges the
native `AuthorizationRequest` to an authenticated runtime approval event. That
event includes `native_fingerprint`, `summary`, and `freshness_seconds` in addition
to the generic approval fields. It replaces the generic gate for native actions,
so there is one exact human approval and no blanket native approver.

Read-only window inspection and Windows diagnostics are enabled by default.
The production launcher disables all desktop mutation until a real symptom
verifier exists; an environment flag cannot enable it. Programmatic checkbox
integration requires an injected verifier and uses the unchanged `CheckboxRecovery`
wrapper, durable private baseline and existing session execution lock. Startup
records block repairs; restoration requires a new approved owner context and is
not exposed as an API/model action. Mouse and close are not runtime operations.
`capture_target`
is not offered until a scoped consented capture pipeline exists;
`restore_spooler_stopped` is never in the model registry. Native recovery records
are scanned at startup and pending records block repairs. PowerShell workers are
included in the Python wheel.

Startup uses a persistent, serialized PowerShell transport in Member 3's runtime
paths. It invokes fixed unchanged Member 1 scripts through a cached runspace;
request payloads cannot provide code, script paths or new operations. Calls are
bounded to 20 seconds, and failures kill the process without replaying an action.
This removes repeated process/type startup, not the five-second freshness gate.
Actual Windows read-only reuse passed; guest execution timing remains pending.

`runtime/ports.py` provides `Operation(validate, mutates, expected, recovery)`
and `Snapshot(observation, facts)`. Native integration must supply:

```python
operations: dict[str, Operation]
async def targets() -> list[dict]: ...  # [{label, target: asdict(Target)}]
async def observe(target: Target) -> Snapshot: ...
async def execute(action: ActionProposal, observation: Observation,
                  mode: str, cancelled: asyncio.Event) -> ExecutionResult: ...
async def verify(action: ActionProposal, complaint: str) -> list[Check]: ...
```

Operations use trusted fixed argument validators and deterministic mutation
classification. Expected postcondition/recovery descriptions come from the
registry, not model text. Native adapters must separately check policy, target
identity, foreground/occlusion, coordinates, geometry/DPI, input freshness and
cancellation immediately before input, with bounded native calls. A timeout in
async Python alone cannot interrupt an independent native worker.

Observation adds optional bounds `(left,top,right,bottom)` and positive DPI.
The runtime compares new identity/geometry/DPI before execution. Coordinate
validators and native foreground checks remain Member 1's responsibility.
No UI screenshot/control metadata pipeline is implemented yet.

## Approval, execution and verification

One proposed action is allowed per run. Mutations require repair mode and a
single-use random token bound to run, action, arguments, target and observation.
The runtime snapshots the action and checks a canonical digest before execution.
Rejection/cancellation never starts the action. Target changes or evidence older
than five seconds reject the action, even if the 60-second approval token has not
expired. The UI must start a new run for a refreshed observation/proposal.

The initial pre-inference observation may be older than five seconds when Gemma
responds. The model proposal must match its initial identity/observation ID; the
runtime then re-observes and compares identity/bounds/DPI, binds to the new ID,
and emits the new observation before approval. This implements Member 2's patch.
It does not relax the post-approval freshness rule. The UI states that limit and
native tokens expire within the remaining observation freshness interval.

`ExecutionResult.status`: `ok|blocked|failed|cancelled`.
`ExecutionResult.recovery`: `none|pending|restored|failed`.
Mutation starts with pending recovery; exceptions/timeouts preserve that state.
Pending/failed recovery blocks later mutations. The native bridge also checks
durable records after restart and verifies a machine marker before mutation.
No operator recovery endpoint is implemented; pending records need human
inspection. Do not use process restart or a different path to bypass recovery.

`Check(name,expected,actual,passed,observed_at)` is created by a deterministic
verifier after execution. Its timestamp must be within the new verification
interval. No checks/all failed means unresolved; mixed checks mean partial;
all passed means resolved **only for the listed symptom checks**. A successful
execution result alone cannot mean resolved. Completion payloads contain verdict,
recovery, limitations and simulation. Error/cancellation are distinct verdicts.

See `docs/MEMBER_3_SETUP.md` for budgets and limits, and
`docs/MEMBER_3_VALIDATION.md` for actual validation evidence.

## Original shared foundation notes (historical starting point)

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
