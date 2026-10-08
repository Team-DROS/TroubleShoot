# Join the repository and revised branches

Use this newly created repository, not the earlier standalone prototype checkout. Keep older history separate; no unrelated-history merge or prototype cherry-pick.

## Revised roles

| Member | Previous branch (retired) | Current branch |
|---|---|---|
| 1 / local Gemma + VM | `member-1/gemma-orchestrator` | `member-1/windows-desktop-vm` |
| 2 / local Gemma | `member-2/windows-computer-use` | `member-2/local-gemma-agent` |
| 3 / no local model/VM | `member-3/ui-vm-validation` | `member-3/backend-hosted-api` |
| 4 / documentation | unchanged | `member-4/docs-demo-submission` |

The role update is documentation-only. Existing shared code/test behavior is unchanged. Old remote role branches are retired only after checking no unique teammate commits have appeared; shared history is preserved in main and the new branches.

## New clone

```powershell
git clone https://github.com/Team-DROS/TroubleShoot.git TroubleShoot-Event
cd TroubleShoot-Event
git fetch origin
git switch --track origin/member-1/windows-desktop-vm
```

Substitute your current branch from the table. Each person needs private-repository access and their own Git identity.

## Existing clone

Pause any agent working on the previous role. Inspect `git status -sb`, preserve uncommitted/fresh work separately, then fetch and switch to the new branch. If it already exists locally, use `git switch <branch>` and `git pull --ff-only`. Do not reset or overwrite local changes. Review any unpublished code for the new ownership before carrying it forward; never carry the earlier prototype implementation.

Member 4's branch name is unchanged; update it with a fast-forward pull. Read the revised MEMBER_N.md before resuming, including hardware requirements and handoffs. Coordinate API/contracts with Member 3 and provider protocol with Member 2.

Reuse installed third-party tools/model caches where permitted. Member 3 develops API/UI with injected test fixtures and explicit hosted inference when credentials are available; no local-model/VM installation is required. Member 4 needs only Git/editor/browser.
