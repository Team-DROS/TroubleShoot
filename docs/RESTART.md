# Join the new repository

Use this new repository, not an older local checkout with the same remote URL. The repository was recreated: old commit ancestry must not be pushed here.

```powershell
git clone https://github.com/Team-DROS/TroubleShoot.git TroubleShoot-Event
cd TroubleShoot-Event
git fetch origin
git switch --track origin/member-1/gemma-orchestrator
```

Substitute your assigned role branch. In the original development PC's clone the local branches already exist: use `git switch <branch>`.

Keep any older project or branch separate. Do not merge unrelated histories, cherry-pick the prototype, or push from the old clone. Install only dependencies required by freshly authored code; reuse ordinary download/model caches to save disk. No old project files or compiled outputs belong here.

Read AGENTS.md, PROJECT_CONTEXT.md and your member assignment. Each person needs private-repository access, their own Git identity and the owned paths stated in the assignment. Coordinate contracts with Member 1 before integrating.
