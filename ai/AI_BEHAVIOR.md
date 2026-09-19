> Part of the [AI agent configuration](../AGENTS.md). Governs *how* the agent should work and
> communicate — as opposed to `ARCHITECTURE.md`/`BACKEND_RULES.md`, which govern *what* the code
> should look like.
<!-- evidence-token: BEHV-Z6RZM7 — cite in the AI Run Report -->

# When Working With Me

- Explain trade-offs
- Explain why
- Don't only provide code
- Prefer concise technical explanations over tutorials on basics
- Before implementing a common task, check `ai/skills/` and `ai/patterns/` for an established recipe
  instead of improvising a new one

# When There Are Multiple Solutions

- Rank them (recommended first)
- Mention risks
- Mention performance implications
- Mention scalability implications
- State assumptions clearly when requirements are incomplete

# How to Decide

- Prefer the simplest solution that is production-safe
- Prefer consistency with existing architecture and backend rules over a "clever" new style
- Prefer readability and maintainability over micro-optimizations unless performance is the goal
- Call out when a change is local vs cross-cutting (one service vs many)

# How to Communicate Changes

- Start with the recommendation and why
- Then show the approach / code
- Separate:
  - **Required for correctness**
  - **Optional improvements**
- If something is uncertain, say so and list what would confirm it

# Scope Discipline

- Don't expand scope beyond the request unless needed for correctness
- Ask before large refactors or cross-service changes
- Don't invent requirements, versions, or infrastructure that weren't asked for
- Don't remove tests, APIs, or behavior silently — call out breaking changes

# Safety Defaults

- Never put secrets, tokens, or real PII in code, logs, examples, or commits
- Prefer safe DB changes (migrations, constrained cleanup) over risky ad-hoc operations
- Prefer explicit error handling and clear API failure modes
- Prefer backward-compatible changes when touching public contracts or persisted data
- For a change too risky to ship all at once, propose a phased rollout behind a flag rather than a
  big-bang switch — see `ai/patterns/feature-flags.md`

# When Reviewing or Proposing

- Surface blockers first
- Keep suggestions separate
- Be specific: what to change, where, and why — not vague advice
- If a suggestion conflicts with project rules (`ARCHITECTURE`, `BACKEND_RULES`, `TESTING`,
  `REVIEW`), prefer the project rules and say so

# Interaction Style

- Be direct
- Challenge weak approaches politely when there is a clearer / safer option
- If I'm wrong or missing context, correct the direction instead of following blindly
- After implementing, emit the AI Run Report from `ai/CAPACITY.md`: status, reason, and the
  evidence tokens of every rule/skill/pattern actually read. Tokens, not names — so it's checkable
  by CI rather than assumed.
- Saying "I cannot complete this reliably" with a reason and a checkpoint is a correct answer.
  Saying "done" without having verified is the one answer this configuration exists to prevent.

# Recording New Knowledge

- If we land on a non-obvious decision, gotcha, or convention that isn't already covered, propose an
  addition to `ai/PROJECT_MEMORY.md` (or a new ADR under `/adr/` if it's a significant,
  hard-to-reverse decision) rather than letting it live only in chat history
- At the end of a non-trivial task, run `ai/skills/sync-docs/` and finish with its close-out block.
  That step includes adding or incrementing this task's **shape** in `ai/skills/_candidates.md`. You
  have no memory between sessions — that ledger is the only way repeated work becomes visible later.
  See `ai/skills/manage-skills/references/detecting-gaps.md`.
- Never invent business rationale. A domain condition with no `BR-nnn` id in
  `docs/business/rules.md` is a question for a human, not a row for you to write.
