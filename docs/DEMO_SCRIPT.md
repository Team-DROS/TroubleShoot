# Demo script — TroubleShoot

Owner: Member 4. Created 8 October 2026, Asia/Calcutta.
Deadline: 16:30 IST 8 October 2026; team target 16:15.

**Status:** Script prepared from project design and pending team evidence.
No live application, model inference or guest repair currently exists.
Sections marked **[EVIDENCE PENDING]** require recordings/screenshots from Members 1–3
before this script can be used for a live or recorded demo.

Do not re-use old prototype footage. Request newly authorized recordings from
the team and insert their file paths or YouTube/Devpost links here.

---

## Purpose

Provide a clear, honest walkthrough of what TroubleShoot does (or is designed
to do) during the hackathon demo. The script has two parts:

1. **Architecture walkthrough** — what exists and how the pieces connect.
2. **Scenario walkthrough** — a step-by-step intended workflow showing one
   bounded Windows troubleshooting run.

Judges should be able to follow this even if no live environment is available,
because it explicitly distinguishes implemented from planned stages.

---

## Pre-demo checklist (Member 1 / host)

- [ ] Clean Windows guest VM running, snapshot taken.
- [ ] Ollama running on host (Member 2) with Gemma 4 tag confirmed.
- [ ] Repository cloned to the demo machine on correct branch.
- [ ] `PYTHONPATH=src python -m unittest discover -s tests/unit -v` passes.
- [ ] No old prototype app or demo materials visible.
- [ ] Screen/window sharing ready; UAC dialog visible to audience.

---

## Part 1 — What is built (≈ 2 minutes)

### Slide / repo view

> "TroubleShoot is a fresh hackathon build — started today on 8 October 2026
> from a clean repository. We are a four-person team. Each member has different
> hardware:
>
> - Member 1: Windows VM + local Gemma — owns the Windows executor and guest validation.
> - Member 2: local Gemma only — owns the AI provider adapter and agent reasoning.
> - Member 3: no local model/VM — owns the backend API, hosted Gemma support and UI.
> - Member 4: no model/VM — owns documentation, demo and submission preparation.
>
> The local-first design means Gemma runs on the user's own machine. Text and
> images only leave the machine if the user explicitly consents to hosted inference."

### Show the contract tests

Open a terminal and run:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests/unit -v
```

Expected output: 16 tests, all OK.

> "These 16 tests validate the shared contract boundary — the rules that
> every component in the system must satisfy before any Windows action can
> be proposed, approved or executed. They cover consent enforcement,
> operation allow-listing, target identity binding, stale observation
> rejection and approval token rules."

### Show `contracts.py` briefly

Point to:
- `RunRequest` — complaint, mode, provider, consent flags.
- `parse_action` — rejects unknown operations and extra fields.
- `require_target` — binds action to an observed window with a freshness check.

---

## Part 2 — Intended workflow scenario (≈ 3 minutes)

**Scenario:** *"My printer spooler has stopped. Can you fix it?"*

This walkthrough describes the intended runtime flow. Steps without
**[LIVE]** or **[RECORDED]** markers are design descriptions.
No live repair has been performed yet.

### Step 1 — User submits complaint

User opens the minimal browser UI (planned, Member 3).
Types: `"My print spooler service keeps stopping."`
Selects mode: `repair`. Provider: local Ollama (default).

> Contract created:
> ```json
> { "complaint": "My print spooler service keeps stopping.",
>   "mode": "repair", "provider": "ollama",
>   "cloud_consent": false }
> ```

### Step 2 — Fresh observation

The Windows executor (planned, Member 1) reads the current spooler service state
using a registered read-only tool, collecting:

- Service name, status, PID and process start timestamp.
- No screenshot; no mutation at this step.

**[EVIDENCE PENDING — Member 1]**: attach a screenshot or screen recording
of the read-only service state query here.

### Step 3 — Gemma diagnosis

The local Gemma provider (planned, Member 2) receives the observation
and returns a bounded action proposal:

```json
{ "operation": "restart_service",
  "arguments": { "service_name": "Spooler" },
  "observation_id": "<fresh-obs-id>" }
```

The contract layer checks:
- `restart_service` is in the registered operation allow-list.
- No extra fields.
- Observation ID matches the fresh read.

**[EVIDENCE PENDING — Member 2]**: attach a terminal log showing a real
local Gemma response here (tag, timing, exact text).

### Step 4 — Approval gate

The UI shows a confirmation dialog (planned, Member 3):

> *"Gemma proposes: restart the Windows Print Spooler service.*
> *This will interrupt active print jobs.*
> *Approve / Reject"*

The user clicks **Approve**. A single-use token is created, bound to this
exact action, target, observation and run.

**[EVIDENCE PENDING — Member 3]**: attach a screenshot of the approval UI.

### Step 5 — Execution and fresh verification

The Windows executor (Member 1) runs the registered `restart_service`
operation, then immediately re-reads the service state (post-check).

- Before state: stopped.
- After state: running, new PID, new start timestamp.
- Verdict: `resolved` (if post-check confirms running).

**[EVIDENCE PENDING — Member 1]**: attach before/after service-state
screenshots from the clean guest VM.

### Step 6 — Result reported

The UI displays:

> *"Spooler service restarted successfully.*
> *Before: stopped. After: running (PID 1234, started 11:42:07).*
> *[View evidence] [Cancel/undo if available]"*

---

## What to say about pending items (honest disclosure)

> "At the time of this demo, the shared contract layer and 16 unit tests are
> the working foundation. The Windows executor, local Gemma adapter, backend
> API and browser UI are under construction by the respective team members.
> We have a clear integration plan and separation of concerns. The contract
> tests prove that no unregistered operation, stale target or missing consent
> can reach the executor — by design."

---

## Cancellation and denial demonstration (if time allows)

Show the test `test_unknown_operation_rejected` — the contract layer
rejects `"run_shell"` before it can reach any executor.

Show the test `test_stale_observation_rejected` — a 6-second-old
observation is rejected even if the action itself is valid.

---

## Demo video / recording instructions **[EVIDENCE PENDING]**

When Members 1–3 supply authorized recordings:

1. Do **not** reuse old prototype footage.
2. Record commit hash, date/time, OS version, model tag and Ollama version
   at the start of each recording.
3. Keep recordings under 3 minutes each per scenario.
4. Upload to an authorized location (team-managed Google Drive or direct
   Devpost/OrganizerHQ upload). No public YouTube link without team
   authorization.
5. Paste the link(s) into `README.md` → **Demo Video** section and into
   `docs/SUBMISSION_CHECKLIST.md`.

---

## Submission portal notes

The user-supplied template includes a **Devpost** demo-video field. The earlier
event snapshot references **OrganizerHQ**. These may both be required or one
may supersede the other — the team must confirm with organizers before submitting.
No portal completion, upload or external message is authorized by Member 4 alone.
