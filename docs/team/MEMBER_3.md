# Member 3 — New interface and VM validation

**Branch:** `member-3/ui-vm-validation`. **Resources/workload:** VirtualBox owner; approximately 30% workload. No mandatory second model download.

Read AGENTS.md, PROJECT_CONTEXT.md, docs/RESTART.md, HACKATHON_AGENT_RULES.md and docs/PROVENANCE.md first. Update your assigned branch with `git fetch origin`, `git switch <your-branch>` and `git pull --ff-only`; preserve local work if not clean. Do not reset/overwrite teammates' changes.

**No application code exists. Author a new implementation from these requirements. Do not copy/port/read the removed prototype as a template, restore old tests/config, or reuse old results.** Use official library documentation and new synthetic fixtures. Read docs/CONTRACTS.md: the initial shared contract module and synthetic fixtures are provided. Other runtime paths are your fresh implementation deliverables.

## Ownership

Own new `web/`, `tests/e2e/`, docs/VM_STATUS.md, docs/VALIDATION.md and sanitized docs/evidence. Keep interface scope small to leave time for VM validation. Member 1 owns API/provider wiring, Member 2 owns Windows control.

## Ordered implementation

1. Create a fresh minimal frontend and its own manifest/lock. A basic complaint form, run status/timeline and result panel are enough initially. No copied UI/CSS/assets/build output. Work against new synthetic fixtures until Member 1 supplies the agreed contract; label simulations.
2. Integrate actual API/SSE; add diagnose/repair mode, selected target, provider/model visibility, explicit vision/cloud consent, action approval, Stop and recovery state. Show partial/unresolved outcomes honestly and no keys/raw base64.
3. Inspect the existing Windows VM as environment infrastructure. Use a clean OS/tools snapshot, excluding the old project installation/data/scripts. Check Windows desktop, disk/RAM/dependencies and snapshot/recovery before faults. Do not duplicate ISO/VDI or blindly rerun old setup.
4. Agree inference transport with Member 1. Host/hosted inference is not guest-local/offline; a network fault can disconnect it. Do not disable the only inference link without a recovery arrangement. Run the new desktop executor inside the guest.
5. Validate healthy real-model diagnosis, one safe guest action with fresh postchecks, denial/cancellation and Member 2's computer-use scenario. Restore between deliberate faults. No host repair as a substitute.
6. Write evidence with actual revision/time/model/provider/OS/snapshot, before symptom, approval, action, postcondition/recovery and limitations. Provide Member 4 only supported claims/demo steps.

## Tests and completion

Create fresh frontend build checks and integration tests for API/SSE errors, token expiry, cancellation, provider failure and unresolved results. Run the new backend suite after integration. A service-running check proves service recovery only; fixture GUI control proves fixture control only.

If VM resources/snapshot are inadequate, report live repair blocked and continue UI/read-only work. Do not consume the whole event rebuilding a VM or downloading a redundant model. Deliver a working fresh UI and honest evidence; never reuse the removed project's tests or footage.

## Prompt for your AI agent

“Read the shared fresh-build instructions and MEMBER_3.md. Work on member-3/ui-vm-validation in owned paths only. The earlier prototype reuse permission has been withdrawn; author new code/docs from requirements, never copy or restore old implementation. Coordinate shared contracts, preserve private visibility and report fresh evidence honestly.”
