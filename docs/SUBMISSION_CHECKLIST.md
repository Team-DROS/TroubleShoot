# Fresh-build submission checklist — not submitted

Owner: Member 4. Last updated: 8 October 2026, 11:43 IST.
Member 4 prepares these fields; a designated authorized teammate submits.
Repository remains private until explicit user publication instruction.

---

## Latest organizer guidance

The user reports withdrawal of prototype-reuse permission on 8 October 2026.
Start from scratch. Earlier permission is superseded.
The supplied `HACKATHON_AGENT_RULES.md` is a dated snapshot; confirm current
announcements, check-in, track, development-agent policy and the build window
with the team.

Record the reversal's source and time if available.
This newly created repository has independent history and imports planning only.
Disclose the team's earlier separate prototype if asked; no old implementation
or commits are present here.

---

## Official event sources

- https://events.mlh.com/events/15020-hacktoberfest-hack-day-coimbatore-x-init-club-idea-club
- https://www.mlh.com/events/hacktoberfest-hack-day-coimbatore-x-init-club/challenges
- https://www.mlh.com/events/hacktoberfest-hack-day-coimbatore-x-init-club/submissions/new

---

## Project identity

| Field | Value |
|---|---|
| Project name | TroubleShoot |
| Team name | Team DROS |
| Repository | https://github.com/Team-DROS/TroubleShoot (currently **private**) |
| Branch (Member 4) | `member-4/docs-demo-submission` |
| Submission deadline | 16:30 IST, 8 October 2026 |
| Team internal target | 16:15 IST |

---

## Before release — checklist

### Team / registration
- [ ] Confirm exactly four registered members, actual names and check-in status.
- [ ] Confirm primary track and any optional challenge tracks (Best Use of Gemma 4, Best Open-Source AI).
- [ ] Confirm private-repository access for all members and any judges.

### Documentation
- [x] README aligned with template sections and honest N/A/pending status.
- [x] ATTRIBUTION.md — licenses, third-party components, AI usage.
- [x] CONTRIBUTIONS.md — per-member log of actual new work.
- [x] DEMO_SCRIPT.md — structured walkthrough with evidence placeholders.
- [x] CLAUDE.md — agent pointer updated.
- [ ] Real member names added to README team table and CONTRIBUTIONS.md.
- [ ] Template alignment checklist fully resolved (see TEMPLATE_GUIDE.md).

### Implementation verification
- [x] 16 shared-contract unit tests pass (standard library, no install needed).
- [ ] Member 1: Windows executor implemented, tested and live guest evidence recorded.
- [ ] Member 2: Local Ollama adapter implemented, tested, exact model tag confirmed.
- [ ] Member 3: Backend API skeleton implemented; at least one SSE event emitted.
- [ ] Integration: local-first path wired (Member 3 API → Member 2 provider → Member 1 executor).
- [ ] No old prototype source, manifest, test or demo material in the repo.

### Evidence
- [ ] `docs/VALIDATION.md` updated with fresh commit hash, OS, model, scenario, before/after facts, limitations.
- [ ] Demo script evidence slots filled by Members 1–3.
- [ ] Video/recording authorized and linked (if required by organizers).

### Submission portals (confirm current requirement with team)
- [ ] Reconcile template Devpost field with OrganizerHQ snapshot — which is current?
- [ ] Both portals may be required; do not assume one replaces the other.
- [ ] Confirm whether a live-app URL or local-install instructions suffice for judging access.

### Security and secrets
- [ ] No API keys, passwords or private data in any committed file.
- [ ] `.env.example` added (placeholder-only, by Member 3) when runtime config exists.
- [ ] No raw screenshots containing private user data committed.

### License
- [x] MIT license file present (`LICENSE`).
- [ ] README credits and license section current and accurate.
- [ ] Model weight licenses acknowledged in ATTRIBUTION.md (done; verify against final used tags).

---

## Form preparation

**Project name:** TroubleShoot
**Project link:** https://github.com/Team-DROS/TroubleShoot (private until authorized)

**Description (draft — not ready for submission):**
> TroubleShoot is a local-first Windows troubleshooting assistant built with Gemma 4.
> It observes relevant system state, asks Gemma for a bounded decision, requires
> explicit user approval for any action, executes one registered operation and
> immediately re-checks the symptom. Only shared contract validation and 16 unit
> tests currently exist. Full executor, provider and API are under construction.
> Prior prototype reuse was withdrawn by organizers on 8 October 2026; this is a
> fresh build.

**Technologies (pending final manifests):** Python 3.11+, setuptools, Gemma 4
via local Ollama (planned), Google Gemma API (planned), FastAPI (planned).

**Challenge tracks to consider:**
- Best Use of Gemma 4 — requires live evidence of Gemma inference.
- Best Open-Source AI Project — requires public repository (not yet released).

Do not select tracks without confirmed evidence and eligibility.

---

## Final submission steps

- [ ] Refresh actual form fields and deadline (supplied: 16:30 IST, 8 October 2026).
- [ ] Verify final commit, setup instructions, capabilities and selected challenges.
- [ ] Authorized teammate completes the confirmed official route (OrganizerHQ and/or Devpost).
- [ ] Save acceptance receipt, timestamp, link, final commit hash and challenge selection.
- [ ] Stop build and submission changes at deadline unless organizers authorize an extension.
- [ ] A `git push` alone is **not** submission.

---

## Current status summary

| Area | Status |
|---|---|
| Shared contracts and unit tests | ✅ 16/16 pass |
| Windows executor (Member 1) | ⏳ Pending |
| Local Gemma adapter (Member 2) | ⏳ Pending |
| Backend API and UI (Member 3) | ⏳ Pending |
| Documentation (Member 4) | ✅ Core deliverables done |
| Live evidence | ⏳ Pending |
| Demo video | ⏳ Pending |
| Public release | 🔒 Private — not released |
| Submitted | ❌ Not submitted |
