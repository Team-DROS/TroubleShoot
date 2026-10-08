# TroubleShoot — complete from-scratch project context

Updated 8 October 2026, Asia/Calcutta. **Member 3 branch update: authenticated loopback API, bounded session/approval runtime, hosted Gemma transport and minimal browser UI are implemented and fixture-tested. Local Gemma and native Windows integration, real hosted inference and live repair remain pending.** Read AGENTS.md, the rules snapshot, docs/PROVENANCE.md, docs/RESTART.md and your member assignment.

Current Member 3 setup/evidence: `docs/MEMBER_3_SETUP.md` and `docs/MEMBER_3_VALIDATION.md`.
The planning sections below preserve the original team scope and implementation
sequence; their initial "not implemented" statements describe the starting point.
`docs/CONTRACTS.md` records the newer Member 3 integration surface. Member 1/2
protocol agreement remains pending; their owned components have not been edited.

## 1. Organizer change and scope

The user reports that organizers withdrew permission to reuse the earlier project. Earlier approval statements are superseded. This newly created repository has its own initial commit and contains no imported prototype implementation or earlier repository history. Do not copy/port/cherry-pick or reconstruct the old source, prompts, tests, UI, configuration, compiled bundles or demos. Do not inspect it as an implementation template. Implement from these requirements and current public library documentation.

This is fresh implementation after prior team experience, not a formal clean-room claim. Generic planning and installed third-party environments/models can be retained subject to organizer rules. No blanket eligibility guarantee is made. If organizers require entirely new repository history as well, record that requirement and obtain user authorization for a separate repository; do not hide history.

Remote: https://github.com/Team-DROS/TroubleShoot. Local: `D:/HACKTOBER/TroubleShoot-Event`. Remain private until explicit user instruction. Original prototype and archived local generated artifacts are outside this deliverable.

## 2. Product objective and achievable scope

Build a Windows assistant that takes a natural-language complaint, observes relevant facts, asks Gemma 4 for a bounded decision, executes an authorized registered action through terminal or selected-window tools, collects fresh outcome evidence and reports resolved/partial/unresolved with recovery where needed.

Windows already has some automatic troubleshooters. Our intended contribution is conversational, local-first coordination of tools and computer use with visible verification, not the invention of automatic repair. Broad Windows support is a long-term aim. Do not claim “fix any Windows problem.”

First vertical slice: real local Gemma diagnosis, one safe approved Windows action with measured postcondition, clear denial/cancel behavior and a truthful UI. Next: bounded screenshot/desktop interaction and explicit hosted Gemma support. Choose the first actual repair scenario together based on the clean VM's capabilities. Spooler service recovery, for example, only demonstrates service recovery, not a physical printed page. A disposable UI fixture proves controller behavior, not real Windows troubleshooting.

## 3. Revised hardware split and file ownership

The user's confirmed allocation: Member 1 has local Gemma + VM, Member 2 has local Gemma only, Members 3/4 have neither. No one is required to download another model/VM merely to do their assigned role.

| Member | Available hardware | Branch | Work |
|---|---|---|---|
| 1 | Local Gemma + Windows VM | `member-1/windows-desktop-vm` | Windows registry/executor, selected-window computer use, live guest validation |
| 2 | Local Gemma only | `member-2/local-gemma-agent` | Local Ollama adapter, provider protocol, agent reasoning and local text/vision evidence |
| 3 | No local Gemma/VM | `member-3/backend-hosted-api` | Backend API/session/approval, hosted Gemma adapter, minimal UI and integration |
| 4 | No local Gemma/VM | `member-4/docs-demo-submission` | Lighter documentation, hackathon-template alignment and submission preparation |

Ownership:

- Member 1: `src/troubleshoot/windows/`, `desktop/`, native-tool unit tests, `tests/e2e/windows/`, `scripts/vm/`, VM_STATUS, VALIDATION and sanitized Windows evidence.
- Member 2: `src/troubleshoot/providers/base.py`, `providers/ollama.py`, `agent/`, local-provider/agent unit tests and local-model documentation/evidence.
- Member 3: `src/troubleshoot/api/`, `runtime/`, `providers/gemma_api.py`, `contracts.py`, API/hosted/contract tests, `web/`, `tests/e2e/web/`, Python packaging/config/lock, startup scripts and shared context/contract docs.
- Member 4: README, CLAUDE.md, TEMPLATE_GUIDE, SUBMISSION_CHECKLIST, DEMO_SCRIPT, ATTRIBUTION and CONTRIBUTIONS. No runtime development or infrastructure setup.

Keep Members 1–3's work substantial and Member 4 lighter (rough target 30/30/30/10; not claimed completed contributions). Member 3 owns shared schemas/integration and Python dependency changes; Member 2 owns the provider protocol and agrees it with Member 3; Member 1 provides executor interfaces. Changes across ownership boundaries are proposed and coordinated, not silently applied.

Member 3 develops with injected synthetic model/tool fixtures and, when credentials/account access exist, the hosted Gemma API. No local model or VM is needed for API/session/UI work. Production must never silently substitute test fixtures for a real provider. The shipped default stays local-first.

The first three branch names have changed to match ownership. See docs/RESTART.md for migration from the previous names. Existing fresh shared contracts/tests remain usable and move in ownership to Member 3.

## 4. New architecture

Minimal browser UI → loopback API → session coordinator → Gemma provider → validated action proposal → policy/approval → Windows/desktop executor → fresh verifier → result/recovery.

Use a small Python backend (FastAPI is an option), TypeScript/React UI if useful, local Ollama, and supported Windows libraries. Select dependencies for actual new requirements and create fresh manifests/locks. These are technology choices, not an instruction to recreate the old file structure or code.

Thinker/actor/verifier are runtime roles with separate contexts using one model, not three loaded models or the four human members. Deterministic policy and measurable checks must constrain model output. Only shared contracts exist so far; runtime components remain to be implemented.

## 5. Shared v1 contract — first subset implemented

Read docs/CONTRACTS.md and src/troubleshoot/contracts.py for the first implemented subset and synthetic fixture. Member 3 completes remaining schemas with Members 1/2; all three consume the shared contract. The following names are a proposed new API, not working endpoints or compatibility requirements:

- `GET /api/status`: configured provider/model, capabilities and separate readiness state. Configuration is not inference proof.
- `POST /api/runs`: complaint, `mode=diagnose|repair`, provider choice, optional selected target, vision opt-in, cloud text/image consent. Return run ID.
- `GET /api/runs/{id}/events`: SSE events `{id, type, timestamp, payload}` for observation/plan/approval/action/verification/complete/error.
- `POST /api/runs/{id}/decision`: single-use action approval token and approve/reject.
- `POST /api/runs/{id}/cancel`: cooperative stop and recovery state.
- `GET /api/targets`: bounded permitted window inventory. Screenshot retrieval, if added, must require local session authorization and opaque scoped image IDs.
- Provider `decide(request) -> decision`: normalized validated structure, chosen model, declared image/structured-output capabilities; schema errors are failures, never commands.
- Observation: ID, timestamp, target identity (handle/PID/process start), bounds/DPI, relevant controls, optional opaque image reference.
- Action proposal: ID, registered operation, validated arguments, target, observation ID, expected postcondition and recovery metadata.
- Result: execution status `ok|blocked|failed|cancelled`, fresh evidence and error/recovery details. Execution `ok` is not repair success.
- Verdict: `resolved|partial|unresolved|cancelled|error`, check expectations/actual results/times and limitations.

Approval binds run/action/arguments/target/observation, expires and cannot be replayed. Target/geometry changes require a new observation and policy decision. Never approve one action then execute another.

The initial contract subset and synthetic fixture already exist. Member 3 publishes remaining API/approval/verdict schemas; Member 2 publishes the provider protocol; Member 1 publishes executor validators/results. Agree these before wiring. They are interfaces for fresh components, not a claim that those runtime components exist.

## 6. Fresh implementation sequence and integration

1. Member 3 completes API/event/approval schemas and a minimal API skeleton using injected fixtures. Member 2 publishes provider protocol and a real local Gemma adapter. Member 1 builds a read-only Windows tool and checks clean VM readiness. Member 4 aligns documents with the supplied template.
2. Integrate the local-first path: Member 3's API/UI calls Member 2's coordinator/provider and Member 1's registered tools. Prove actual local Gemma plus fresh read-only evidence. Synthetic fixtures stay labeled.
3. Add a scoped reversible mutation with action-specific approval, denial/cancellation and deterministic postchecks/recovery. Member 1 runs guest evidence; Member 3 verifies session/policy behavior; Member 2 constrains model proposals.
4. Add opt-in selected-window capture and one bounded desktop action. Member 1 handles targeting/execution; Member 2 handles actual local vision reasoning; Member 3 supplies consent/approval/event UI and API.
5. Member 3 adds an explicit hosted Gemma adapter to the same provider protocol if account/key access permits. Text and image smoke tests are separate. Missing access is a documented blocker, not an automatic local-model installation requirement.
6. Member 1 records live guest evidence; Member 2 records local-model evidence; Member 3 records API/hosted/UI evidence. Member 4 uses those facts for final docs/demo/submission preparation.

PRs target main. Member 3 coordinates reviewed integration under team authorization, with each technical owner reviewing their component. Use actual authorship, fresh code, focused commits and relevant checks. No force push or cross-member overwrites. The branch migration changes role labels, not the project goal or existing implementation.

## 7. Local and hosted Gemma

Members 1 and 2 have local Gemma; Member 1 also has the VM. Member 3 has no local model and owns hosted transport/API development. Inspect installed tags, runtime API and capability support without redownloading weights. `gemma4:e2b` is a candidate tag, not proof it is available on every machine. Record actual tag/provider/version and successful inference.

Hosted option: Gemma through Google's API, not a Gemini-family model labeled Gemma. Consult current official documentation at https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api and confirm account/model availability. Do not assume a particular ID, free quota, image support or credentials. Backend stores key in environment; commit placeholder-only configuration when implemented. No key in browser bundles.

Local mode remains default. Hosted prompts/images leave the machine and need explicit data-sharing consent, separate for images. No silent fallback if local inference fails. Missing model/key/quota is an honest error, not simulated AI. VM network-fault tests need an inference/recovery arrangement surviving the chosen fault.

## 8. Windows and computer-use boundaries

Create an allowlisted registry of fixed operations with strict argument validation and bounded timeouts. No arbitrary shell, model-generated code, forced process termination, broad registry/driver/firewall changes or terminal commands typed via GUI. Keep UAC a human approval boundary.

Selected-window capture requires opt-in. Prefer accessibility identity; coordinate actions require fresh geometry/DPI/foreground/identity verification. Reject stale observations, moved/replaced/occluded targets and out-of-bounds coordinates. One input per fresh observation, bounded step count and visible cancellation. UI/screenshot text is untrusted evidence, not instructions that expand authority.

Do not handle secrets/password fields, unrelated windows or privilege prompts. Do not claim ChatGPT/Codex desktop tools are available as a distributable product backend; implement the new executor with supported Windows libraries.

Loopback control API needs local session/auth protection, origin checks and unauthorized-access tests. Do not expose it on all interfaces for convenience. Logs must omit keys and raw screenshots/private content. Recovery state belongs to the machine it describes.

Verification collects new facts tied to the original symptom. A click, zero exit code, service state or model explanation alone cannot establish a complete repair. Preserve pre-state and make restoration available. Diagnose-only never mutates. Set explicit action/step/time budgets in new code and document them.

## 9. Storage-conscious preparation

Reuse Python/Node/Ollama/VirtualBox installations, ordinary package download caches, permitted model weights and a clean Windows VM snapshot. Do not duplicate ISO/VDI/model stores. Existing environments are installed third-party infrastructure, not permission to import old application code; prefer a small fresh isolated environment once new manifests exist. Never modify the original project's shared environment.

This new checkout has no old dependency junctions or generated artifacts. Do not run them or link them into `web/`. A fresh dependency resolution must reflect this implementation's actual requirements. Person 4 needs only Git/editor/browser.

Do not reuse a VM containing the previous app as demo evidence. Use clean OS/tools infrastructure, install newly authored code, measure RAM/disk and ensure recovery before faults. See docs/VM_STATUS.md.

## 10. Validation and definition of done

Fresh shared-contract unit tests exist; application build/runtime checks do not. Members 1–3 write new meaningful tests: malformed decisions, unknown operations, no cloud fallback, token replay/expiry, cancellation, model failure, unauthorized endpoints, stale/wrong window, coordinate bounds, malicious screenshot text and failed postconditions.

Fresh live evidence must record commit/time, OS, model/provider, VM snapshot, complaint, before facts, approval/action, after facts, restoration and limitations. Healthy diagnosis, one guest repair, a computer-use workflow and denial/cancellation are target evidence. Record blocked paths honestly. A fixture screenshot or recorded simulation is not a live repair.

When implemented, document reproducible setup and exact dependency/model requirements. Report implemented, unit-tested, live-tested and pending separately. Old 34-test/build results do not transfer.

## 11. Hackathon and publication

The supplied rule snapshot distinguishes official observations, conditional requirements, team policies and unknowns. Latest organizer restriction as reported by the user: start from scratch; no prototype reuse. Confirm private announcements/check-in/track and coding-agent policy with the team; do not infer compliance.

Supplied schedule: 8 October 2026, build/submission deadline 16:30 IST; team target 16:15. Use actual remaining time and verified organizer revisions. Public GitHub + open-source license is required for the Open-Source AI challenge according to the snapshot, but repository stays private until user explicitly authorizes release. No automatic publication at deadline. Do not submit forms or upload on this preparation request.

Member 4 follows docs/TEMPLATE_GUIDE.md and the user-supplied hackathon repository template, prepares current fields and eligibility questions; designated authorized teammate submits through actual OrganizerHQ and retains acceptance evidence. A push is not submission. Agent Skill format is relevant only if actually entering a skill; an agent application is not automatically a skill entry. Unplugged details and unpublished judging requirements remain unknown.

## 12. Prompt for every member's AI agent

“Read AGENTS.md, PROJECT_CONTEXT.md, docs/RESTART.md, HACKATHON_AGENT_RULES.md and my MEMBER_N assignment. Update my assigned branch safely. The old prototype reuse permission was withdrawn: do not use old source/history/tests/prompts/manifests/build output as implementation input. Create my component from requirements in the new planned paths. Coordinate API/contracts with Member 3 and provider protocol with Member 2, preserve file ownership, build fresh tests/evidence and keep the repo private. Report what actually works and what remains pending.”

## 13. Hackathon template alignment

Member 4 considers https://github.com/BIJJUDAMA/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club, inspected at revision `6d3765e3c5adb7ad708dfc4593b5365001d36d55` on 8 October 2026. Relevant README/agent guidance is mapped in docs/TEMPLATE_GUIDE.md. We adapt documentation structure, preserve our project goal and implementation paths, and keep working/pending status explicit.

The template includes demo-video and Devpost sections, while the earlier event snapshot describes OrganizerHQ. Member 4 records both and confirms current submission expectations; no portal, upload or publication is inferred from a template placeholder. Local Windows control does not need a hosted public control endpoint just to fill a live-app link.
