# TroubleShoot — Team DROS

Fresh Windows troubleshooting assistant project: local Gemma 4, bounded terminal and selected-window tools, approval, fresh verification and recovery. Hosted Gemma support is planned as an explicit optional mode.

This new private repository includes planning and the first freshly authored shared-contract module. No old implementation or old Git history is imported. See [provenance](docs/PROVENANCE.md).

Start with [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) and [join instructions](docs/RESTART.md).

| Member | Work | Branch |
|---|---|---|
| 1 / Gemma PC A | [Providers, backend, integration](docs/team/MEMBER_1.md) | `member-1/gemma-orchestrator` |
| 2 / Gemma PC B | [Windows tools and computer use](docs/team/MEMBER_2.md) | `member-2/windows-computer-use` |
| 3 / VirtualBox | [UI and guest validation](docs/team/MEMBER_3.md) | `member-3/ui-vm-validation` |
| 4 / lighter role | [Docs, demo, submission preparation](docs/team/MEMBER_4.md) | `member-4/docs-demo-submission` |

Repository stays private until explicit user instruction. Read [rules](HACKATHON_AGENT_RULES.md) and [submission checklist](docs/SUBMISSION_CHECKLIST.md). No accepted submission or live repair is claimed.

## First development milestone

Shared validation is implemented in `src/troubleshoot/contracts.py`; read [CONTRACTS.md](docs/CONTRACTS.md) for interfaces and synthetic examples. No running API, model connection, Windows executor or UI exists yet.

Run the new tests with Python 3.11+; no package downloads are required:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests/unit -v
```

Member 1 continues with the local provider and API; Member 2 implements the executor registry; Member 3 builds the UI against these contracts and checks clean VM readiness. Member 4 prepares documentation.
