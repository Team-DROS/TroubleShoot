# TroubleShoot — complete from-scratch project context

Updated 8 October 2026, Asia/Calcutta. **Planning baseline only: no application, UI, tests, build configuration or working model integration exists yet.** Read AGENTS.md, the rules snapshot, docs/PROVENANCE.md, docs/RESTART.md and your member assignment.

## 1. Organizer change and scope

The user reports that organizers withdrew permission to reuse the earlier project. Earlier approval statements are superseded. This newly created repository has its own initial commit and contains no imported prototype implementation or earlier repository history. Do not copy/port/cherry-pick or reconstruct the old source, prompts, tests, UI, configuration, compiled bundles or demos. Do not inspect it as an implementation template. Implement from these requirements and current public library documentation.

This is fresh implementation after prior team experience, not a formal clean-room claim. Generic planning and installed third-party environments/models can be retained subject to organizer rules. No blanket eligibility guarantee is made. If organizers require entirely new repository history as well, record that requirement and obtain user authorization for a separate repository; do not hide history.

Remote: https://github.com/Team-DROS/TroubleShoot. Local: `D:/HACKTOBER/TroubleShoot-Event`. Remain private until explicit user instruction. Original prototype and archived local generated artifacts are outside this deliverable.

## 2. Product objective and achievable scope

Build a Windows assistant that takes a natural-language complaint, observes relevant facts, asks Gemma 4 for a bounded decision, executes an authorized registered action through terminal or selected-window tools, collects fresh outcome evidence and reports resolved/partial/unresolved with recovery where needed.

Windows already has some automatic troubleshooters. Our intended contribution is conversational, local-first coordination of tools and computer use with visible verification, not the invention of automatic repair. Broad Windows support is a long-term aim. Do not claim “fix any Windows problem.”

First vertical slice: real local Gemma diagnosis, one safe approved Windows action with measured postcondition, clear denial/cancel behavior and a truthful UI. Next: bounded screenshot/desktop interaction and explicit hosted Gemma support. Choose the first actual repair scenario together based on the clean VM's capabilities. Spooler service recovery, for example, only demonstrates service recovery, not a physical printed page. A disposable UI fixture proves controller behavior, not real Windows troubleshooting.

## 3. Team split and file ownership — all paths are to be created

| Member | Hardware | Branch | Owned planned paths | Deliverable |
|---|---|---|---|---|
| 1 | Gemma PC A | `member-1/gemma-orchestrator` | `src/troubleshoot/api/`, `src/troubleshoot/agent/`, `src/troubleshoot/providers/`, `src/troubleshoot/contracts.py`, Python packaging/config, `tests/unit/test_provider*`, `tests/unit/test_agent*`, `tests/api/`, `scripts/start*` | New backend, provider adapters, coordinator and integration |
| 2 | Gemma PC B | `member-2/windows-computer-use` | `src/troubleshoot/windows/`, `src/troubleshoot/desktop/`, `tests/unit/test_windows*`, `tests/unit/test_desktop*` | New registered Windows tools and selected-window executor |
| 3 | VirtualBox | `member-3/ui-vm-validation` | `web/`, `tests/e2e/`, `docs/VM_STATUS.md`, `docs/VALIDATION.md`, sanitized `docs/evidence/` | New minimal UI and real guest validation |
| 4 | No model/VM needed | `member-4/docs-demo-submission` | README, `docs/SUBMISSION_CHECKLIST.md`, new `docs/DEMO_SCRIPT.md`, `docs/ATTRIBUTION.md`, `docs/CONTRIBUTIONS.md` | Lighter documentation/demo/submission preparation |

Approximate effort target: 30/30/30/10, not a claim about completed contributions. Resource assignments are role slots; swap people if hardware overlaps. Person 1 owns shared context/contracts and integration; Person 2 proposes Python dependency needs to Person 1; Person 3 owns frontend dependencies. Do not independently rewrite shared files. Person 4 does not own runtime development or VM setup.

## 4. New architecture

Minimal browser UI → loopback API → session coordinator → Gemma provider → validated action proposal → policy/approval → Windows/desktop executor → fresh verifier → result/recovery.

Use a small Python backend (FastAPI is an option), TypeScript/React UI if useful, local Ollama, and supported Windows libraries. Select dependencies for actual new requirements and create fresh manifests/locks. These are technology choices, not an instruction to recreate the old file structure or code.

Thinker/actor/verifier are runtime roles with separate contexts using one model, not three loaded models or the four human members. Deterministic policy and measurable checks must constrain model output. No implementation already exists.

## 5. Proposed shared v1 contract — agree before implementation

Person 1 creates actual schemas and sample fixtures; Persons 2/3 consume them. The following names are a proposed new API, not working endpoints or compatibility requirements:

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

Person 1's first small integration commit is schemas + synthetic fixtures, not a full application. Until available, Persons 2/3 can author internal modules/UI shell against this written proposal. They must reconcile names once Person 1 publishes actual schemas.

## 6. Fresh implementation sequence and integration

1. Person 1 authors minimal package/test setup and shared schemas; Person 2 authors a read-only tool plus target identity checks; Person 3 creates a minimal UI and checks clean VM readiness; Person 4 prepares truthful planning docs.
2. Integrate actual local Gemma request and one read-only tool end-to-end. Use a real model smoke check; mocked fixtures stay labeled.
3. Add one scoped mutation, specific approval, denial/cancellation and measured postcondition/recovery. Build tests for failure as well as success.
4. Add selected-window capture, image reasoning and one bounded input action with freshness checks. First fixture validation, then a supported guest application scenario.
5. Add hosted Gemma via explicit provider selection/consent if account access permits; measure text and images separately. Preserve the working local path.
6. Run guest evidence, document setup and limitations, prepare final submission. Defer additional categories and polish if the core slice is not proven.

Keep PRs small and target main. Each person commits with their real identity; Person 1 coordinates integration under team authorization. Rebase/merge only fresh work, never resurrect the removed import. Before merging, update from origin/main and rerun relevant checks. No force-pushing or cross-member overwrites.

## 7. Local and hosted Gemma

Persons 1 and 2 already have Gemma 4 installed according to the user. Inspect installed tags, runtime API and capability support without redownloading weights. `gemma4:e2b` is a candidate tag, not proof it is available on every machine. Record actual tag/provider/version and successful inference.

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

No tests/build currently exist. Members 1–3 write new meaningful tests: malformed decisions, unknown operations, no cloud fallback, token replay/expiry, cancellation, model failure, unauthorized endpoints, stale/wrong window, coordinate bounds, malicious screenshot text and failed postconditions.

Fresh live evidence must record commit/time, OS, model/provider, VM snapshot, complaint, before facts, approval/action, after facts, restoration and limitations. Healthy diagnosis, one guest repair, a computer-use workflow and denial/cancellation are target evidence. Record blocked paths honestly. A fixture screenshot or recorded simulation is not a live repair.

When implemented, document reproducible setup and exact dependency/model requirements. Report implemented, unit-tested, live-tested and pending separately. Old 34-test/build results do not transfer.

## 11. Hackathon and publication

The supplied rule snapshot distinguishes official observations, conditional requirements, team policies and unknowns. Latest organizer restriction as reported by the user: start from scratch; no prototype reuse. Confirm private announcements/check-in/track and coding-agent policy with the team; do not infer compliance.

Supplied schedule: 8 October 2026, build/submission deadline 16:30 IST; team target 16:15. Use actual remaining time and verified organizer revisions. Public GitHub + open-source license is required for the Open-Source AI challenge according to the snapshot, but repository stays private until user explicitly authorizes release. No automatic publication at deadline. Do not submit forms or upload on this preparation request.

Member 4 prepares current fields and eligibility questions; designated authorized teammate submits through actual OrganizerHQ and retains acceptance evidence. A push is not submission. Agent Skill format is relevant only if actually entering a skill; an agent application is not automatically a skill entry. Unplugged details and unpublished judging requirements remain unknown.

## 12. Prompt for every member's AI agent

“Read AGENTS.md, PROJECT_CONTEXT.md, docs/RESTART.md, HACKATHON_AGENT_RULES.md and my MEMBER_N assignment. Update my assigned branch safely. The old prototype reuse permission was withdrawn: do not use old source/history/tests/prompts/manifests/build output as implementation input. Create my component from requirements in the new planned paths. Coordinate schemas with Member 1, preserve file ownership, build fresh tests/evidence and keep the repo private. Report what actually works and what remains pending.”
