# Attribution and open-source notices — TroubleShoot

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
Members 1–3 must append rows as runtime dependencies are added and manifests
are created.

| Component | Version / tag | License | Role | Status |
|---|---|---|---|---|
| Python | ≥ 3.11 (system) | PSF-2.0 | Runtime language | Installed — used for contracts/tests |
| setuptools | ≥ 68 (pip cache) | MIT | Build backend | In `pyproject.toml` |
| Gemma 4 (local, Ollama) | Tag TBD by Member 1/2 | Gemma Terms of Use | Local inference provider | Planned — not yet wired |
| Gemma via Google AI API | API model ID TBD by Member 3 | Gemma Terms of Use | Hosted inference provider (opt-in) | Planned — not yet implemented |
| Ollama | Version TBD by Member 2 | MIT | Local model runtime | Planned — not yet integrated |
| FastAPI | TBD by Member 3 | MIT | Backend API server | Planned — not yet implemented |
| VirtualBox | Existing install — version TBD | GPLv2 | Windows guest VM | Member 1 infrastructure only |

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
| Gemma 4 (local Ollama) | Members 1 & 2 (runtime target) | Windows diagnostic reasoning — not yet integrated |
| Gemma via Google AI API | Member 3 (when credentials available) | Hosted inference — not yet integrated |

All generated code was reviewed and committed by the appropriate team member.
No earlier prototype model output, prompts or inference results are re-used.

---

## Dataset notice

No dataset is used by this project. No model has been fine-tuned.

---

## Pending items

- [ ] Member 2: Record exact Ollama/Gemma tag and confirm license acceptance.
- [ ] Member 3: Record FastAPI and other dependency versions; add environment example.
- [ ] Member 1: Record VirtualBox version and Windows guest edition.
- [ ] Member 4: Update this file as each component is confirmed working.
