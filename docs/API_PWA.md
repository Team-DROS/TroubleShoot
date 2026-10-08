# Hosted Gemma Windows PWA

## Windows setup

Requires Python 3.11+, internet and a Google AI Studio account with Gemma access/quota.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock -e .
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/configure-api.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-api-pwa.ps1
```

The masked setup dialog saves a DPAPI CurrentUser-encrypted key outside Git:
`%LOCALAPPDATA%/TroubleShoot/api-key.dpapi`. Never share or commit it. The backend
also accepts GEMMA_API_KEY from its environment. Default model is gemma-4-26b-a4b-it;
GEMMA_API_MODEL can select gemma-4-31b-it. No local or fixture fallback is enabled.

The launcher opens the console on http://127.0.0.1:8765 with a temporary local
session token in a URL fragment. The page removes the fragment immediately and
keeps the token in memory. Reopening an installed app requires the launcher or a
fresh manual session connection. Select system diagnostics, describe the complaint,
check cloud consent and start. Images are disabled in this prototype.

Chrome/Edge may offer Install through their menu; an in-page button appears when
the browser exposes beforeinstallprompt. Manifest, 192/512 PNG icons and a public-shell-only caching
service worker are included. Only static app files are cached; diagnostic data and secrets are never cached.
The shell can open offline, but offline troubleshooting is unavailable. Keep the helper running. A PWA cannot repair Windows
without that helper. The separate web/ React landing preview is not the operator UI.

## Demo scope and limits

- Fresh read-only Windows diagnosis using real hosted Gemma, visible run timeline.
- Stop an active run; action-specific reject/approval when a mutation is proposed.
- Install/open the PWA on a supported browser, subject to live install validation.
- Optional Spooler start only in a disposable guest with verified recovery and human
  elevation. Never stop the host service to stage a demo.

Spooler Running proves service state only, not a successful print. Production desktop
changes stay disabled. Full hosted guest repair, hosted vision and live browser
installation remain pending. No old prototype results are claimed for this build.

## Validation on 8 October 2026

Real hosted Gemma connection-only inference passed. A single exact JSON Markdown
fence is accepted; surrounding prose and malformed/schema-invalid output are rejected.
Thought parts are discarded. 156 unit tests, 42 API/runtime tests and 5 synthetic
console UI tests passed. Live helper returns 200 for console/manifest/worker/icons and
401 for unauthenticated API status. Fresh host read-only Spooler check returned Running.
Repository visibility verified PRIVATE. No host mutation or service fault performed.
Browser automation failed to initialize; visual/install verification is not claimed.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests/unit -q
.\.venv\Scripts\python.exe -m unittest discover -s tests/api -q
node --test tests/e2e/console/app.test.cjs
```


## Real read-only integration evidence

The user explicitly approved cloud text for a read-only run. Fresh Windows facts,
a real Gemma API proposal and the authenticated API/session completed through
TestClient. Gemma reported Spooler Running and correctly warned that this does not
prove printing. action:null; verdict unresolved; recovery none. No mutation.
See docs/evidence/hosted/api-pwa-diagnosis.json. This is a real inference/native
integration check, not browser-click evidence. Earlier attempts safely returned
hosted_timeout and policy_rejected before the model-facing corrections. Minimal
thinking and a bounded 60-second transport timeout are now used. Model-facing
operation descriptions/schemas and exact observation field paths are supplied;
diagnosis excludes mutating choices before inference.

Validated implementation commit: `71aefb76fccfd21cbc405bb27a820098e2de7f06`.
Official Gemma thinking options: https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api


## PWA usability and provider recovery update

Printing/system diagnosis shortcuts, readable fact summaries, expandable evidence,
visible Gemma explanation, offline guidance and renewed per-run cloud consent are
implemented. The public app shell can open offline; inference still requires internet
and the Windows helper. API responses and credentials are never cached.
Temporary HTTP 502/503/504 inference failures get one cancellable retry; authentication
and quota failures do not. Errors now distinguish connection failures and busy/gateway
responses. The reported hosted_unavailable failure could not be reproduced: a fresh
key check returned HTTP 200, and a fresh real read-only diagnosis completed successfully.
Eleven hosted-provider tests and seven synthetic console UI tests passed for this update.
These checks do not prove live installation or a successful print.


## Hosted website and matching PWA

The product website is https://troubleshoot-one.vercel.app/. The landing page now
includes Windows helper setup and an Open running helper link to port 8765. The PWA
links back to the website and uses its dark/lime palette, Space Grotesk and DM Mono
fonts. Fonts are self-hosted with their license text in the console package.

This is a website-to-local-app handoff, not remote control from the Vercel page.
The existing same-origin/session protections remain. Run start-api-pwa.ps1 to open
an authenticated tab; opening another tab directly may need a local session token.
Custom ports use the URL opened by the launcher. No API key is sent to the website.

Fresh Edge browser validation passed: PWA loads without JavaScript errors, matching
font renders, public website link is correct, and cached shell reloads offline with
an offline notice. Mobile layouts have no horizontal overflow at 390px. The built
landing page exposes correct helper/setup links. Frontend production build, 10 React
fixture checks, 7 console fixture checks and 42 API/runtime checks passed. Actual
browser installation remains pending. Hosted deployment depends on Vercel's configured
production branch; source changes alone are not proof of a completed deployment.


## Launcher port conflicts

The automatic launcher reserves a loopback socket before generating a session.
If the requested port is occupied or reserved, it chooses an available port within
the next 20 ports and reports the selected URL. The browser opens only after the
server starts successfully, using that server's session token. Existing processes
are not stopped or trusted. Explicit CLI --port without --open fails cleanly on
collision. Three focused launcher checks and 42 API/runtime checks passed.
