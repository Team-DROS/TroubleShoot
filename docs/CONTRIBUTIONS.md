> Final integration update, 8 October 2026: all four members' fresh work is being
> consolidated into main. Current production is hosted Gemma API + Windows PWA,
> with real read-only inference evidence and 203 passing checks. Earlier pending
> entries below are historical planning/checkpoints, not current feature status.
> See README.md, docs/API_PWA.md and docs/evidence/hosted/api-pwa-diagnosis.json.
> The user authorized public release; no event submission/video upload is claimed.

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

### Member 1 — Windows / VM (Pranesh Subramanian)

| Item | Status | Evidence |
|---|---|---|
| Windows operation allowlist: `start_spooler`, `spooler_status`, `system_snapshot` | ✅ Done | `src/troubleshoot/windows/registry.py`, `policy.py`, `runner.py` |
| Desktop executor: `toggle_checkbox`, `graceful_close`, 5 mouse ops | ✅ Done | `src/troubleshoot/desktop/executor.py`, `mouse.py` |
| Target identity binding + 5-second freshness check | ✅ Done | `require_target` wired in executor |
| Recovery records with DPAPI-private directory | ✅ Done | `src/troubleshoot/desktop/recovery.py` |
| Windows 11 guest: real Gemma text → approved checkbox action → fixture verify → restore | ✅ Done | `docs/evidence/windows/` — developer harness, not full API path |
| Read-only host Spooler check: returned Running | ✅ Done | `docs/evidence/windows/service-2026-10-08.json` |
| Gemma desktop vision: returned unknown/none, execution blocked safely | ✅ Done | `docs/evidence/windows/gemma-vision-2026-10-08.json` |
| VM validation scripts | ✅ Done | `scripts/vm/` |

### Member 2 — Local Gemma / provider (Umasuthan Palaniappan)

| Item | Status | Evidence |
|---|---|---|
| Local Ollama provider (`providers/ollama.py`) + base protocol | ✅ Done | `src/troubleshoot/providers/` |
| Agent coordinator, prompts, decision parsing, CLI | ✅ Done | `src/troubleshoot/agent/` |
| 7 recorded inference runs — `gemma4:e2b`, Ollama 0.40.1 | ✅ Done | `docs/evidence/local-model/*.json` |
| 6/6 simulated scenarios passed | ✅ Done | `local-gemma-eval-20261008T064725Z.json` |
| Decisions on real Member 1 guest facts | ✅ Done | `local-gemma-guest-facts-20261008T070836Z.json` |
| Vision pass: Gemma read stopped-spooler from screenshot | ✅ Done | `local-gemma-vision-20261008T065641Z.json` |
| Injected-text safety: "ignore previous instructions" banner → no change | ✅ Done | `local-gemma-vision-20261008T065342Z.json` |
| Agent unit tests (test_agent.py, test_provider_local.py) | ✅ Done | `tests/unit/` |

### Member 3 — Backend API / hosted (Srinath Balakrishnan)

| Item | Status | Evidence |
|---|---|---|
| Shared contracts + 16 unit tests | ✅ Done — `cae0176` | VALIDATION.md |
| FastAPI loopback API with session tokens and SSE event timeline | ✅ Done | `src/troubleshoot/api/app.py` |
| Runtime / PowerShell worker / session state | ✅ Done | `src/troubleshoot/runtime/` |
| Hosted Gemma transport (`providers/gemma_api.py`) — real inference passed | ✅ Done | `docs/evidence/hosted/api-pwa-diagnosis.json` |
| DPAPI-encrypted key setup (`configure-api.ps1`) | ✅ Done | `scripts/configure-api.ps1` |
| Installable PWA console with manifest, icons, service worker | ✅ Done | `src/troubleshoot/api/console/` |
| 156 unit + 42 API/runtime + 5 console UI tests passed | ✅ Done | `docs/API_PWA.md` validation record |
| Real hosted read-only Windows diagnosis end-to-end | ✅ Done | `docs/evidence/hosted/api-pwa-diagnosis.json` |

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
