# Fresh project validation

## Member 1 assistance check — 8 October 2026, 13:28 IST

Prepared on the assisting teammate's PC by Umasuthan Palaniappan with Codex, not
represented as new work performed on Member 1's guest. Source under test:
`213db932948c293e097c0e1bc66562560bd24ddc`, based on Member 1 `3edf350`.
Host OS reports Windows NT `10.0.26300.0`; Python `3.14`.
The 16:15 IST team target remains unchanged.

| Check | Actual result |
|---|---|
| Guest/snapshot access | Blocked: VirtualBox 7.2.20 lists no registered VMs, running VMs or hard disks on this PC. Its machine registry is empty. The earlier named `TROUBLESHOOT-Test` and snapshot `fresh-tools-preflight-20261008` cannot be inspected or restored here. |
| Local model readiness | Member 2 CLI at `6ed184b45f2ad45aafa30769f523d043a311f335` reports reachable Ollama 0.40.1, installed `gemma4:e2b`, vision and structured-output capability. This status query is not a new inference result. |
| Original private capture | Unavailable in this workspace. Original PNG dimensions/byte size cannot be verified and no real-image rerun occurred. Previous unknown/none vision failure remains the latest guest-image result. |
| Helper correction | Target prompt now names `Enable demonstration feature`, asks for its visible state without supplying that state, checks PNG signature/header, byte size strictly below 4 MiB and dimensions up to 1280 px per side. Provider uses Member 2 environment configuration and records its actual checkout revision. Offline replay is no longer labelled a fresh live capture. |
| Local checks | Existing 73 unit tests pass; modified helper compiles; Git whitespace check passes. These checks do not establish image interpretation quality. |
| Full API guest validation | Not run. Remote Member 3 remains `769e895`; latest Member 1 mouse/recovery work and Member 2 mouse-schema/150-second timeout work are absent. Guest access, human approval/UAC and snapshot restoration are also prerequisites. |

**Chosen scenario:** the synthetic checkbox application, explicitly a controller
demo. Before-state must be independently observed Off, approved action sets On,
and fresh fixture state must confirm On; restore Off and close cooperatively.
These are intended assertions, not new observed before/after facts. This scenario
does not require elevation; record UAC as not applicable instead of manufacturing
an elevation prompt. If testing an actual privileged service action later, a human
must handle guest UAC. No Microsoft Print to PDF installation was attempted.
Earlier Spooler Running evidence continues to prove only service state.

The suggested `vision_reads_stopped_spooler` CLI scenario expects a Services
image named `services_spooler_stopped.png` and simulated service actions. It is
not an appropriate assertion for the failed checkbox screenshot. Use the corrected
Member 1 helper with Member 2's provider code for that specific capture:

```powershell
$env:PYTHONPATH = '<Member 2 checkout>\src'
$env:TROUBLESHOOT_OLLAMA_URL = 'http://127.0.0.1:11434'
python '<Member 1 checkout>\scripts\vm\decide-gemma-desktop.py' '<private capture JSON>' '<private report JSON>' '<private proposal JSON>'
```

Keep all three paths outside Git and use a new, private proposal output path for
each attempt. A helper failure must prevent any downstream execution. Inspect the
sanitized report before committing it; never commit PNG/base64 or the input capture.
If width exceeds the limit, resize the guest window and recapture. The original
capture must be visually checked for the intended control before interpreting a
model result. Naming the label is a plausible prompt improvement, not a proven
root cause or successful fix.

Once Member 3 integrates the owner branches, run `python -m troubleshoot.api`
inside the guest with `TROUBLESHOOT_OLLAMA_URL=http://10.0.2.2:11434` and
`TROUBLESHOOT_OLLAMA_ALLOW_LAN=1`. Confirm guest reachability separately: the host
loopback status check above does not prove the NAT address works. Run healthy
diagnosis, approved controller action, rejected approval and cancellation. Restore
the clean snapshot between fault scenarios and record restore success, exact merged
revision, guest OS, model, times and independently measured before/after states.
All four full-app cases remain pending. No host fault was injected.

Member 4 handoff text is in `docs/evidence/windows/MEMBER_4_HANDOFF.md`. There is
no identified Member 4 messaging destination in this workspace; this is a prepared
handoff, not a claim that a direct message was delivered.

8 October 2026, Asia/Calcutta. Newly authored implementation and tests; no old prototype code or validation imported.

- 46 unit tests pass: the original 16 shared-boundary tests plus 30 new Windows/desktop tests covering diagnosis-only, denial/cancellation, approval binding/delay, recovery persistence, uncertain mutation, human elevation, exact arguments, shell-free transport, malformed results, reused targets, stale/future observations, moved/DPI/foreground changes, changed controls and failed postconditions.
- Python compilation, all fresh PowerShell parser checks, WPF fixture compilation and Git whitespace checks pass. Run from checkout with `PYTHONPATH=src`, `python -m unittest discover -s tests/unit -v`. Packaging still needs Member 3 to include both native `.ps1` workers.
- Live host check was read-only system diagnosis. Intentional faults/input were confined to the guest.

## Fresh guest results

Desktop source revision `f4d5838`, 8 October 2026 at 06:33:55 UTC / 12:03:55 IST, Windows 11 Enterprise LTSC Evaluation 10.0.26100; provider/model **none**. All 11 native checks passed: healthy Spooler diagnosis, denied capture, stale capture, reused identity, selected checkbox toggle, selected-window PNG capture, secret-field capture refusal, removal of the synthetic secret field, save-dialog partial outcome, foreground-loss refusal and fixture cooperative recovery.

Fresh fixture state started checkbox Off; the native action set On and independently read On. Capture produced a 9824-byte PNG in memory; no image was retained in published evidence. Graceful close left two fixture windows, so it correctly reported incomplete; the fixture's explicit cleanup mechanism then exited it. These verify controller mechanics, not a real application symptom or Gemma image reasoning. Python approval/cancellation gates were unit tested separately, not claimed as a full guest API flow.

Service worker/harness contents subsequently committed in `6ad86df`, at 06:30:14–06:30:15 UTC / 12:00:14–12:00:15 IST. Powered-off preflight snapshot was available. User approved Windows UAC manually; the fixed elevated guest harness observed baseline Running, injected Stopped, invoked the fresh `start_spooler` operation, freshly checked Running, and checked baseline restoration. Actual print verification is **false**. No host service or adapter was changed.

Sanitized JSON reports are under `docs/evidence/windows/`. No credentials, private screenshots, prior demo footage or model results are included. Snapshot creation was verified; snapshot restore itself was not exercised.

## Remaining integration gates

The native tools run, but no runnable project API/UI, hosted adapter or local-model reasoning loop exists in this branch. Actual Gemma planning/image interpretation, runtime approval tokens, session authorization, packaging and crash-recovery startup inspection need Members 2/3 integration. Desktop actions do not implement automatic semantic rollback or reopening; each shipped repair scenario still needs symptom verification and recovery. Generic click/type navigation is not implemented.

Tests reuse installed Python/.NET/PowerShell and the VM infrastructure without model/VM duplication. Guest Python was unavailable; native tests were run in its actual interactive Windows session. Slow guest PowerShell startup means the 5-second observation gate may reject a future process-per-action integration; measure it and design a persistent bounded worker rather than relaxing freshness silently.

Member 1 owns this report and appends actual guest/native evidence, with local-model evidence from Member 2 and API/hosted/UI evidence from Member 3 with revision/time, OS/model/provider, scenario, before facts, approval/action, fresh postchecks, recovery and limitations.

## Bounded mouse tools: 8 October 2026

Source revision `2fa7187`, native report at 07:25:55 UTC / 12:55:55 IST: all 22 fresh synthetic guest checks passed. Move, single/double left click, bounded list scroll and slider drag changed independently observed fixture state. Checks also cover secret/occluded targets, Escape, held modifiers, concurrent input, cancellation between clicks, out-of-client points, stale/replaced targets, changed DPI/monitor/window geometry, user cursor movement and cooperative fixture/cursor recovery. Evidence: `docs/evidence/windows/mouse-2026-10-08.json`.

65 unit tests pass, including 19 new mouse policy/transport tests. Mouse actions remain bounded to supported selected UI Automation controls; there is no arbitrary desktop typing or general canvas automation. Delivered input returns a partial result until the caller verifies its actual symptom. Native fixture actions and Python authorization checks are separately validated, not a full API/Gemma flow. Physical multi-monitor/DPI hardware, process crash at every input boundary and actual Gemma-driven interaction remain untested. See `docs/evidence/windows/MOUSE_TOOLS.md` for integration and limits.

A small predetermined controller demo script is included for later use. Demo recording/presentation is deferred at the user's request; no video was produced. No model inference or real troubleshooting success is claimed.

## Real Gemma guest integration and recovery: 8 October 2026

Member 2 provider source `41b1c9b` was exercised without modifying teammate files, using the existing host model `gemma4:e2b`, Ollama 0.35.1 on host-only loopback `127.0.0.1:11435`. Default port 11434 was occupied by a nonresponsive listener; no host networking configuration was changed. No model weights or VM disk were copied/downloaded. Native code/test revision is recorded in each sanitized JSON report.

The real text flow passed: fresh guest accessibility facts → real local Gemma proposal to set the synthetic demonstration checkbox On (2890 ms inference) → human Yes approval in the guest → newly bound native observation/control baseline → native action → independently observed `Feature state: True` → approved restoration to Off → cooperative fixture closure. Guest report at 07:40:20 UTC / 13:10:20 IST. Reports: `gemma-text-2026-10-08.json` and `gemma-desktop-2026-10-08.json`. This is a real cross-machine inference/execution test harness, not the API/session/token or Python policy flow. Approval covers the exact synthetic checkbox change and baseline restoration; target/control/baseline are rechecked after approval. No real application symptom is claimed.

Live selected-window capture was supplied to the same real Gemma vision provider. It returned `visible_state: unknown` and `operation: none`; validation correctly blocked execution. Preserve this as **failed/unsupported for this tested image**, not vision success. Report: `gemma-vision-2026-10-08.json`. No hosted image transfer occurred and no PNG/base64 is published.

Original print symptom: live guest probe confirmed Spooler Running but no printer configured, no Microsoft Print to PDF driver or matching local driver package. The new bounded PDF print probe therefore reports blocked, with both PDF/physical print verification false. Report: `print-probe-2026-10-08.json`. No driver installation, external print or new service fault was performed. A configured printer and independently checked output are still prerequisites for a print-repair success claim.

73 unit tests pass (8 added recovery cases); fresh Python compilation and PowerShell parsing pass. `CheckboxRecovery` persists a baseline before input and offers conditional, newly approved restoration. See `RECOVERY.md`. The helper's Python journal/API wiring was not live-tested inside the guest. Keep user-facing desktop changes disabled until Member 3 integrates these gates and a chosen real workflow's original-symptom verifier. Vision/API/live print remain pending. Demo recording remains deferred.
