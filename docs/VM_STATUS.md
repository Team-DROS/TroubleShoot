# VM preparation for the fresh project

Owner: Member 1 (local Gemma + Windows VM).

## Fresh checks: 8 October 2026

- `TROUBLESHOOT-Test` verified running Windows 11 Enterprise LTSC Evaluation, version 10.0.26100; Guest Additions 7.2.8. Interactive guest execution is session 1. Guest Python was not available, so fresh native workers were tested with Windows PowerShell 5.1; the Python policy layer was tested on the host.
- Recovery snapshot `fresh-tools-preflight-20261008`, UUID `d92e3823-463e-4b5a-9ea1-dc4312c05450`, created while powered off before fresh tests. Restore has not been exercised; normal service/fixture recovery succeeded without needing it.
- VM configured with 4096 MB RAM, 3 CPUs, NAT; clipboard and drag-and-drop disabled. At the last guest diagnostic: about 1.7 GiB free RAM and 31.3 GiB free C: storage. Host preflight had approximately 4 GiB free RAM and only 7 GiB free on D:, so avoid another VM/model download. Joint Gemma+VM inference capacity is not yet measured.
- Fresh WPF fixture tested selected-window inspection, checkbox toggle, capture, denied/stale/secret capture, reused identity rejection, foreground loss, partial close and cooperative cleanup. Earlier WinForms fixture controls appeared as generic panes and were correctly refused; the supported WPF fixture exposes actual TogglePattern controls.
- User entered credentials locally and approved guest UAC manually. A fixed elevated test stopped only the guest Spooler, ran the new repair worker, verified Running, and restored the original Running baseline. Actual printing was not tested.
- Only newly authored scripts/fixtures were transferred under `C:\Users\Public\TroubleShootFresh`. No old application or model files were copied. Temporary host credential files were removed after testing. The VM remains running with its visible console available.
- Evidence: `docs/evidence/windows/desktop-2026-10-08.json` and `service-2026-10-08.json`; exact integration and limitations in `INTEGRATION.md` in that directory.

Reuse an existing Windows VM only as permitted environment infrastructure. Do not use any prior application installation, startup script, demo, test fixture or repair result inside it. Prefer a clean OS/tools snapshot, then transfer/install only newly authored competition code. No ISO/VDI copies in this repo. Do not recreate a VM or download another model without checking disk/RAM and necessity.

Run the new Windows desktop executor inside the guest. Host accessibility automation does not provide guest application controls. Ordinary VirtualBox does not provide host CUDA GPU access to Ollama; measure guest model feasibility rather than assuming it. If inference runs on host or a hosted API, configure a narrowly scoped transport deliberately and disclose locality/data flow.

A disabled guest adapter may sever inference access. Choose a first repair scenario that preserves inference, or design a deterministic approved recovery path independent of the network. Never fault the host adapter to make a demo. Snapshot and restoration are prerequisites for guest fault injection; if unavailable, limit work to observation and report the blocker.

Keep OS license acceptance and UAC with the user. Verify actual Windows desktop/dependencies, resource headroom and recovery state; record time and evidence in VALIDATION.md when available. No old VM repair results count for the fresh build.

Member 2 helps with local-model/image reasoning; Member 3 helps API/hosted transport. Neither needs a second VM to complete their role. Record fresh guest evidence for Member 4 to document.

Fresh mouse validation (source `2fa7187`): all 22 native guest checks passed at 12:55:55 IST on 8 October 2026, including movement/click/double click/scroll/slider drag and refusal/cancellation/recovery cases. Report: `docs/evidence/windows/mouse-2026-10-08.json`. Demo work and recording are deferred; a synthetic controller script remains available for later. No Gemma or real application repair was tested in this mouse suite.
