# Team contributions — TroubleShoot

Owner: Member 4. Created 8 October 2026, Asia/Calcutta.
This is a log of **actual new work** committed in this fresh repository.
Assigned roles are not contribution claims; only completed and merged work is recorded here.
Member 4 updates this file as the team reports evidence and as PRs merge into `main`.

---

## What counts

Only work that is:
- **Newly authored** in this repository (no ported/cherry-picked prototype code), and
- **Committed and pushed** to the relevant member branch, and
- **Verified** (unit-tested, or has live evidence where applicable)

is recorded as a contribution. Pending items are listed separately.

---

## Current contributions (as of 8 October 2026, 11:30 IST)

### Shared — all members / initial setup

| Item | Who | Commit(s) | Evidence |
|---|---|---|---|
| Initial repo creation, planning docs, LICENSE | Team lead / shared | `bdb8919` | Commit history |
| Project scope, architecture, hardware split | Shared (documented) | `ead43f2` | PROJECT_CONTEXT.md, AGENTS.md |
| Shared contract module (`src/troubleshoot/contracts.py`) | Member 3 (owns contracts) | `cae0176` | 150 lines, stdlib only |
| 16 fresh boundary unit tests (`tests/unit/test_contracts.py`) | Member 3 | `cae0176` | All pass — see VALIDATION.md |
| Synthetic inspection fixture (`docs/fixtures/inspect_target.json`) | Member 3 | `cae0176` | Labeled synthetic, not live |
| Role-table + branch realignment documentation | Shared | `9b7fddd` | RESTART.md, MEMBER_N.md files |

### Member 1 — Windows / VM

| Item | Status | Evidence target |
|---|---|---|
| Windows native tool design and executor interface | Pending | `src/troubleshoot/windows/` — not yet implemented |
| Selected-window observation and identity checks | Pending | `src/troubleshoot/windows/` |
| Live guest validation evidence | Pending | VALIDATION.md appendix |
| VM snapshot and clean-state notes | In progress | VM_STATUS.md |

### Member 2 — Local Gemma / provider

| Item | Status | Evidence target |
|---|---|---|
| Local Ollama provider adapter | Pending | `src/troubleshoot/providers/ollama.py` |
| Provider base protocol | Pending | `src/troubleshoot/providers/base.py` |
| Agent reasoning loop | Pending | `src/troubleshoot/agent/` |
| Local-model inference evidence (tag, response, timing) | Pending | VALIDATION.md appendix |

### Member 3 — Backend API / hosted

| Item | Status | Evidence target |
|---|---|---|
| Shared contracts + 16 unit tests | ✅ Done — `cae0176` | VALIDATION.md |
| API routes (`src/troubleshoot/api/`) | Pending | FastAPI skeleton |
| Session/approval/event schemas | Pending | docs/CONTRACTS.md update |
| Hosted Gemma transport | Pending — depends on key access | `src/troubleshoot/providers/gemma_api.py` |
| Minimal browser UI (`web/`) | Pending | Web folder |
| SSE event stream | Pending | API integration |

### Member 4 — Documentation / submission

| Item | Status | Commit |
|---|---|---|
| Expand CLAUDE.md with agent entry-point list | ✅ Done | `ee18873` |
| ATTRIBUTION.md — licenses, components, AI disclosure | ✅ Done | `4b100d6` |
| CONTRIBUTIONS.md (this file) — per-member log | ✅ Done | `331236f` |
| DEMO_SCRIPT.md — structured walkthrough | ✅ Done | `e33d7ec` |
| SUBMISSION_CHECKLIST.md — updated with current status | ✅ Done | `c682de1` |
| TEMPLATE_GUIDE.md — alignment checklist update | ✅ Done | `de66bc8` |
| README.md — template-aligned, fully honest | ✅ Done | `b240eed` |
| VALIDATION.md — deliverables table + pending-evidence sections | ✅ Done | `0b1909b` |

---

## Pending items (for this file)

- [ ] Member 1: Report Windows executor commit hash, test count, VM evidence date.
- [ ] Member 2: Report Ollama adapter commit hash, exact model tag, test evidence.
- [ ] Member 3: Report API skeleton commit hash, hosted-provider status, UI commit.
- [ ] Member 4: Append final contribution rows after PRs merge.
- [ ] All: Confirm real member names to replace role-slot placeholders.

---

## Notes

- Team member names are **not yet provided**; role slots are used as placeholders.
  Real identities will be recorded when the team confirms them.
- Contributions are recorded per-role, not per-commit-author, because Git identity
  may differ from actual authorship for agent-assisted commits.
  Each member confirms their own contribution record before submission.
- The contribution split target is approximately 30 % / 30 % / 30 % / 10 % for
  Members 1–4 respectively; final percentages depend on what is actually implemented.
