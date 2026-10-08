# Member 3, Backend API, hosted Gemma and minimal interface

**Branch:** `member-3/backend-hosted-api`. **Hardware/workload:** No local Gemma or VM required. Hosted credentials, if available, enable real API smoke tests.

Read AGENTS.md, PROJECT_CONTEXT.md, docs/CONTRACTS.md and HACKATHON_AGENT_RULES.md first. Preserve local changes before updating your branch. Existing shared-contract code and synthetic fixtures are newly authored and may be used; the earlier standalone prototype must not be copied or restored.

No running model adapter, API, UI or Windows executor exists yet. Every runtime feature below is work to implement and validate. Keep the repository private until explicit user instruction.
## Ownership

Own `src/troubleshoot/api/`, `src/troubleshoot/runtime/`, `src/troubleshoot/providers/gemma_api.py`, `src/troubleshoot/contracts.py`, `tests/api/`, `tests/unit/test_provider_hosted*`, `tests/unit/test_contracts.py`, `web/`, `tests/e2e/web/`, Python packaging/config/lock, startup scripts and shared project/contract documentation. You coordinate integration. Member 2 owns the provider protocol/local reasoning; Member 1 owns Windows/VM operations.

## Work without local Gemma

Use injected synthetic provider/executor fixtures for API and UI tests; expose them only as clearly labeled development/test fixtures. Production must never silently return mock AI or pretend a hosted/local model is reachable. An API key is not assumed: implement/test error handling without one, then run a real hosted smoke check only when credentials/account access are available.

## Ordered work

1. Complete the existing shared schemas with Members 1/2: observation geometry, provider protocol agreement, approval/result/verdict/error/event payloads. Preserve working contract tests and publish samples. Select fresh dependencies for actual needs and centralize Python lock updates.
2. Implement a loopback API and runtime session state machine: status, run creation, events, bound single-use approval, cancellation and recovery. Use authenticated local session access and origin checks for sensitive controls/screenshots. Do not expose native control on all network interfaces.
3. Implement hosted Gemma in `providers/gemma_api.py` against Member 2's protocol using current official documentation and actual account availability. Keep keys backend-only. Handle missing key, unavailable model, quota, timeout and malformed decisions. Hosted text and image transfer require explicit separate consent.
4. Integrate Member 2's local adapter/coordinator and Member 1's executor through dependency injection. The shipped default remains local-first; explicit hosted mode is optional. Starting API/tests on your own PC must not require Ollama or a Windows guest. Missing production provider is reported as unavailable, not silently swapped.
5. Create a small `web/` interface: complaint, mode/provider/model, target selection, vision/cloud consent, timeline, specific approval, Stop and truthful verdict/recovery. Keep it minimal; no elaborate UI redesign. Match actual API contracts, and keep credentials out of frontend code.
6. Publish runnable setup/test commands once verified. Coordinate small integrations and help Member 1 run the new app in the guest. Provide Member 4 exact endpoint/model/provider/setup facts and limitations.

## Acceptance and tests

API/session tests cover unauthorized access, expired/replayed/mismatched approval, cancellation, pending recovery, model/tool errors, diagnose-only mutation prevention and no cloud/mock fallback. Hosted tests cover credentials, consent, malformed results and image capability. UI checks cover SSE errors, unavailable provider and partial/unresolved display.

Real hosted inference is pending until a key and supported Gemma model are available. You can complete core API/UI integration with synthetic test fixtures independently; Member 2 verifies local inference and Member 1 verifies guest/native behavior. Do not claim your tests prove real Windows execution.

## Handoffs

Freeze endpoint/event samples early. Member 2 implements local reasoning against those shapes; Member 1 supplies operation validators/execution/recovery. Merge reviewed changes under team authorization, run fresh integrated checks and keep the repository private.

## Prompt for your AI agent

“Read AGENTS.md, PROJECT_CONTEXT.md, docs/CONTRACTS.md and MEMBER_3.md. Work on member-3/backend-hosted-api in my owned paths. Follow the revised hardware split; author fresh implementation/docs, coordinate with Member 3 on API/contracts and Member 2 on provider protocol. Keep the project local-first, preserve bounded Windows/computer-use and fresh verification, keep repository private and report actual evidence.”
