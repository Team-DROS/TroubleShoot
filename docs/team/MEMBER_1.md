# Member 1 — Windows tools, computer use and VM validation

**Branch:** `member-1/windows-desktop-vm`. **Hardware/workload:** Local Gemma 4 + Windows VM; substantial technical role.

Read AGENTS.md, PROJECT_CONTEXT.md, docs/CONTRACTS.md and HACKATHON_AGENT_RULES.md first. Preserve local changes before updating your branch. Existing shared-contract code and synthetic fixtures are newly authored and may be used; the earlier standalone prototype must not be copied or restored.

No running model adapter, API, UI or Windows executor exists yet. Every runtime feature below is work to implement and validate. Keep the repository private until explicit user instruction.
## Ownership

Own `src/troubleshoot/windows/`, `src/troubleshoot/desktop/`, `tests/unit/test_windows*`, `tests/unit/test_desktop*`, `tests/e2e/windows/`, `scripts/vm/`, `docs/VM_STATUS.md`, `docs/VALIDATION.md` and sanitized `docs/evidence/windows/`. Member 2 owns model reasoning/local provider; Member 3 owns API/runtime/shared schemas and packaging.

## Ordered work

1. Verify a clean Windows guest and resource/snapshot readiness. Reuse OS/tools/model infrastructure where permitted; install newly authored project code only. Do not copy the old application or its guest test results. Preserve disk space; no duplicate ISO/VDI/model download without a demonstrated need.
2. Build registered fixed Windows diagnostics with strict per-operation argument validation, timeouts and structured evidence. Export validators for `parse_action` and explicit executors; no model-generated shell text.
3. Build selected-window identity, accessibility inspection and consented capture. Include handle/PID/process-start time, fresh observation ID, geometry/DPI and foreground/visibility state. Coordinate observation schema additions with Member 3.
4. Implement one bounded desktop action at a time. Recheck identity/freshness/geometry immediately before input. Reject stale/replaced/out-of-bounds/protected targets, terminals/Run dialog, secret fields and UAC prompts. Prefer accessibility controls and keep UAC human-driven.
5. Work with Member 2 to connect actual Gemma image reasoning to your observations/actions and Member 3 to connect approvals/UI. Define one genuine reversible troubleshooting scenario, its postcondition and recovery before attempting it.
6. Validate inside the guest: healthy diagnosis, one approved repair, denial/cancellation, a computer-use workflow and a failed/partial outcome. Record actual revision/time/model/provider/snapshot, pre-state, action/approval, fresh checks and restoration. Do not fault host adapters or replace live evidence with footage from the old project.

## Acceptance and tests

Create new executor tests for wrong/reused identity, stale or future observation, DPI/geometry changes, foreground loss, extra args/unknown actions, malicious UI text, denied approval, cancellation and action success without symptom change. A running Spooler proves service recovery only; fixture GUI control proves controller behavior only.

Local Gemma on your host is useful for joint tests, but the Windows guest does not inherit host CUDA or host loopback. Agree a scoped inference arrangement with Members 2/3. A network fault may sever hosted/host inference: use a scenario preserving it or a documented recovery design. Report resource/recovery blockers honestly.

## Handoffs

Give Member 2 the operation registry, observations and postcheck evidence. Give Member 3 exact callable signatures, required privileges/dependencies, target metadata and recovery behavior. Member 3 applies Python packaging changes. Give Member 4 only sanitized fresh results and genuine demo steps.

## Prompt for your AI agent

“Read AGENTS.md, PROJECT_CONTEXT.md, docs/CONTRACTS.md and MEMBER_1.md. Work on member-1/windows-desktop-vm in my owned paths. Follow the revised hardware split; author fresh implementation/docs, coordinate with Member 3 on API/contracts and Member 2 on provider protocol. Keep the project local-first, preserve bounded Windows/computer-use and fresh verification, keep repository private and report actual evidence.”
