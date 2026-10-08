# Local Gemma provider and agent reasoning (Member 2)

Owner: Member 2, branch `member-2/local-gemma-agent`. Standard library only: no new Python dependencies.

| Path | Purpose |
|---|---|
| `src/troubleshoot/providers/base.py` | Provider protocol shared with Member 3's hosted adapter |
| `src/troubleshoot/providers/ollama.py` | Local Ollama transport |
| `src/troubleshoot/agent/` | Decision schema, prompts, Think/Act/Verify coordinator, deterministic verdicts, simulation and CLI |
| `tests/unit/test_provider_local.py`, `tests/unit/test_agent.py` | Unit tests (simulated HTTP server, scripted provider, simulated machine) |
| `docs/evidence/local-model/` | Recorded real-inference runs (simulated tools) |

## Run it on a Gemma PC (PowerShell)

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests/unit -v                     # no model needed
python -m troubleshoot.agent.cli status                          # live runtime/model/capabilities
python -m troubleshoot.agent.cli smoke --record docs/evidence/local-model
python -m troubleshoot.agent.cli eval  --record docs/evidence/local-model
```

Settings via environment: `TROUBLESHOOT_OLLAMA_MODEL` (default `gemma4:e2b`), `TROUBLESHOOT_OLLAMA_URL` (default `http://127.0.0.1:11434`), `TROUBLESHOOT_OLLAMA_ALLOW_LAN=1` to permit a non-loopback runtime such as the host seen from the VirtualBox guest. A LAN runtime is reported as `locality: "lan"`, never as local.

`smoke` and `eval` use **real local inference** with **simulated tools and facts** (`agent/simulation.py`). They measure the model's decisions and the loop's safety behavior. They are not Windows troubleshooting evidence; Member 1's guest runs provide that.

## Provider protocol (for Member 3's hosted adapter)

```text
Provider.name, Provider.model
Provider.status()  -> ProviderStatus   # live query; never raises for an unreachable runtime
Provider.decide(ModelRequest) -> ModelReply   # one parsed JSON object, or raises ProviderError
```

- `ModelRequest(system, user, schema, images=(), max_output_tokens=512, timeout_seconds=90)`. `schema` is the JSON schema the reply must follow (`agent.decision_schema`).
- `ModelReply(data, provider, model, latency_ms, prompt_tokens, output_tokens)`. `data` is not yet trusted; the agent validates it.
- `ProviderError.code` is one of `unavailable, model_missing, timeout, malformed, too_large, capability, configuration, http, cancelled`.
- `ProviderStatus` separates `configured`, `reachable`, `model_present` and `last_inference_ok`. Configuration is not inference proof.
- `ImageInput(ref, media_type, data)`: PNG or JPEG, at most 4 MiB, bytes never appear in `repr` or events. A provider without declared vision raises `capability` instead of dropping the image.
- `parse_json_object` is the shared strict parser: one JSON object, optionally inside a single Markdown fence. Anything else is `malformed`.
- No adapter may call another provider or return canned text when it fails. Hosted consent stays in `RunRequest` (Member 3).

Ollama specifics: `stream: false`, `format: <schema>` for constrained decoding, `temperature 0`, `seed 7`, `num_ctx 8192`, `keep_alive 10m`. `think` is sent only when `/api/show` declares `thinking` (default `false` for latency). Capabilities come from `/api/show`, model presence from `/api/tags`. Environment HTTP proxies are bypassed so local prompts/images cannot leave the machine through a proxy. Replies over 2 MiB and prompts over 48k characters are rejected.

## Coordinator hooks (Member 3 runtime, Member 1 executor)

```text
Coordinator(provider, Catalog([...ToolSpec]), Budget()).run(complaint, mode, hooks, vision=False) -> Outcome
```

`ToolSpec(name, description, mutates, arguments_json_schema, validator, postcondition)`: Member 1 supplies one per registered operation; `validator` is the same strict validator used by `contracts.parse_action`. A mutating tool must describe its postcondition.

`hooks` must provide:

| Hook | Owner | Contract |
|---|---|---|
| `observe() -> FreshObservation(observation, facts, image=None)` | Member 1 | New observation each call; `facts` is JSON-serialisable symptom data |
| `authorize(proposal, tool) -> bool` | Member 3 | Called for every action; must return exactly `True` to proceed. Bind/expire approval here |
| `execute(proposal, fresh) -> ExecutionResult(status, evidence, error)` | Member 1 | Re-validates identity/freshness itself; status `ok, blocked, failed, cancelled` |
| `postcheck(proposal, result) -> [Check(name, expected, actual, passed, symptom)]` | Member 1 | Fresh facts after a change; `symptom=True` only for checks of the user's symptom |
| `cancelled() -> bool` | Member 3 | Polled before each model call, after it, and before execution |
| `emit(kind, payload)` | Member 3 | `kind` in observation/plan/approval/action/verification/complete/error; wrap with `contracts.event` |

`Outcome.status`: `diagnosed, completed, needs_user, denied, cancelled, error, budget_exhausted`. `Outcome.verdict` exists only after a change and comes from `judge()`.

### What the loop enforces

1. Diagnose mode never shows a mutating tool to the model; the schema has no branch for it and `parse_decision` rejects it anyway.
2. Constrained decoding ties each operation to its own argument schema. The executor's validator then re-checks arguments.
3. Model output that breaks the schema is rejected and fed back once in HISTORY; more than `max_invalid` consecutive rejections ends the run with `error`.
4. Inference outlasts the 5 s freshness window, so after a decision the target is observed again, identity compared, and the proposal bound to that new observation (`require_target`). After approval it is observed once more; a replaced target aborts.
5. Budgets: 6 decisions, 1 approved change, 300 s wall clock, 120 s per model call, 400 output tokens per decision. Identical repeated tool calls are rejected.
6. Observed text is fenced as untrusted data with a random nonce; instruction-like snippets are reported in `Outcome.untrusted_instructions`. The guard is structural (schema, registry, approval), not the prompt.
7. Verdict: all symptom checks pass with execution `ok` → `resolved`; some → `partial`; none or no symptom checks → `unresolved`. A model opinion can only lower a verdict. "Restarted successfully" without a passing symptom check is never `resolved`.
8. Images go to the model only when the run opted into vision and the observation has one; events carry only the image `ref`.

## Evidence

See `docs/evidence/local-model/` for recorded runs, each labelled with runtime version, model, settings, revision and the simulation notice. Per-run results are summarised below as they are recorded.
