# Member 3 validation, 8 October 2026

## Mouse registry follow-up

The reported mouse registry/dispatcher gap is already excluded by `bc13ea7`:
only inspection and explicitly verified checkbox integration can enter the
desktop runtime registry. No `mouse_*` operation is offered, even with the
programmatic checkbox verifier enabled; the environment flag cannot enable it.
Added a regression covering all five owner mouse operations, checking registry
and status omission, dispatch rejection before authorization, zero input and no
recovery records. No owner files or native runtime behavior changed.

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python -m unittest discover -s tests/api -q
# PASS: 42 tests, 9.831 s on Windows
```

Current suite total: **196 Python + 5 web tests** (154 unchanged unit tests,
42 API tests, 5 unchanged web tests). The mutation/approval regression uses
synthetic fixtures. Earlier complete-suite commands/results remain below.

## Latest owner integration, 13:30 IST onwards

Fetched all branch refs explicitly because the single-branch clone's default
fetch only updates Member 3. Merged Member 2 `6ed184b` in `4cdfda3` and Member 1
`3edf350` in `d796ad9`. No rebase, force push, or owner source/test edits.
The following results apply to these merges plus the Member 3 changes committed
with this report. Earlier sections describe earlier revisions.

```powershell
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
git merge --no-edit origin/member-2/local-gemma-agent
git merge --no-edit origin/member-1/windows-desktop-vm
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python -m unittest discover -s tests/unit -q
# PASS: 154 tests, 5.978 s, Windows; includes both owner PowerShell tests
.\.venv\Scripts\python -m unittest discover -s tests/api -q
# PASS: 41 tests, final run 9.107 s
node --test tests/e2e/web/app.test.cjs
# PASS: 5 tests; synthetic DOM/transport
.\.venv\Scripts\python scripts/check_integrated_readonly.py
# PASS: real native read-only workers + SYNTHETIC provider, no errors,
# observation/plan/observation/action/verification/complete; partial, recovery none
.\.venv\Scripts\python -m pip wheel --no-deps . --wheel-dir .venv/wheels
# PASS: application wheel built
.\.venv\Scripts\python -m pip check
# PASS: No broken requirements found
git diff --check
# PASS: no whitespace errors
.\.venv\Scripts\python -c "import zipfile; from pathlib import Path; names=zipfile.ZipFile(next(Path('.venv/wheels').glob('troubleshoot_agent-0.1.0-*.whl'))).namelist(); required=['troubleshoot/runtime/persistent-worker.ps1','troubleshoot/desktop/mouse-native.ps1','troubleshoot/desktop/worker.ps1','troubleshoot/windows/diagnostics.ps1']; assert all(n in names for n in required); print('PASS: four fixed PowerShell scripts packaged')"
# PASS: all four fixed scripts packaged
.\.venv\Scripts\python -m pip install --force-reinstall --no-deps .venv/wheels/troubleshoot_agent-0.1.0-py3-none-any.whl
# PASS: installed
$env:PYTHONPATH=$null
.\.venv\Scripts\python -m troubleshoot.api --help
# PASS: installed API entry point
```

Total **195 Python + 5 web tests**. This machine runs Windows with Python 3.14.3
and Node 24.18.0. Member 1's Windows-only tests passed here; that is not evidence
that they run on Linux. New API checks include actual read-only worker reuse,
worker policy failure followed by an explicit separate request, bounded timeout
without retry, unregistered commands, refusing desktop environment opt-in without
a symptom verifier, and synthetic CheckboxRecovery journal/approval/startup blocks.
The usual TestClient deprecation warning remains non-failing.

Exact additional read-only timing command:

```powershell
$env:PYTHONPATH='src'
@'
import json, time
from troubleshoot.runtime.powershell_worker import PersistentPowerShellWorker
worker=PersistentPowerShellWorker()
try:
    elapsed=[]
    pids=[]
    for i in range(3):
        started=time.monotonic()
        worker.run('diagnostics','spooler_status',{})
        elapsed.append(round(time.monotonic()-started,4))
        pids.append(worker.process.pid)
    print(json.dumps({'label':'ACTUAL Windows read-only service checks','seconds':elapsed,'same_process':len(set(pids))==1}))
finally:
    worker.close()
'@ | ./.venv/Scripts/python -
```

Result: `[0.4014, 0.0086, 0.0042]` seconds, same process true. No service state
changed, private facts logged, desktop input or capture performed. Host measurements
do not prove guest latency. The persistent transport invokes fixed unchanged owner
scripts, caches types/runspace, serializes calls and discards failures/timeouts
without automatic action retry. Freshness remains five seconds. Repair directory
permissions are prepared before starting the run, rather than consuming approval
freshness with ACL setup.

The launcher keeps all desktop changes disabled regardless of the environment
switch. Programmatic verifier injection can enable only the checkbox wrapper;
durable baseline and a new restoration approval remain required. No real symptom
verifier/recovery API exists, so mouse/close/capture are not model-facing runtime
operations. The new mouse schemas are merged unchanged into Member 2's adapter.

Owner evidence imported unchanged: Member 1's real Gemma guest checkbox harness
passed using a synthetic UI, with state verification/restoration, but no API token
flow or original symptom proof. Its live vision result was unknown and safely
blocked; print probe lacked a printer and could not prove printing. Member 2's
real model/session re-check uses simulated execution. On this PC local Gemma remains
unavailable; no fixture or hosted fallback occurred. Combined live API/UI guest
flow and guest persistent-worker timing remain pending, as does hosted inference.

Member 4's exact setup and evidence handoff is `docs/MEMBER_3_HANDOFF.md`.
The local README draft is excluded from commits/pushes. Repository remains private;
one PR into main is prepared for team review, not automatic merge.

## Integration update, approximately 12:45-12:56 IST

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
Python 3.14.3, Node.js 24.18.0. Validation occurred approximately 11:40-11:52 IST.

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
