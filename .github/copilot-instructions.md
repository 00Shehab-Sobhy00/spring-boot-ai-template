# Copilot adapter

All rules live under `ai/`; this file only points at them (single source — see `AGENTS.md`).

Read, in order: `AGENTS.md`, `ai/AI_BEHAVIOR.md`, `ai/CAPACITY.md`, `ai/ARCHITECTURE.md`, `ai/BACKEND_RULES.md`,
`ai/TESTING.md`, `ai/REVIEW.md`, `ai/PROJECT_MEMORY.md`.

Before a common task, follow the recipe in `ai/skills/<name>/SKILL.md`. End every non-trivial
task with `ai/skills/sync-docs/SKILL.md` and the close-out format it defines.
Every task ends with the AI Run Report from `ai/CAPACITY.md`; `FAILED` with a reason beats a false `OK`.
