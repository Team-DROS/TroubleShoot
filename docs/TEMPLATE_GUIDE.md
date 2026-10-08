# User-supplied hackathon template guide

Owner: Member 4.
Source: https://github.com/BIJJUDAMA/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
Inspected 8 October 2026 at revision `6d3765e3c5adb7ad708dfc4593b5365001d36d55`.
Files inspected: README.md, AGENTS.md, CLAUDE.md.

This is the template supplied by the user. Current organizer directions and our
project constraints still govern eligibility, release and submission.

---

## What to apply

Use the template's README structure to cover:
- Problem / motivation
- Solution and key differentiators
- Architecture and technology stack
- Event-time work and team contributions
- Application / demo access
- AI components and open-source usage
- Reproducible setup
- Lessons and challenges
- Credits and license

Mark absent technologies **N/A** and pending evidence **pending/not yet recorded**.
Maintain honest claims, meaningful external attribution, focused implementation
and safe credential handling. Keep organizer-only information out of the README.
The template's CLAUDE.md points to its agent instructions; our `CLAUDE.md`
similarly delegates to `AGENTS.md`.

---

## Our project mapping

| Template section | Our content source |
|---|---|
| Problem / motivation | README.md §Problem Statement |
| Solution / key features | README.md §Solution, §Key Features |
| Differentiation | README.md §Innovation and Differentiation |
| Architecture / stack | README.md §Technical Implementation |
| Event-time work | README.md §Implementation During the Hackathon + CONTRIBUTIONS.md |
| Working app / demo | README.md §Working Application + DEMO_SCRIPT.md |
| AI components | README.md §Open Source and AI Usage + ATTRIBUTION.md |
| Setup | README.md §Setup and Usage |
| Challenges / learnings | README.md §Challenges and Learnings |
| Credits / license | README.md §Credits and License + ATTRIBUTION.md |
| Devpost / demo video | README.md §Demo Video + DEMO_SCRIPT.md |

**Windows/desktop/guest evidence:** ask Member 1.
**Local Gemma/provider/reasoning evidence:** ask Member 2.
**Backend/hosted/UI/setup facts:** ask Member 3.

Do not import upstream application code or expand Member 4's role into technical
development or video production.

---

## Submission differences to resolve

The template includes a **Devpost** demo-video field; the earlier event snapshot
identifies **OrganizerHQ** and an optional demo URL. These differences are unresolved.

Current status:
- Neither Devpost nor OrganizerHQ submission has been made.
- No public demo video has been recorded for the fresh project.
- Template placeholders do not prove a submission requirement or successful submission.

Action items for the team:
- [ ] Confirm with organizers whether Devpost and OrganizerHQ are both required or one replaces the other.
- [ ] Confirm whether a live-app URL or a local setup walkthrough satisfies judging access.
- [ ] Member 4 records the authoritative answer here and in SUBMISSION_CHECKLIST.md.

A local Windows app does not need a hosted public control endpoint merely to fill
a link field. Never expose the native-control loopback API publicly.
Keep the repository private until explicit user release instruction.

---

## Template alignment checklist

- [ ] Real member names and actual new contributions supplied by the team.
- [x] Working versus planned features clearly distinguished (README, DEMO_SCRIPT).
- [x] N/A / pending marked for unimplemented technologies (README technology table).
- [ ] Exact model tag and Ollama/provider version confirmed by Members 1 and 2.
- [ ] Setup commands verified by technical owners (Members 2/3 own runtime setup).
- [ ] `.env.example` added (placeholder only, by Member 3) when runtime config implemented.
- [x] Architecture diagram present and labeled as proposed (mermaid in README).
- [x] Challenges and learnings section present.
- [x] Attribution and license accurate (ATTRIBUTION.md, LICENSE).
- [ ] Demo video / recording slot filled with authorized newly recorded footage.
- [ ] App/demo access and actual portal requirements confirmed with organizers.
- [x] No fabricated performance, guest result, uploaded video or accepted submission claim.
- [x] Repository private; no release authorized yet.
