---
name: manage-skills
description: >
  Maintain this repo's own AI template — find work that should become a skill, and write or fix
  skills following the repo's conventions. Use when asked what skills are missing, whether
  something should be a skill, or to add or repair one.
metadata:
  when_to_use: ["add a skill", "write a skill", "what skills are missing", "should this be a skill", "my skill doesn't trigger", "review the template"]
---
<!-- evidence-token: SKMANA-4121JD — cite in the AI Run Report -->

# Managing This Template

The template only stays useful if it keeps up with how the team actually works. Two halves:

| You want to... | Read |
| --- | --- |
| Find work that should become a skill | `references/detecting-gaps.md` |
| Write a new skill, or fix one that won't trigger | `references/writing-a-skill.md` |

Detection comes first. A skill written without evidence of repeated need encodes a guess.

## The Constraint Behind All of This

**You have no memory between sessions.** You cannot know "we've done this three times" by
recall. Detection must be grounded in evidence on disk: the candidates ledger
(`ai/skills/_candidates.md`), git history, duplication in the codebase, or repeated corrections
recorded in `ai/PROJECT_MEMORY.md`.

This is why the ledger matters: **at the end of every non-trivial task, add or increment that
task's shape in `ai/skills/_candidates.md`.** That single habit is what makes next month's
detection possible at all.

## The Two Costs to Balance

Every skill has two price tags, and they pull in opposite directions:

- **The description** is loaded in *every session, forever*, whether the skill runs or not. Keep
  it free of anything explaining *how* — that belongs in the body.
- **The body** is loaded only when the skill triggers. Length there is cheap.

But the priority order matters: **a skill that never triggers is worth nothing regardless of how
cheap it is.** If a skill isn't firing when it should, widen the description — even past the
usual budget. Trigger accuracy beats token thrift.

## Don't

- Don't write a skill for a task done fewer than three times — record it in the ledger instead
- Don't detect and write in one motion; detection proposes, a human decides
- Don't restate a rule that already lives in a rule file — link to it
- Don't leave a new skill unregistered in `AGENTS.md`
- Don't nest skill folders (`skills/group/skill/SKILL.md`) — only the top level is discovered.
  Group by consolidating into one skill with `references/`, exactly as this one does.

## Related

`ai/skills/_candidates.md` (the ledger) · `AGENTS.md` (Skills Map) · `ai/patterns/` (for "why"
content) · `ai/prompts/` (for full workflows) · `ai/PROJECT_MEMORY.md`
