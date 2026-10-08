# Member 3 facts for Member 4

8 October 2026. Owner integration branch: `member-3/backend-hosted-api`.
Merged Member 2 `6ed184b` and Member 1 `3edf350` without modifying their owned files.
This handoff supports README preparation; it does not authorize publication/submission.

## Exact run commands

From the integrated checkout in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.lock
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python -m troubleshoot.api --port 8765
```

Open `http://127.0.0.1:8765`. Copy the local session token printed in the terminal
into the UI and click Connect. It is held in tab memory and sent as a Bearer
header; never put it in a URL, screenshot, README or recording. Restart generates
a new token unless `TROUBLESHOOT_SESSION_TOKEN` is deliberately set. The token
is not a hosted API key. Use literal `127.0.0.1`, not `localhost`.

Default provider: **local Ollama, `gemma4:e2b`**, URL
`http://127.0.0.1:11434`. Startup does not download weights. Set
`TROUBLESHOOT_OLLAMA_URL` and `TROUBLESHOOT_OLLAMA_MODEL` for the actual existing
runtime. Member 1's harness used port 11435; that is not the default. Non-loopback
inference requires deliberate `TROUBLESHOOT_OLLAMA_ALLOW_LAN=1` and disclosure of
where inference runs. Default decision timeout is 150 seconds via
`TROUBLESHOOT_OLLAMA_TIMEOUT`; production run budget is 300 seconds.

Select This computer for system/network/Spooler evidence, or an allowed window
for read-only inspection. The supported API binds only loopback. There is no
silent hosted or synthetic fallback. Missing Ollama/model is displayed unavailable.
Hosted mode requires explicit text consent and a backend `GEMMA_API_KEY`;
the frontend never receives that key. Hosted live inference remains untested.

## Evidence wording

- Member 3: 154 unit + 41 API tests passed on Windows, plus 5 synthetic web tests.
  Unit suite includes Member 1's two Windows-only PowerShell worker tests.
  API suite also includes actual read-only persistent worker reuse on Windows;
  all mutation/provider fixtures are synthetic. Wheel/dependency checks pass.
- Actual host read-only diagnostics passed through the session runtime with an
  explicitly synthetic proposal. Verdict partial; no host fault/input/mutation.
  Three direct service queries reused one PowerShell process (0.4014, 0.0086,
  0.0042 seconds). This is host timing, not guest proof.
- Member 2: real CPU Gemma inference through the session runtime with simulated
  execution passed after the 150-second timeout update. A resolved fixture verdict
  is not a Windows repair claim. See its integration evidence.
- Member 1: real host-local Gemma text proposal from guest accessibility facts,
  human-approved native checkbox change, state verification and restoration passed
  a developer harness using a synthetic application. No authenticated API/UI flow
  or real application symptom is proven by that harness.
- Guest mouse tests demonstrate guarded controller primitives. Production API
  does not expose mouse or close actions. Desktop repairs remain disabled even
  with the environment flag because no real symptom verifier is integrated.
- Live guest capture→Gemma vision returned unknown and blocked input. Vision is
  unavailable in API/UI. Do not call this successful vision troubleshooting.
- Guest Spooler restoration passed native testing. Original print verification
  is blocked: no printer/PDF driver installed. Running is service evidence only.

## Still pending

Combined real Gemma→authenticated API/UI approval→native guest action→original
symptom verification; guest timing with the persistent worker; usable capture and
vision integration; real hosted inference with account credentials; a real symptom
verifier and operator recovery API before enabling desktop repairs.

Approvals must complete within five-second observation freshness. Persistent
transport reduces startup overhead but never relaxes that limit. Changed or
stale targets fail closed. Pending recovery records block further repairs.

Member 4's README is owned by Member 4. The user's separate local README draft
remains uncommitted/unpushed. Keep the repository private; the integration PR must
not be merged until the team agrees.
