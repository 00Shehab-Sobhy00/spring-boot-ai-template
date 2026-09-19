---
name: review-pr
description: >
  Review a diff or pull request against this repo's review checklist and output Blockers /
  Suggestions / Notes. Trigger when the user asks to review a PR, review a diff, or "check my
  changes before I push".
metadata:
  when_to_use: ["review this PR", "review my diff", "check this before I commit", "code review"]
disable-model-invocation: false
---
<!-- evidence-token: SKREVI-5YJPIW — cite in the AI Run Report -->

# Review a PR / Diff

Runs the checklist in `ai/REVIEW.md` against a change and reports findings in the required output
format. If a deeper security or architecture pass is also wanted, hand off to
`ai/prompts/security-review.md` or `ai/prompts/architecture-review.md` — this skill covers the
standard day-to-day checklist.

## Steps

1. **Get the diff.** If not already in context, ask for it (or read the changed files) rather than
   reviewing from memory of the conversation.
2. **Walk the checklist in `ai/REVIEW.md`**: naming, complexity, performance, thread safety, null
   safety, SQL efficiency, duplicate logic, API & error correctness, tests & safety.
3. **Check consistency with the rule files** — does this change match `ai/ARCHITECTURE.md` layering
   and `ai/BACKEND_RULES.md` conventions, or does it quietly introduce a second style?
4. **Check for scope creep** — is this diff doing more than the stated task, per `ai/AI_BEHAVIOR.md`
   (Scope Discipline)?
5. **Produce the output in the required format** (from `ai/REVIEW.md`):
   - **Blockers** — must fix before merge
   - **Suggestions** — optional improvements, listed separately from blockers
   - **Notes** — informational observations only

## Don't

- Don't mix "what changed" narration in with the blockers/suggestions list — keep them separate
- Don't invent a blocker out of personal style preference when the code matches the existing repo
  convention — prefer consistency (`ai/AI_BEHAVIOR.md` → How to Decide)
- Don't skip calling out a real correctness or security issue to be agreeable

## Related

`ai/REVIEW.md` · `ai/prompts/security-review.md` · `ai/prompts/architecture-review.md` ·
`ai/skills/database/references/optimize-query.md`
