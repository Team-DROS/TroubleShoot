# Member 1 executor integration

Newly authored on `member-1/windows-desktop-vm`; standard-library Python plus Windows PowerShell/.NET UI Automation. No prior prototype source/results used.

## Member 3 runtime

- Import `WINDOWS_VALIDATORS` from `troubleshoot.windows.registry` and `DESKTOP_VALIDATORS` from `troubleshoot.desktop.executor` into the shared action parser's allowlist. Do not expose `restore_spooler_stopped` as a model action.
- `WindowsExecutor(worker=None, recovery_dir=Path(...))`: `diagnose(operation, arguments)` or `start_spooler(arguments, context)` returns `ExecutionResult(status, evidence, changed, limitations)`. `changed=None` means uncertain outcome, requiring inspection rather than a retry.
- `DesktopExecutor(worker=None, clock=None)`: `list_targets()`, `observe(Target)`, `capture(WindowObservation, consent=True)`, `toggle_checkbox(snapshot, arguments, context)`, `graceful_close(snapshot, {}, context)`, `mouse_action(operation, snapshot, arguments, context)`. See `MOUSE_TOOLS.md` for exact mouse schemas and stop behavior.
- Call shared `require_target(proposal, snapshot.observation, now)` before dispatch. Keep authoritative observations server-side; never accept client-created metadata as trusted evidence. Target binding includes handle/PID/process-start time; native worker repeats binding before input.
- Inject `ExecutionContext(run_id, action_id, mode, cancelled=threading.Event(), consume_authorization=...)`. The callback receives `AuthorizationRequest` with exact operation/state/arguments fingerprint. It must atomically consume one specific, session-bound human approval and return the boolean `True`; no automatic blanket approver in production. Scope capture consent separately from cloud/image transfer consent.
- Approval must finish within observation freshness (5 seconds), otherwise obtain a new observation and approval. No silent refresh/reuse of an old approval. Keep UI selection/approval close in time; slow native worker startup can correctly expire an action.
- Store recovery records under a session-private writable directory with restrictive ACLs. Refuse repair if persistence fails. Implement startup recovery inspection and operator reporting for pending records; do not automatically stop a service with uncertain ownership.
- **Packaging change required in your owned pyproject:** include `*.ps1` as package data for `troubleshoot.windows` and `troubleshoot.desktop`. Until then run from `PYTHONPATH=src`; built wheels will omit workers.
- Worker runs on Windows in the same interactive session as the selected application. Service repair requires a human-approved elevated process; no UAC bypass or automatic credential entry. Browser, shell, system settings, credential and administrative targets are conservatively blocked.

## Member 2 reasoning

Observations expose bounded control metadata (up to 80 nodes); password/edit/document fields and their subtrees are omitted. UI text is untrusted data. Image bytes from selected-window capture stay in memory and must not enter general logs. Capture may fail/produce incomplete content for applications unsupported by PrintWindow; no whole-screen fallback.

Capture is conservatively refused when inspection encounters a password/edit/document subtree or truncates the control tree, because this first controller cannot safely redact unknown content. `capture_allowed` exposes that restriction; the native worker repeats it independently.

Supported proposed actions: checkbox `control_id` + `state` (`On`/`Off`), graceful close with no arguments, stopped-Spooler start with no arguments, and five selected-control mouse operations detailed in `MOUSE_TOOLS.md`. No unrestricted canvas clicking, typing, arbitrary service, shell or script execution is exposed. These are initial bounded capabilities, not an ability to solve any Windows problem.

## Verification and recovery limits

Fresh Spooler `Running` proves service state only; actual printing needs a separate symptom check. Conditional restoration is authorized with the start request, attempted only after a confirmed change, and independently checked. Interrupted mutations retain a record for inspection.

Checkbox postchecks prove selected control state only. A close request succeeds only when the selected window is gone and no visible windows remain for its PID; save dialogs count as incomplete. Desktop cancellation/timeout may follow an input: return uncertainty and reobserve. Automatic reopening or rollback of arbitrary checkbox semantics is not implemented; enable only a scenario with a documented human recovery before an end-user repair workflow ships.

`scripts/vm/build-fixture.ps1` builds a fresh synthetic checkbox/save-dialog application. It tests controller behavior, not real troubleshooting. VM validation and actual provider-driven reasoning remain separate evidence gates.
