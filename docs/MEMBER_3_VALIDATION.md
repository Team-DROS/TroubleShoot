# Member 3 validation, 8 October 2026

## Integration update — approximately 12:45–12:56 IST

Member 3 merged Member 2 `41b1c9b` (merge `5ff128b`) and Member 1 `7623bc7`
(merge `f1f9321`) without rebasing or changing their owned implementation/tests.
The following results apply to that tree plus the integration changes committed
alongside this evidence. The earlier standalone results below remain historical.

### Exact commands and results

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python -m unittest discover -s tests/unit -q
# PASS: 125 tests, 6.060 s
.\.venv\Scripts\python -m unittest discover -s tests/api -q
# PASS: 35 tests, 7.116 s
node --test tests/e2e/web/app.test.cjs
# PASS: 5 tests, 0 failures
.\.venv\Scripts\python -m pip check
# PASS: No broken requirements found
.\.venv\Scripts\python scripts/check_integrated_readonly.py
# PASS: actual native read-only workers, synthetic provider; no mutation
.\.venv\Scripts\python -m pip wheel --no-deps . --wheel-dir .venv/wheels
# PASS: troubleshoot_agent-0.1.0-py3-none-any.whl built
.\.venv\Scripts\python -c "import zipfile; from pathlib import Path; wheel=next(Path('.venv/wheels').glob('troubleshoot_agent-0.1.0-*.whl')); names=zipfile.ZipFile(wheel).namelist(); required=['troubleshoot/windows/diagnostics.ps1','troubleshoot/desktop/worker.ps1','troubleshoot/providers/base.py','troubleshoot/providers/ollama.py','troubleshoot/agent/runtime_adapter.py','troubleshoot/runtime/native.py']; assert all(n in names for n in required); print('PASS: wheel includes all native workers and local provider/runtime adapters')"
# PASS: both PowerShell workers and integration/provider modules included
.\.venv\Scripts\python -m pip install --force-reinstall --no-deps .venv/wheels/troubleshoot_agent-0.1.0-py3-none-any.whl
# PASS: installed successfully
$env:PYTHONPATH = $null
.\.venv\Scripts\troubleshoot.exe --help
# PASS: installed entry point/imports work
```

Total: **160 Python tests + 5 JavaScript tests**. Test workers/model replies are
synthetic unless explicitly described below. Tests perform no live host mutation.
The existing non-failing TestClient deprecation warning remains.

New integration coverage includes a real 5.1-second **synthetic** inference delay
crossing the original freshness boundary, three runtime observations per action,
exact native fingerprint approval before mutation, rejection, cancellation,
startup recovery blockers, and excluding restoration/unconsented capture from
model actions. The native bridge tests use unchanged Member 1 executor classes
with a synthetic worker; they do not start or stop an actual service.

### Live and simulated evidence

`scripts/check_integrated_readonly.py` queried the configured local model and
reported `gemma4:e2b` **unavailable** on this PC. No model was installed or downloaded,
and no fallback was attempted.

The script then used an explicitly synthetic read-only proposal with **actual
Windows PowerShell workers** through SessionManager. It produced:

```json
{"events":["observation","plan","observation","action","verification","complete"],"errors":[],"verdict":"partial","recovery":"none","simulation":true}
```

It collected real read-only system/service facts and a fresh service postcheck.
No fault was injected, service changed, desktop input sent, screenshot captured,
or raw private system/window evidence logged. The original symptom is not verified;
partial is a limited service-state result, not restored printing.

Member 2's imported [integration report](evidence/local-model/INTEGRATION_MEMBER3.md)
records real CPU Gemma inference through the prior runtime with a simulated
executor: 36.7-second inference exposed the stale observation failure, and a
35.8-second run with the proposed patch reached approval/action/checks. This is
Member 2's evidence, not a new live model test on Member 3's PC.

Member 1's imported guest evidence records native service restoration and desktop
fixture checks without an AI/API integration. Those results remain distinct from
this combined bridge's tests. A complete real Gemma → API approval → native guest
repair → symptom verification run is still pending on a teammate's model/VM setup.

### Current policy and limits

Member 2's rebind-after-inference patch was applied with whitespace tolerance for
this checkout's CRLF files. It compares identity/bounds/DPI and binds to newly
observed evidence; it does not loosen native validation. The second freshness gap
uses the permitted documented-limit option: UI approval must finish within the
bound observation's five-second limit, and native token expiry uses the remaining
interval. Changed/expired targets require a new run; no silent post-approval rebind.

The local adapter, native executors and worker package data are wired at startup.
Pending durable recovery records block repairs after restart; exact native state
fingerprints are approved once. No restoration operation is model-facing.
Desktop mutation needs explicit recovery-scenario opt-in; capture/vision and a
symptom-specific verifier remain pending. Hosted inference still lacks credentials.
The existing local README draft was excluded from all integration commits.

## Earlier standalone validation

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
