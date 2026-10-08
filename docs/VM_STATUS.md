# VM preparation for the fresh project

Owner: Member 1 (local Gemma + Windows VM). VirtualBox availability is user-reported. Guest readiness, resource capacity and snapshot state must be checked anew.

Reuse an existing Windows VM only as permitted environment infrastructure. Do not use any prior application installation, startup script, demo, test fixture or repair result inside it. Prefer a clean OS/tools snapshot, then transfer/install only newly authored competition code. No ISO/VDI copies in this repo. Do not recreate a VM or download another model without checking disk/RAM and necessity.

Run the new Windows desktop executor inside the guest. Host accessibility automation does not provide guest application controls. Ordinary VirtualBox does not provide host CUDA GPU access to Ollama; measure guest model feasibility rather than assuming it. If inference runs on host or a hosted API, configure a narrowly scoped transport deliberately and disclose locality/data flow.

A disabled guest adapter may sever inference access. Choose a first repair scenario that preserves inference, or design a deterministic approved recovery path independent of the network. Never fault the host adapter to make a demo. Snapshot and restoration are prerequisites for guest fault injection; if unavailable, limit work to observation and report the blocker.

Keep OS license acceptance and UAC with the user. Verify actual Windows desktop/dependencies, resource headroom and recovery state; record time and evidence in VALIDATION.md when available. No old VM repair results count for the fresh build.

Member 2 helps with local-model/image reasoning; Member 3 helps API/hosted transport. Neither needs a second VM to complete their role. Record fresh guest evidence for Member 4 to document.
