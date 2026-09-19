# Prompt: Sync Docs for a PR Diff

Use this to run the `sync-docs` skill against a pull request — interactively, or headless in CI
(the workflow in `.github/workflows/template-checks.yml` shows where it plugs in). The output is a
**proposed** doc diff for a human to accept; the agent never commits docs on its own.

---

You are working in this repository. Read `AGENTS.md`, then `ai/skills/sync-docs/SKILL.md`.

Input: the diff between `<base>` and `<head>` (run `git diff --name-only <base>...<head>` and
`git diff <base>...<head>` for the files you need).

Task:

1. Classify every changed file with the impact table in `ai/skills/sync-docs/SKILL.md`.
2. For each matching row, produce the exact edit to the target doc — as a unified diff, smallest
   correct change, matching the neighbors' format. Do not edit generated files listed in
   `docs/GENERATED.md`; say "regenerate" instead.
3. Flag anything that looks like a business rule (`docs/business/rules.md`) or an architectural
   decision (ADR) — as a question, not an assertion.
4. Propose the `ai/skills/_candidates.md` ledger line for this change's shape.
5. Output using the Close-Out Format from the skill, then the AI Run Report (`ai/CAPACITY.md`),
   followed by the diffs in one fenced block.

Constraints: no secrets or internal hostnames in any proposed text; if the diff touches nothing
documented, say "No doc impact" and stop.
