# Fresh-build instructions for every team coding agent

Read PROJECT_CONTEXT.md, HACKATHON_AGENT_RULES.md, docs/PROVENANCE.md, docs/RESTART.md and your docs/team/MEMBER_N.md before work.

- The user's latest instruction says organizers withdrew code-reuse permission. It supersedes every older permission statement. Build a new implementation from the requirements in these planning documents.
- Do not copy, translate, port, cherry-pick, recover or use the old prototype as an implementation template. This includes source, prompts, tests, manifests/locks, scripts, UI, compiled output, recordings and old results. Do not ask another agent to do that for you. Do not inspect historical implementation to recreate it. General problem knowledge and new planning are not working code.
- Current tree includes Windows tools, local and hosted Gemma providers, an authenticated API, PWA console and React website. Read README.md and docs/API_PWA.md for current enabled scope. Verify each changed feature and label simulation clearly; historical checks do not prove current live repairs.
- This repository is a separate fresh implementation. Disclose prior team prototype work accurately; do not rewrite/backdate history or fabricate contributions. Do not guarantee event eligibility; organizer interpretation still governs.
- Work on your assigned branch and owned files. Member 3 owns API/shared contracts/integration and packaging; Member 2 owns local provider/protocol/reasoning; Member 1 owns Windows/desktop/VM; Member 4 owns documentation. Use new `src/troubleshoot/` and `web/` paths. No force push or silent cross-member overwrites.
- Existing third-party runtimes/caches/model weights and clean VM infrastructure may be reused as permitted environment preparation. Create new dependency manifests from actual new needs. No linking/copying old application files or build output into the new runtime.
- Keep repository private until user explicitly requests public visibility. No external submission, message or upload without authorization.
- Model output proposes actions; deterministic executor policy validates them. No arbitrary shell/model code or command execution through desktop typing. Use action-specific approvals and human UAC.
- Local mode is default. Hosted mode and image transfer require explicit consent; no hidden fallback. Keys remain server-side. Exclude private logs/screenshots, model and VM images from Git.
- Fresh observations, target identity/freshness checks, cancellation, bounded execution, symptom verification and recovery are required. Test intentional faults only in a disposable guest with recovery available, never on the host.
- Supplied deadline: 16:30 IST on 8 October 2026. Honor confirmed organizer amendments and stop competition changes at the deadline absent an extension.

- Actual hardware: Member 1 local Gemma + VM; Member 2 local Gemma only; Members 3/4 neither. Member 3 uses explicit test fixtures or hosted Gemma for API development; never silently ship mock inference. The final runtime remains local-first.
- Member 4 considers the user-supplied hackathon template via docs/TEMPLATE_GUIDE.md. Keep README aligned with actual code, attribution, setup and event-time work; avoid organizer-only details and invented metrics. Template links/fields do not authorize release/submission.

## Latest authorized integration override
The user authorized one agent to finish across all member paths on integration/api-pwa.
The current prototype is hosted Gemma API only with a loopback Windows helper and
installable PWA. Earlier local-first requirements describe the previous scope.
Keep explicit cloud consent, server-side keys, approvals, human UAC, fresh checks,
private repository and the prohibition on old prototype reuse.


## Latest publication instruction
The user explicitly authorized merging all fresh team work into main and making
this repository public. This supersedes earlier private-until-instructed language.
Keep secrets, raw private evidence and machine-local data excluded from Git.
