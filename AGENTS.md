# Fresh-build instructions for every team coding agent

Read PROJECT_CONTEXT.md, HACKATHON_AGENT_RULES.md, docs/PROVENANCE.md, docs/RESTART.md and your docs/team/MEMBER_N.md before work.

- The user's latest instruction says organizers withdrew code-reuse permission. It supersedes every older permission statement. Build a new implementation from the requirements in these planning documents.
- Do not copy, translate, port, cherry-pick, recover or use the old prototype as an implementation template. This includes source, prompts, tests, manifests/locks, scripts, UI, compiled output, recordings and old results. Do not ask another agent to do that for you. Do not inspect historical implementation to recreate it. General problem knowledge and new planning are not working code.
- Current tree includes planning, a first shared-contract module and fresh contract tests; no runtime executor/model/UI is implemented. No prior tests or live-repair claims apply. Verify each newly built feature and label simulation clearly.
- This repository is a separate fresh implementation. Disclose prior team prototype work accurately; do not rewrite/backdate history or fabricate contributions. Do not guarantee event eligibility; organizer interpretation still governs.
- Work on your assigned branch and owned files. Person 1 owns shared contracts/integration. Use new `src/troubleshoot/` and `web/` paths. No force push or silent cross-member overwrites.
- Existing third-party runtimes/caches/model weights and clean VM infrastructure may be reused as permitted environment preparation. Create new dependency manifests from actual new needs. No linking/copying old application files or build output into the new runtime.
- Keep repository private until user explicitly requests public visibility. No external submission, message or upload without authorization.
- Model output proposes actions; deterministic executor policy validates them. No arbitrary shell/model code or command execution through desktop typing. Use action-specific approvals and human UAC.
- Local mode is default. Hosted mode and image transfer require explicit consent; no hidden fallback. Keys remain server-side. Exclude private logs/screenshots, model and VM images from Git.
- Fresh observations, target identity/freshness checks, cancellation, bounded execution, symptom verification and recovery are required. Test intentional faults only in a disposable guest with recovery available, never on the host.
- Supplied deadline: 16:30 IST on 8 October 2026. Honor confirmed organizer amendments and stop competition changes at the deadline absent an extension.
