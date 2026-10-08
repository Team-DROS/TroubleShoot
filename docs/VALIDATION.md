# Fresh project validation

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
