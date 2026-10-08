# Member 3 validation, 8 October 2026

Branch: `member-3/backend-hosted-api`. Tested implementation revision:
`36a0322`, followed by the recovery-retention regression fix (see branch history). Environment: Windows,
Python 3.14.3, Node.js 24.18.0. Validation occurred approximately 11:40–11:52 IST.

## Automated evidence

`scripts/test.ps1` passed:

- 23 contract/hosted tests (including the 16 existing shared-contract tests).
- 29 API/session tests.
- 5 Node UI behavior tests with synthetic DOM and transport.

Total: **52 Python tests + 5 JavaScript tests**. No hosted credentials, local model
or real Windows executor were used. All new executor/provider fixtures explicitly
label their output synthetic.

Coverage includes unauthorized access, Host/Origin rejection, SSE completion and
cursor replay, malformed requests, explicit hosted consent, missing credentials,
quota/unavailable-model/timeout/malformed response failures, separate image
consent, approval mismatch/replay/expiry/tampering, wrong or stale target checks,
diagnose-only mutation prevention, cancellation, budgets, malicious unregistered
operations, pending recovery, and partial/unresolved outcome display.

`pip check` passed. `pip wheel --no-deps .` built the application wheel, which
installed in the fresh project environment. Its `troubleshoot --help` entry point
ran. The dependency resolution emits a TestClient deprecation warning; it did
not fail tests.

## Browser smoke evidence

At approximately 11:49 IST, the real launcher on loopback port 8765 rendered the
UI and accepted its session token. Local mode displayed unavailable; selecting
hosted mode showed `gemma-4-26b-a4b-it` unavailable without a configured key.
Start remained disabled. No inference was attempted.

The separately launched `tests/e2e/web/serve_fixture.py` on port 8766 authenticated
successfully. The browser displayed **SYNTHETIC FIXTURE; no real repair**. Selecting
its synthetic target and submitting a synthetic complaint streamed observation,
plan and complete events. The result was **unresolved (synthetic fixture)**,
recovery **none**, and "Diagnosis only; no symptom postcondition was measured."
The measured synthetic event timestamp was `2026-10-08T06:18:59.311367+00:00`
(11:48:59 IST). No real Windows target was captured or changed.

## Pending evidence and integration

Real hosted text and image inference, actual account model access/quota, Member
2's local provider/protocol, Member 1's executor/recovery and guest validation,
selected-window capture and real symptom restoration are **not verified**.
These tests do not establish event eligibility, model quality or live repair.
No third-party account credentials, screenshots of unrelated windows or private
logs are included in this evidence.
