# Claude Code adapter

All rules live under `ai/` — this file only imports them so a rule is edited once.

@AGENTS.md
@ai/AI_BEHAVIOR.md
@ai/CAPACITY.md
@ai/ARCHITECTURE.md
@ai/BACKEND_RULES.md
@ai/TESTING.md
@ai/REVIEW.md
@ai/PROJECT_MEMORY.md

Skills: Claude Code discovers `.claude/skills/`, not `ai/skills/`. Run the per-clone setup once —
`scripts/setup-agent-tools.sh` (or `.ps1` on Windows) — it links `.claude/skills` to the single
source for Claude and every other tool (`AGENTS.md` → Tool Adapters).

End-of-task enforcement: `.claude/settings.json` attaches a `Stop` hook that runs
`scripts/end-of-task-check.py` — every tool has the same hook, see `AGENTS.md` → Tool Adapters.
