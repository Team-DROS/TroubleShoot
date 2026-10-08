# Member 1 — Gemma backend and integration

**Branch:** `member-1/gemma-orchestrator`. **Resources/workload:** Gemma PC A; approximately 30% workload.

Read AGENTS.md, PROJECT_CONTEXT.md, docs/RESTART.md, HACKATHON_AGENT_RULES.md and docs/PROVENANCE.md first. Update your assigned branch with `git fetch origin`, `git switch <your-branch>` and `git pull --ff-only`; preserve local work if not clean. Do not reset/overwrite teammates' changes.

**No application code exists. Author a new implementation from these requirements. Do not copy/port/read the removed prototype as a template, restore old tests/config, or reuse old results.** Use official library documentation and new synthetic fixtures. All listed source paths are future deliverables, not files already provided.

## Ownership

Own `src/troubleshoot/api/`, `agent/`, `providers/`, `contracts.py`, Python project/dependency configuration, backend startup scripts, provider/agent/API tests and shared context. Coordinate integration; do not write Member 2's executor or Member 3's UI for them.

## Ordered implementation

1. Create minimal Python package/build/test configuration from scratch. Select dependencies for actual needs; generate a fresh lock. Establish new shared schemas from PROJECT_CONTEXT section 5, plus synthetic event/action fixtures. Commit this small contract first to unblock the team.
2. Implement a local Ollama Gemma adapter with explicit capability/configuration checks, bounded requests and validated structured output. Confirm a real installed model response; do not count mock responses as inference.
3. Implement a coordinator/session state machine and loopback API for diagnosis, bounded plan, approval, cancellation, fresh verification and recovery. Match agreed contracts, protect sensitive endpoints with session authorization and origin checks, and keep model output separate from execution authority.
4. Integrate Member 2's exported registry/observation/execution helpers and Member 3's UI. First prove one read-only workflow; then one approved repair with independent postchecks. Set/document step/time budgets.
5. Add a hosted Gemma adapter using current official docs and actual account access. Explicit local/hosted choice, no fallback, backend-only key and separate prompt/image consent. Fail clearly on missing key/model/quota.
6. Publish working setup/run/test commands only after running them. Coordinate small reviewed PRs; final integrated verification includes all newly written tests and guest evidence from Member 3.

## Tests and completion

Create new tests for malformed/extra/unknown decisions, model timeout/unavailability, cloud fallback prohibition, consent, unauthorized API calls, single-use bound approval, cancellation/recovery and false verifier success. Fresh local model smoke evidence is required; hosted evidence is separate and may remain blocked honestly.

Give Members 2/3 committed schema names, sample payloads, error types and executor/provider signatures early. Own dependency changes requested by Member 2. Report what is implemented versus mocked/live-tested. No inherited compatibility layer or old backend refactor is needed.

## Prompt for your AI agent

“Read the shared fresh-build instructions and MEMBER_1.md. Work on member-1/gemma-orchestrator in owned paths only. The earlier prototype reuse permission has been withdrawn; author new code/docs from requirements, never copy or restore old implementation. Coordinate shared contracts, preserve private visibility and report fresh evidence honestly.”
