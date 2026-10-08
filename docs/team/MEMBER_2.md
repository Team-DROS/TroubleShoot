# Member 2 — Local Gemma and agent reasoning

**Branch:** `member-2/local-gemma-agent`. **Hardware/workload:** Local Gemma 4; no VM required.

Read AGENTS.md, PROJECT_CONTEXT.md, docs/CONTRACTS.md and HACKATHON_AGENT_RULES.md first. Preserve local changes before updating your branch. Existing shared-contract code and synthetic fixtures are newly authored and may be used; the earlier standalone prototype must not be copied or restored.

No running model adapter, API, UI or Windows executor exists yet. Every runtime feature below is work to implement and validate. Keep the repository private until explicit user instruction.
## Ownership

Own `src/troubleshoot/providers/base.py`, `src/troubleshoot/providers/ollama.py`, `src/troubleshoot/agent/`, `tests/unit/test_provider_local*`, `tests/unit/test_agent*`, `docs/LOCAL_GEMMA.md` and sanitized `docs/evidence/local-model/`. Member 1 owns native actions/VM; Member 3 owns hosted provider/API/runtime/contracts/packaging. Do not independently edit their files.

## Ordered work

1. Inspect actual installed Gemma tags and the local runtime without downloading duplicates. Measure a real text response and record exact model/runtime/settings. Do not assume every selected tag supports usable vision.
2. Define a small provider protocol in `providers/base.py` jointly with Member 3: typed inputs/normalized decision, declared text/image capability, bounded errors and no executable fallback text. Local and hosted adapters implement it; only you edit the shared protocol file.
3. Implement Ollama transport in `providers/ollama.py`: bounded requests, strict structured decisions, explicit unavailable/malformed/timeout errors, and no silent hosted fallback. Configuration/status must distinguish configured from actually responding.
4. Build Think/Act/Verify coordination as fresh code. The model selects registered diagnostic/action proposals; the runtime approval gate and native executor remain independently authoritative. Verification uses new symptom facts, not a second model agreeing.
5. Add opt-in image input through the provider protocol. Measure actual Gemma screenshot-to-action behavior with Member 1's synthetic then guest observations; never claim captioning alone is vision-guided repair. UI/screenshot instructions cannot expand permissions.
6. Integrate your coordinator into Member 3's runtime/API and Member 1's tool interface. Help prove the local-first vertical slice on a Gemma machine and joint live VM scenarios. Publish setup and evidence for actual local inference.

## Acceptance and tests

Create new tests for malformed/extra/unknown decisions, unsupported image capability, timeout/missing model, screenshot prompt injection, bounded reasoning/action loops, unsupported symptoms, no implicit cloud fallback, and false verifier success. Coordinate policy tests with Member 3 rather than implementing a competing approval/session system.

No Windows VM is needed for provider/unit development: use labeled synthetic evidence and mock executors. Real desktop/repair behavior is validated by Member 1. Unit mocks are never substituted for live inference evidence.

## Handoffs

Give Member 3 the provider protocol and coordinator hooks early so API/hosted development can proceed without local Gemma. Give Member 1 exact image/observation constraints and model outputs for a scoped guest case. Request dependency changes from Member 3. Local execution remains default for the final app regardless of your colleagues' development hardware.

## Prompt for your AI agent

“Read AGENTS.md, PROJECT_CONTEXT.md, docs/CONTRACTS.md and MEMBER_2.md. Work on member-2/local-gemma-agent in my owned paths. Follow the revised hardware split; author fresh implementation/docs, coordinate with Member 3 on API/contracts and Member 2 on provider protocol. Keep the project local-first, preserve bounded Windows/computer-use and fresh verification, keep repository private and report actual evidence.”
