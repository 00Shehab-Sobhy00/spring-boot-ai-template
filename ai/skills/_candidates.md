# Skill Candidates Ledger

> The tally that makes cross-session detection possible. The AI has no memory between
> sessions — this file **is** its memory for "have we done this before?"
>
> Maintained by: the AI (appends at the end of a task) and humans (when they notice a pattern).
> Read by: `ai/skills/manage-skills/references/detecting-gaps.md`.

## How to use this file

At the end of a non-trivial task, the AI adds or increments one line here describing the
**shape** of the task — not the specific instance. "Added a Kafka consumer for order events"
is an instance; "Adding a Kafka consumer" is a shape. Only shapes accumulate.

When a shape reaches **3 occurrences**, it is a skill candidate. That does not mean write
the skill automatically — it means raise it, and a human decides.

## Format

```text
| Task shape | Count | Last seen | Existing skill? | Notes |
```

- **Task shape** — how you'd describe the job to a new hire, in under 8 words
- **Count** — increment when the same shape recurs; do not add a duplicate row
- **Last seen** — date, so stale candidates can be pruned
- **Existing skill?** — if a skill already covers it, the answer may be to *extend* that skill
  rather than create a new one. Note which one.

---

## Candidates

| Task shape | Count | Last seen | Existing skill? | Notes |
| --- | --- | --- | --- | --- |
| *example: adding a scheduled cleanup job* | 2 | 2024-03-01 | no | *both times we got the batching wrong the first try* |
| Closing a gap between a stated rule and its CI check | 1 | 2026-09-19 | no | the rule existed in `ai/CAPACITY.md`; the script parsed the field and never used it |

## Promoted (became skills)

Move rows here when a candidate becomes a skill, so the count isn't restarted by accident
and so the history of why a skill exists is preserved.

| Task shape | Became | Date |
| --- | --- | --- |
| *example: adding a REST endpoint* | `ai/skills/create-rest-api/` | *2024-01-15* |

## Rejected (deliberately not skills)

Equally important — stops the same candidate being re-raised every few weeks.

| Task shape | Why not | Date |
| --- | --- | --- |
| *example: renaming a class* | *IDE does it; no project-specific decisions involved* | *2024-02-01* |
