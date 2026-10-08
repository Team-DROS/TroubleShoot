# Selected-window mouse tools

Member 1 implementation on `member-1/windows-desktop-vm`. Native input is newly authored using Windows SendInput; no old prototype code or results were used. This is an executor capability, not a complete Gemma-driven computer-use agent.

## Calling from Members 2 and 3

All five operations are registered in `DESKTOP_VALIDATORS`. Dispatch with:

```python
result = desktop.mouse_action(proposal.operation, authoritative_snapshot,
                              proposal.arguments, execution_context)
```

Use shared `require_target` on the proposal first. Keep observations and approvals server-side, and atomically consume an approval tied to the operation, arguments, selected control and original observation. Never trust client/model-supplied window metadata or cancel paths.

| Operation | Exact arguments | Initial supported controls |
|---|---|---|
| `mouse_move` | `control_id`, `x`, `y` | Button, CheckBox, RadioButton, ListItem, TabItem, Slider, List |
| `mouse_click` | `control_id`, `x`, `y` | Button, CheckBox, RadioButton, ListItem, TabItem |
| `mouse_double_click` | `control_id`, `x`, `y` | Button, ListItem |
| `mouse_scroll` | above plus `ticks` | List; integer -5 through 5, excluding zero |
| `mouse_drag` | above plus `to_x`, `to_y` | Slider; both points and the straight path stay inside that same control |

Clicks use the left button only. Drag is one short atomic down/move/up batch with eight interpolated points; no arbitrary duration, sustained hold, right-click, keyboard typing, canvas coordinates or title-bar dragging is exposed.

`x`/`y` and drag endpoints are **physical pixels relative to the original selected-window image**, not desktop pixels, logical DIP coordinates, percentages or normalized model coordinates. With a resized image, use `image_to_window(x, y, image_width, image_height, snapshot)` from `desktop.mouse`. Do not multiply by DPI again. Native input maps actual screen pixels across the current virtual desktop, including a negative origin; cursor position is checked after movement. The input point must also lie inside the actual client area and selected accessibility control.

New authoritative observation metadata: `client_bounds` (`left/top/width/height` in screen pixels), `cursor` (`[screen_x, screen_y]`), and `virtual_screen` (`[left, top, width, height]`). Existing target identity, timestamp, geometry/DPI, foreground and controls remain binding.

## Execution gates

- Repair mode and specific approval are required even for movement. Original observation age stays at most five seconds; approval does not reset its timestamp.
- Identity, bounds, client geometry, DPI, virtual desktop, foreground, control identity/name/bounds/state and initial cursor position are checked again. Disabled/offscreen controls and held mouse buttons/modifier keys are rejected.
- Native hit testing must identify the selected window and control; other windows covering a point and password/edit/document hits are refused. Terminals, credentials/UAC, browsers and administrative targets retain the conservative existing protection.
- A per-session Windows mutex excludes competing project mouse, accessibility-toggle and close actions. An abandoned lock fails the next action for inspection.
- Keep the cursor still and target foreground through observation/approval/input. Mouse approval in another window can invalidate both; Member 3 must design a keyboard/voice or otherwise non-disruptive approval flow, or obtain a new observation and specific approval. This branch provides no UI for that yet.
- Hold **Escape** to prevent further packets. Runtime cancellation uses `ExecutionContext.cancelled`; `PowerShellWorker.run_cancellable` supplies a private per-call marker and polls every 50 ms. Its payload comes from a private input file so a blocked stdin pipe cannot prevent timeout/cancellation polling.
- Double-click rechecks cursor, target and hit control between clicks and refuses a late second click if the Windows double-click interval has elapsed. Cancellation between clicks may leave the first click applied.

## Verification and recovery

`ExecutionResult` is **partial** after delivered input: delivery does not prove the requested application outcome or symptom. Evidence includes a fresh post-observation, actual cursor position, `input_delivered`, and `symptom_verified=False`. Failed/interrupted/cancelled input reports uncertainty and must not be retried automatically. A fresh semantic postcondition and scenario-specific recovery are still required.

Drag/click batches include button-up events, and a partial SendInput return attempts a release. Once an atomic batch is queued, cancellation cannot retract it or stop halfway through that batch. Process/OS crashes and races with unrelated applications/user input cannot be eliminated; this is not a zero-flaw guarantee. No automatic semantic undo or restoration of a user's cursor after user interference is implemented. Native integrity/UIPI restrictions remain in force; the controller does not bypass UAC.

## Validation boundaries

Host unit tests cover strict schema/bounds, scaling, negative monitor origin, stale/reused target, client/DPI/monitor/cursor changes, denial, cancellation, expired approval, supported control types, uncertain outcomes and worker lifecycle/cleanup. Native execution tests use only newly built synthetic WPF controls inside the Windows VM and recover the fixture/cursor afterward.

Live multi-monitor layouts, actual DPI changes, arbitrary third-party application behavior, crashes while injecting input, Gemma-generated points and the API/UI approval flow remain unvalidated. The fixture validates controller mechanics and its own state only. See VALIDATION.md and the sanitized mouse JSON report for actual checks, time and source revision.

Member 3 packaging must include **all `*.ps1`** files for `troubleshoot.desktop` (including `mouse-native.ps1`) plus the Windows worker. No additional Python dependencies are required. Keep guest test scripts out of agent registries: fixed test key injection and fixture controls are development-only, not shipping keyboard tools.

Native references: [Microsoft SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput), [MOUSEINPUT coordinates](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput), [WindowFromPoint](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-windowfrompoint).
