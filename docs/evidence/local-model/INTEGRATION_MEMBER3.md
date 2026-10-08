# Local Gemma through Member 3's session runtime (8 October 2026)

**What ran:** real `gemma4:e2b` (Ollama 0.40.1, CPU-only container) through Member 3's real `SessionManager` at `member-3/backend-hosted-api` revision `d8a97c0`, using Member 2's `LocalGemmaAdapter` (revision `353d70e`). **What was simulated:** the executor. It uses Member 1's operation names (`spooler_status`, `start_spooler`) over a simulated stopped Spooler with 3 queued jobs. This is not Windows evidence.

The merge was a temporary local worktree. Nothing from Member 3's branch is committed here. Script: `integration_member3_live.py` (run from a tree containing both branches' files with `PYTHONPATH=src`).

## Compatibility

With Member 3's `requirements.lock` installed, the combined tree passed Member 2 and Member 3 unit tests (95) and Member 3's API tests (29).

## Finding: actions always expire after real inference

| Run | Result |
|---|---|
| Repair, runtime as published | Gemma proposed `start_spooler` (36.7 s, 190 tokens). The runtime then raised `policy_rejected`: it requires the pre-inference observation to be under 5 s old after inference, so any real model run fails. |
| Repair, with the proposed patch | Plan → re-observation of the same target → approval (token bound to the new observation) → action `ok` → fresh check "print queue drains" passed → verdict `resolved`. Inference 35.8 s. |
| Diagnose, with the patch | Gemma chose read-only `spooler_status` (32.5 s). No approval was requested. The fresh check still failed, so the verdict was `unresolved`, which is correct for diagnose-only. |

## Proposed fix for Member 3 (not applied; Member 3 owns `runtime/session.py`)

`member3-rebind-after-inference.patch`: after the decision, re-observe the selected target, require the same identity, bounds and DPI, and bind the proposal to that new observation before approval. A changed target still fails closed. The only test change is the expected observation count (2 → 3). All 29 API tests pass with it.

Still open for Member 3: after approval, the runtime re-observes but checks freshness against the pre-approval observation. A human approval longer than 5 s therefore expires the action. The same rebind pattern would fix it, if the team accepts it within the approval policy.
