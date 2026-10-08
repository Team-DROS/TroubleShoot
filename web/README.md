# TroubleShoot frontend

Original responsive landing page and interactive walkthrough on the `frontend` branch. React, TypeScript, Vite, and CSS/SVG. Created from the supplied charcoal/lime editorial design brief and this repository's product requirements.

## Run

Node 22.18+ (Node 24 recommended) and npm are required. From `web/`:

```powershell
npm ci
npm run dev
```

Open the URL printed by Vite (normally `http://127.0.0.1:5173`). If that port is occupied, use `npm run dev -- --port 5174`. Both development and preview bind to loopback only.

```powershell
npm test
npm run build
npm run preview
npm run format:check
```

The build emits `web/dist/`. Serve that directory with any static server; there is no server runtime, environment variable, or API key needed for this preview. This build assumes hosting at the origin root. Configure Vite's `base` before hosting under a subdirectory.

## Vercel deployment

Production: https://troubleshoot-one.vercel.app

Vercel project: `umasuthanpalaniappan/troubleshoot`. The frontend was deployed from the `frontend` branch with `web/` as the CLI working directory. `vercel.json` specifies Vite, `npm ci`, `npm run build`, and `dist` output. No application environment variables are needed.

To redeploy from `web/` after signing in:

```powershell
npm exec --yes --package=vercel@63.1.0 -- vercel link --yes --project troubleshoot --scope umasuthanpalaniappan
npm exec --yes --package=vercel@63.1.0 -- vercel deploy --prod --yes --scope umasuthanpalaniappan
```

This is a CLI deployment; automatic GitHub deployments are not configured. If connecting GitHub later, select repository `Team-DROS/TroubleShoot`, root directory `web`, and production branch `frontend`. Keep `.vercel/` and generated `.env*` files out of Git.

## What works

- Responsive landing page, original diagnostic-core SVG, self-hosted typography, restrained motion, FAQ, mobile navigation, and keyboard-operable workflow tabs.
- Lazy-loaded native-dialog workspace with selected scenarios, editable complaint, diagnose/repair mode, observation, action approval, denial, stop, partial/unresolved results, and sample restoration.
- JSON sample-evidence export initiated by an explicit user action.
- Input is kept in component memory. No analytics, cookies, persistent storage, third-party fonts, device access, model calls, or backend requests.

All observations and actions are **synthetic examples**. The walkthrough does not diagnose freeform text; the selected scenario determines its fixture. Printer/audio examples end with a partial outcome, and the network example remains unresolved. The sample operation names are frontend fixtures, not registered Windows capabilities or finalized API contracts.

## Where to work

- `src/App.tsx`: page content, section navigation, workflow tabs, entry into the demo.
- `src/components/Core.tsx`: original vector artwork; decorative and hidden from accessibility APIs.
- `src/components/Demo.tsx`: scenario workspace, timed presentation, export, accessible dialog.
- `src/lib/demo.ts`: isolated deterministic fixture state machine. Invalid transitions, target changes during a run, and late events after cancellation are rejected.
- `src/lib/demo.test.ts`: meaningful boundary tests using Node's test runner, without an extra test framework.
- `src/styles.css`: design tokens, desktop/mobile composition, focus states, reduced motion, forced-colors support.
- `src/fonts.css`: Latin-only WOFF2 fonts served from the same origin.

## Backend handoff

The repository does not yet expose a working control API. Keep preview mode explicit until Member 1 and Member 2 provide and verify the actual runtime. Replace the fixture transition layer with an authenticated adapter only after agreeing to `docs/CONTRACTS.md` and the implemented server schema. The demo is not an executor or authorization layer.

Live integration still needs provider/readiness discovery, real targets, `POST /api/runs`, authorized event transport, server-bound single-use approval tokens, server cancellation/recovery, model/API failure states, and fresh outcome evidence. Validate event payloads at the adapter boundary. Never infer real readiness from a configured model name or substitute fixtures for failed inference. Hosted text and image consent must be explicit before adding those modes.

## Design and performance

The supplied brief determines the charcoal, off-white, and acid-lime palette; Space Grotesk/DM Mono hierarchy; editorial section rhythm; and lightweight motion. Watermelon UI (`https://ui.watermelon.sh/home`) was inspected for interaction and composition reference. No template, reference-site code, paid assets, or prior TroubleShoot implementation was imported.

The hero is SVG/CSS, without video, raster hero assets, WebGL, or an animation library. The walkthrough loads on demand. Two local font files total about 37 KB. The initial production JavaScript is about 77 KB gzip and CSS about 9 KB gzip; the walkthrough adds about 4.4 KB gzip. These are build sizes, not a Lighthouse or real-user speed claim.

Space Grotesk and DM Mono are distributed through Fontsource under the SIL Open Font License. React is MIT-licensed. Their notices are preserved in `public/THIRD-PARTY-NOTICES.txt` and included in the production build. The project uses the repository's existing license.

## Validation — 8 October 2026

- Production build and TypeScript checks pass.
- Ten state-machine tests pass: diagnose-only, approval gating, denial, cancellation at each active stage, frozen run inputs, bounded complaint length, recovery eligibility, reset.
- Browser walkthrough checks: approved repair/partial outcome, sample restoration, audio diagnosis-only, network unresolved outcome, denial, stop, Escape, and return of focus to the opening button.
- Responsive layout checks at 320, 390, 768, 1024, and 1440 CSS pixels; 320px overflow corrected. Mobile navigation closes on selection. Arrow keys change workflow tabs. The mobile dialog and approval panel have no horizontal overflow.
- The automated browser download check was denied by browser policy. Export implementation is present, but file delivery was not verified or retried through another route.
- No native Windows, Gemma, API, VM, or actual repair behavior was exercised. This evidence applies to the frontend only.
