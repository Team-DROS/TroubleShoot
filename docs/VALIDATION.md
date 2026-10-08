# Fresh project validation

8 October 2026, Asia/Calcutta. Newly authored shared contracts and tests; no old
prototype code or validation imported.

---

## Contracts and unit tests (Member 3 — verified)

- **16 unit tests pass** covering:
  - Local-mode default (ollama, diagnose).
  - Explicit hosted / image consent enforcement.
  - Unknown provider rejection.
  - Unknown operation rejection.
  - Extra-field rejection.
  - Per-operation argument rejection.
  - Target identity binding (handle / PID / start-time).
  - Observation freshness: stale and future timestamps.
  - Invalid freshness policy inputs (NaN, inf, bool, non-positive).
- Python source compilation and Git whitespace checks pass.
- Fixtures are **synthetic**; no live model inference or Windows operation is claimed.
- Tests use the installed Python runtime and standard library; no model / dependency / VM duplication.

Run command:
```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests/unit -v
```

---

## Documentation deliverables (Member 4 — verified)

Completed on 8 October 2026, branch `member-4/docs-demo-submission`:

| File | Purpose | Commit |
|---|---|---|
| `CLAUDE.md` | Agent entry-point list for Member 4 | `ee18873` |
| `docs/ATTRIBUTION.md` | Licenses, components, AI tool usage | `4b100d6` |
| `docs/CONTRIBUTIONS.md` | Per-member contribution log | `331236f` |
| `docs/DEMO_SCRIPT.md` | Structured 5-min demo walkthrough | `e33d7ec` |
| `docs/SUBMISSION_CHECKLIST.md` | Pre-release and final submission checklist | `c682de1` |
| `docs/TEMPLATE_GUIDE.md` | Template mapping, portal differences, alignment checklist | `de66bc8` |
| `README.md` | Full template-aligned rewrite | `b240eed` |

---

## Pending evidence (to be appended by Members 1–3)

Member 1 owns this section and appends actual guest/native evidence:

### Member 1 — Windows / VM evidence
_(Pending: commit hash, date/time IST, OS version, VM snapshot name, scenario,
before state, approval event, action result, after state, limitations.)_

### Member 2 — Local Gemma evidence
_(Pending: Ollama version, Gemma tag, model response sample, inference timing,
provider test result.)_

### Member 3 — API / hosted / UI evidence
_(Pending: FastAPI routes tested, SSE event sample, hosted Gemma API status —
available or blocked, UI screenshot.)_

---

## No running application or live evidence yet

No runnable UI / API or hosted adapter exists. No live repair, guest result or
Gemma inference has been performed against this fresh codebase.
Fixture screenshots and recorded simulations are not live repairs.
