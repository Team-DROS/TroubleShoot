# TroubleShoot

**A Windows troubleshooting assistant with hosted Gemma 4 reasoning and an installable PWA connected to a local Windows helper.**

TroubleShoot lets you describe a Windows problem in plain English, watches the system gather real facts, asks Gemma to reason about them, and then—only after *you* approve—executes one bounded, registered action. It immediately re-checks whether the symptom actually changed, and tells you honestly whether it worked.

> Final integration update: all four members' fresh work is consolidated into main. Current production is **hosted Gemma API + Windows PWA**. 
> Built in a single day at **Hacktoberfest Hack Day Coimbatore × INIT Club & Idea Club** on 8 October 2026 by Team DROS.

---

## Why we built this

Most Windows troubleshooting today is a loop: read a support page, run a command, guess whether it helped, repeat. Automated troubleshooters exist, but they offer little visibility into *what* they're doing or *why*.

We wanted something different — a conversational assistant that shows you the evidence it collected, explains the reasoning behind a proposed fix, puts you in control of the decision, and then proves whether the outcome matched the expectation. Not "we ran something, trust us." Verified.

We don't claim TroubleShoot can fix every Windows problem. It targets a small, honest, demonstrable workflow first.

---

## What it does

```
You describe a symptom
   ↓
TroubleShoot reads real Windows facts (services, diagnostics)
   ↓
Gemma 4 reasons about them and proposes a specific, bounded action
   ↓
You review and explicitly approve (or reject/cancel)
   ↓
The approved action runs — nothing else
   ↓
Fresh postchecks verify whether the symptom changed
   ↓
You see: Resolved / Partial / Unresolved — with the evidence
```

---

## Team DROS

| Member | Role | Branch |
|---|---|---|
| **Pranesh Subramanian** | Windows tools, selected-window computer use, guest validation | `member-1/windows-desktop-vm` |
| **Umasuthan Palaniappan** | Local Gemma provider, agent reasoning, local evidence | `member-2/local-gemma-agent` |
| **Srinath Balakrishnan** | Backend API, hosted Gemma integration, PWA console | `member-3/backend-hosted-api` |
| **Sanjeev Singotam** | Documentation, template alignment, submission preparation | `member-4/docs-demo-submission` |

---

## What actually works today

### ✅ Shared contract layer (all members)
16 boundary tests enforce every trust rule in the system: unknown operations are blocked, stale observations are rejected, consent is required for hosted inference, extra fields from the model are stripped before they can reach any executor.

### ✅ Hosted Gemma API + PWA console (Member 3 & Integration)
- FastAPI loopback backend with session tokens, encrypted DPAPI key storage and SSE event timeline.
- Real hosted Gemma 4 connection-only inference passed with a read-only Windows diagnosis.
- 156 unit, 42 API/runtime and 5 synthetic console UI tests passed.
- Installable PWA console served at `http://127.0.0.1:8765` with manifest, icons and service worker.
- Cloud text consent is explicit and per-run. Hosted Gemma API is the only production inference; no silent fallback is enabled.

### 🔬 Experimental: Local Gemma reasoning (Member 2)
Real inference on `gemma4:e2b` via Ollama — 7 recorded evidence runs on 8 October 2026 (outside the enabled live flow).
- **6/6 simulated scenarios passed** (spooler repair, DNS repair, diagnose-only, injected-text safety, unresolved symptom, out-of-scope decline).
- **Decisions on real guest facts** from Member 1's Windows 11 guest — `start_spooler`, `system_snapshot`, `spooler_status` chosen correctly.
- **Vision pass**: Gemma correctly read "Print Spooler is listed as Stopped" from a screenshot and proposed a restart. Injected "ignore previous instructions" banner produced no change.

### 🔬 Experimental: Windows desktop executor (Member 1)
Newly authored PowerShell + Python executor running inside a Windows 11 guest VM (outside the enabled live flow).
- Real local Gemma text inference → human-approved synthetic checkbox action → fixture verification → restoration, through a developer harness.
- Read-only Spooler check returned Running on the host.
- Bounded operation allowlist includes `start_spooler`, `spooler_status`, `system_snapshot`, `checkbox_toggle`, `graceful_close`, and five scoped mouse operations. Desktop mutation and hosted vision are outside this prototype's enabled live flow.



---

## What's still pending

| Item | Status |
|---|---|
| Full hosted guest repair (API → executor path) | ⏳ Integration in progress |
| Browser-automated PWA install verification | ⏳ Blocked — browser automation failed to initialize |
| Hosted Gemma vision | ⏳ Disabled in this prototype |
| Real print success (not just Spooler Running) | ⏳ Requires physical printer in guest |
| Demo video | ⏳ Not recorded — see [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) |

Spooler Running proves service state only, not a successful print job. We say so explicitly.

---

## Architecture

```
Browser PWA (localhost)
    │  SSE event stream
    ▼
FastAPI loopback API  ←── session token / DPAPI key
    │
    ├── Hosted Gemma API  (explicit cloud consent required)
    │       └── gemma-4-26b-a4b-it or gemma-4-31b-it
    │
    ├── Local Ollama  (default, local-first)
    │       └── gemma4:e2b
    │
    └── Windows executor (registered ops only)
            ├── PowerShell native worker
            ├── Action allowlist + argument validators
            ├── Target identity binding (5-second freshness)
            └── Fresh postchecks → recovery record
```

The API, model and executor are deliberately separate: the model proposes, the policy validates, the user approves, the executor runs, and the verifier checks. No shortcut between any of these layers.

---

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, httpx |
| Local AI | Ollama 0.40.1, `gemma4:e2b` (4.6B Q4_K_M) |
| Hosted AI | Google Gemma API (`gemma-4-26b-a4b-it`) |
| Windows tools | PowerShell, .NET UI Automation, pywin32 |
| UI | Vanilla HTML/CSS/JS PWA (installable), React landing preview in `web/` |
| Testing | Python `unittest`, Node.js `--test`, 203+ tests total |
| Secrets | Windows DPAPI CurrentUser encryption; no keys in Git |

---

## Getting started

### Requirements

- Windows 10/11, Python 3.11+, Git
- A Google AI Studio account with Gemma API access and quota
- Chrome or Edge (for PWA install)
- *(Local mode only)* Ollama with `gemma4:e2b` pulled

### Install and run

```powershell
git clone https://github.com/Team-DROS/TroubleShoot.git
cd TroubleShoot

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock -e .

# Configure your Gemma API key (saved encrypted, never committed)
powershell -ExecutionPolicy Bypass -File scripts/configure-api.ps1

# Start the API and open the PWA console
powershell -ExecutionPolicy Bypass -File scripts/start-api-pwa.ps1
```

The console opens at `http://127.0.0.1:8765`. Select diagnostics, describe your problem, tick the cloud consent checkbox, and run.

### Run the tests

```powershell
# Contract + agent + provider + executor unit tests (156 total)
.\.venv\Scripts\python.exe -m unittest discover -s tests/unit -q

# API / session / runtime integration tests (42 total)
.\.venv\Scripts\python.exe -m unittest discover -s tests/api -q

# Shared-contract only (no install needed)
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests/unit -v
```

### Environment variables

| Variable | Purpose |
|---|---|
| `GEMMA_API_KEY` | Hosted Gemma key (alternative to DPAPI; keep out of Git) |
| `GEMMA_API_MODEL` | Override model (`gemma-4-31b-it` for the larger variant) |
| `PYTHONPATH` | Set to `src` when running without install |

See `.env.example` for a placeholder-only reference.

---

## Project structure

```
src/troubleshoot/
├── contracts.py          # Shared trust-boundary contracts (all members consume)
├── agent/                # Coordinator, prompts, decision parsing, CLI (Member 2)
├── providers/            # Ollama + hosted Gemma adapters (Members 2 & 3)
├── api/                  # FastAPI app, session, PWA console (Member 3)
├── runtime/              # PowerShell worker, session state (Member 3)
├── windows/              # Registry, policy, runner (Member 1)
└── desktop/              # UI Automation executor, mouse, recovery (Member 1)

tests/
├── unit/                 # 156 unit tests
├── api/                  # 42 API/integration tests
└── e2e/console/          # 5 synthetic console tests

docs/
├── evidence/
│   ├── local-model/      # 7 recorded Gemma inference runs (Member 2)
│   └── windows/          # Guest executor evidence (Member 1)
├── API_PWA.md            # Setup, demo scope and validation record
├── DEMO_SCRIPT.md        # Walkthrough script for judges
├── ATTRIBUTION.md        # Licenses and component notices
└── CONTRIBUTIONS.md      # Per-member actual work log
```

---

## Evidence and validation

All evidence was produced on 8 October 2026 from newly authored code.

| Evidence | Location | What it proves |
|---|---|---|
| 7 Gemma inference runs (container + Windows PC) | `docs/evidence/local-model/` | Real local model decisions on simulated and real guest facts |
| Hosted Gemma read-only diagnosis | `docs/evidence/hosted/api-pwa-diagnosis.json` | Real API connection, real Windows facts, real model response |
| Guest executor + checkbox fixture | `docs/evidence/windows/` | Human-approved action, target binding, postchecks, restoration |
| 203+ test results | `tests/` | Contract, agent, provider, API and console boundary checks |

No old prototype results are carried over. Tests are not live repair evidence.

---

## Decisions we're proud of

**Separate stages, no shortcuts.** The model, the policy, the user approval, the executor and the verifier are five separate steps. The model can't cause execution by producing a convincing payload. The executor can't skip the freshness check. The verifier can't reuse an old observation.

**Honest about limits.** Spooler Running ≠ successful print. Unknown vision result ≠ execution blocked. We say these things in the UI and in these docs.

**No silent fallback.** If local Ollama isn't running, you get an error — not a quiet switch to the hosted API. If hosted inference times out, you get a timeout — not a cached guess.

**5-second observation window.** The action you approve must match the *exact* window that was inspected, within 5 seconds. Replaced processes, moved windows and stale coordinates are all rejected before any input happens.

---

## Challenges and what we learned

- Splitting a same-day build across four people with different hardware (VM + Gemma, Gemma-only, no local model at all) required very clear interface contracts up front. The shared `contracts.py` module was the right call — it let everyone develop independently against the same shape.
- Gemma's reasoning quality on CPU-only hardware is good but slow (~43 s/decision). On a GPU or the team's Windows PC (~21 s) it's much more usable.
- "Execution returned OK" and "the symptom is resolved" are completely different things. Building the verification layer made this obvious in a way that reading about it doesn't.
- The observation freshness window (5 seconds) feels aggressive, but it's the right default. Window replacement during a troubleshooting session is a real threat, not a theoretical one.

---

## AI and open source usage

This project was built with AI coding assistance (Gemini/Claude). All generated code was reviewed and committed by the responsible team member. No prior prototype code was imported.

**Model licenses:** Gemma weights are subject to the [Gemma Terms of Use](https://ai.google.dev/gemma/terms), separate from this application's MIT license.

See [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md) for the full component list.

---

## Submission

**Event:** Hacktoberfest Hack Day Coimbatore × INIT Club & Idea Club, 8 October 2026
**Tracks considered:** Best Use of Gemma 4, Best Open-Source AI Project
**Repository:** https://github.com/Team-DROS/TroubleShoot
**Status:** Public release authorized by user after team merge into main.

No event submission or demo-video upload is claimed in this README. Confirm current organizer requirements before submitting. See [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md).

---

## Credits and license

Documentation structure informed by the [user-supplied hackathon template](https://github.com/BIJJUDAMA/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club) (revision `6d3765e3c5adb7ad708dfc4593b5365001d36d55`). No application code from that template was used.

See [docs/PROVENANCE.md](docs/PROVENANCE.md) for full repository history and fresh-build disclosure.

**License: MIT** — see [LICENSE](LICENSE).
Model weights and Windows installation media retain their own license terms.
