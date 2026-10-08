> Final integration update, 8 October 2026: all four members' fresh work is being
> consolidated into main. Current production is hosted Gemma API + Windows PWA,
> with real read-only inference evidence and 203 passing checks. Earlier pending
> entries below are historical planning/checkpoints, not current feature status.
> See README.md, docs/API_PWA.md and docs/evidence/hosted/api-pwa-diagnosis.json.
> The user authorized public release; no event submission/video upload is claimed.

# Attribution and open-source notices, TroubleShoot

Owner: Member 4. Created 8 October 2026. Keep updated as runtime components land.

This repository is a fresh implementation started on 8 October 2026. No source,
prompts, tests, manifests, UI or compiled output from the team's earlier prototype
has been imported. See [PROVENANCE.md](PROVENANCE.md) for repository history.

---

## Application license

The project application code is released under the **MIT License**. See
[LICENSE](../LICENSE).

---

## Third-party runtime components

The table below lists every third-party component in use at the time of writing.
Members 1-3 must append rows as runtime dependencies are added and manifests
are created.

| Component | Version / tag | License | Role | Status |
|---|---|---|---|---|
| Python | ≥ 3.11 (system) | PSF-2.0 | Runtime language | Installed, used for contracts/tests |
| setuptools | ≥ 68 (pip cache) | MIT | Build backend | In `pyproject.toml` |
| Gemma 4 (local, Ollama) | `gemma4:e2b` | Gemma Terms of Use | Local inference provider | Adapter and recorded evaluations; not production default |
| Gemma via Google AI API | `gemma-4-26b-a4b-it` | Gemma Terms of Use | Hosted inference provider (opt-in) | Current production provider; real read-only diagnosis recorded |
| Ollama | 0.40.1 in recorded local evaluations | MIT | Local model runtime | Used for local evaluations |
| FastAPI | 0.142.4 | MIT | Backend API server | Implemented |
| Uvicorn | 0.54.0 | BSD-3-Clause | ASGI server | Runtime dependency |
| HTTPX | 0.28.1 | BSD-3-Clause | HTTP transport | Runtime dependency |
| React / React DOM | See `web/package-lock.json` | MIT | Website UI | Implemented |
| TypeScript | See `web/package-lock.json` | Apache-2.0 | Website type checking | Build dependency |
| Vite | See `web/package-lock.json` | MIT | Website bundler | Build dependency |
| Space Grotesk / DM Mono | See bundled font notices | SIL OFL-1.1 | Website and console fonts | Self-hosted |
| VirtualBox | Existing install, version TBD | GPLv2 | Windows guest VM | Member 1 infrastructure only |

> **Note:** Model weights carry their own license terms separate from the MIT
> application license. Gemma weights require acceptance of the
> [Gemma Terms of Use](https://ai.google.dev/gemma/terms).
> Windows ISO/VM installation media retains Microsoft's license; it is not
> included in this repository.

---

## Documentation references

| Resource | URL | Role |
|---|---|---|
| Hackathon template (BIJJUDAMA) | https://github.com/BIJJUDAMA/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club | Documentation structure guide; no application code imported |
| Hosted Gemma API docs | https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api | Reference for Member 3 hosted-provider implementation |
| MLH event page | https://events.mlh.com/events/15020-hacktoberfest-hack-day-coimbatore-x-init-club-idea-club | Hackathon event information |

---

## AI tool usage disclosure

| Tool / model | Used by | Purpose |
|---|---|---|
| AI coding assistants | All members (as permitted) | Fresh code authorship, planning assistance, documentation drafting |
| Gemma 4 (local Ollama) | Members 1 & 2 | Local reasoning and recorded evaluations |
| Gemma via Google AI API | Member 3 / integrated runtime | Hosted diagnosis with per-run cloud consent |

AI-assisted implementation is disclosed here; commit history records authorship.
No earlier prototype model output, prompts or inference results are re-used.

---

## Dataset notice

No dataset is used by this project. No model has been fine-tuned.

---

## Pending items

- [ ] Confirm model-license acceptance in the runtime environment.
- [ ] Member 1: Record VirtualBox version and Windows guest edition.
- [ ] Member 4: Update this file as each component is confirmed working.
