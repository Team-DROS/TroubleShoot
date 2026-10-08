# Member 2 — Windows tools and computer use

**Branch:** `member-2/windows-computer-use`. **Resources/workload:** Gemma PC B; approximately 30% workload.

Read AGENTS.md, PROJECT_CONTEXT.md, docs/RESTART.md, HACKATHON_AGENT_RULES.md and docs/PROVENANCE.md first. Update your assigned branch with `git fetch origin`, `git switch <your-branch>` and `git pull --ff-only`; preserve local work if not clean. Do not reset/overwrite teammates' changes.

**No application code exists. Author a new implementation from these requirements. Do not copy/port/read the removed prototype as a template, restore old tests/config, or reuse old results.** Use official library documentation and new synthetic fixtures. All listed source paths are future deliverables, not files already provided.

## Ownership

Own new `src/troubleshoot/windows/`, `src/troubleshoot/desktop/` and corresponding new unit tests. Member 1 owns provider/API/schema/dependency lock; Member 3 owns guest execution and UI. Propose dependency needs to Member 1.

## Ordered implementation

1. Create a fresh registered operation interface: typed arguments, risk/approval requirement, target, timeout, execution result and postcondition. Start with one useful read-only Windows diagnostic. Use fixed operations, never arbitrary model shell.
2. Independently build target enumeration/identity and selected-window observation with capture consent, timestamp/observation ID, handle/PID/start time, geometry/DPI and controls. Keep image references opaque and private; no raw image logging.
3. Build one allowlisted desktop input at a time, preferring accessibility controls. Revalidate foreground, target and freshness immediately before input. Block terminals/Run dialog, credentials, privilege prompts and unrelated apps; reject bounds/identity changes.
4. Through Member 1's provider interface, connect a fresh image observation to Gemma's structured action proposal. Do not build a second provider client or assume image support; measure it.
5. Create new synthetic fixtures and tests, then coordinate one disposable guest UI workflow with Member 3. Add one real reversible troubleshooting action only after defining pre-state, approval, expected symptom change and recovery. A fixture app is not proof of Windows repair.
6. Capture new facts after each step, enforce short action budgets/cancellation, and stop on ambiguity. Do not expand to universal arbitrary desktop control during the event.

## Tests and completion

New tests: stale/wrong/reused window identity; foreground/geometry/DPI change; out-of-bounds click; protected field/target; unknown action/extra args; screenshot prompt injection; worker timeout; approval denial/cancel; execution success with failed symptom check. Never fault the development host.

Deliver actual helper signatures, operation list, dependencies/timeouts and test results to Member 1; give Member 3 a fresh guest scenario with restoration steps. Success means a measured observation → validated input → fresh postcondition workflow. Report separately if only accessibility or only image interpretation works.

## Prompt for your AI agent

“Read the shared fresh-build instructions and MEMBER_2.md. Work on member-2/windows-computer-use in owned paths only. The earlier prototype reuse permission has been withdrawn; author new code/docs from requirements, never copy or restore old implementation. Coordinate shared contracts, preserve private visibility and report fresh evidence honestly.”
