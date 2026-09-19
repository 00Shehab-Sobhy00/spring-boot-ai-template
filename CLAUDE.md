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

Skills: Claude Code discovers `.claude/skills/`, not `ai/skills/`. Point it at the single source
with one command (no copies, no symlinks committed):

```bash
# from the repo root — run once per clone
mkdir -p .claude && ln -sfn ../ai/skills .claude/skills
```

(`.claude/skills` is git-ignored; see `ai/PROJECT_MEMORY.md` → Environment Quirks for why
symlinks are not committed.)

End-of-task enforcement: `.claude/settings.json` (if present) can attach a `Stop` hook that runs
`ai/skills/sync-docs/` — opencode has no hook mechanism, so there the rule in `AGENTS.md` is the
enforcement.
