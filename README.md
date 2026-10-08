# TroubleShoot - Team DROS

A Windows troubleshooting assistant with hosted Gemma 4 reasoning and an installable
PWA connected to a local Windows helper. Describe a problem, review fresh facts,
approve a specific action and inspect what verification actually establishes.

## Problem and solution

Windows already has some automatic troubleshooters. Many support workflows still
leave users interpreting instructions and performing checks. TroubleShoot coordinates
a limited set of registered Windows tools with AI reasoning, explicit approval,
cancellation, verification and recovery. It cannot fix every Windows problem.

## Current features

- Hosted Gemma API only in production, per-run cloud text consent, no fallback.
- Authenticated loopback helper and PWA operator console with an event timeline.
- Fresh system/network/Spooler diagnostics and bounded approved Spooler start.
- Server-side encrypted key setup, cancellation and explicit partial/unresolved results.

Desktop mutation and hosted vision are outside this prototype's enabled live flow.
Spooler Running proves service state, not successful printing.

## Setup and validation

See [setup and evidence](docs/API_PWA.md). Real hosted read-only Windows diagnosis and connection-only inference passed;
156 unit, 42 API/runtime and 5 synthetic console tests passed. Full hosted guest repair
and browser installation are pending. Tests are not live repair evidence.

## Architecture and stack

PWA -> loopback FastAPI -> bounded session -> hosted Gemma proposal -> deterministic
approval/policy -> registered Windows operation -> fresh checks. Python 3.11+,
FastAPI, httpx, PowerShell and browser JavaScript; no database required. The separate
web/ React landing preview is retained; the working UI is src/troubleshoot/api/console/.

## Team and event-time work

Member 1: Windows/desktop tools and guest validation. Member 2: local provider and
reasoning. Member 3: API/session/hosted integration. Member 4: lighter documentation
and template preparation. Final user-directed integration changes the shipped runtime
to hosted-only PWA. Names, actual submission and demo-video links await the team.

## Lessons, credits and limits

Model proposals, native execution and symptom resolution require separate validation.
PWA installation still requires a Windows helper and internet for inference.
See [provenance](docs/PROVENANCE.md), [attribution](docs/ATTRIBUTION.md),
[context](PROJECT_CONTEXT.md) and [submission checklist](docs/SUBMISSION_CHECKLIST.md).
This is the fresh event implementation. Repo stays private; no submission or upload
is claimed. Confirm template and event requirements before release.
