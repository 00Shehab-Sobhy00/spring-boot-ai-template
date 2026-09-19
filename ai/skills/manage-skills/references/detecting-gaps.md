# Detect a Missing Skill

## The Constraint That Shapes This Whole Skill

**You have no memory of previous sessions.** You cannot know that "this is the third time"
from recall — every session starts blank. So detection must be grounded in evidence that
already exists on disk. There are four such sources, and they are listed below in order of
how much you should trust them.

If none of them show evidence, say so. Do not estimate, guess, or infer frequency from how
common the task *feels* in general — that produces skills for imaginary problems.

## Source 1 — The candidates ledger (most direct)

`ai/skills/_candidates.md` is the tally. It exists precisely because you can't remember.

**To read it:** any row with `Count >= 3` is a candidate to raise now. Check the
`Rejected` table first — if the shape is listed there, do not raise it again.

**To write to it — do this at the end of every non-trivial task:**

1. Describe the task as a **shape**, not an instance. Under 8 words.
   - Instance: "added a Kafka consumer for `order.created`" ✗
   - Shape: "adding a Kafka consumer" ✓
2. Look for an existing row with that shape. If found: increment `Count`, update `Last seen`.
3. If not found: add a row with `Count: 1`.
4. Never add a second row for a shape already listed — that is how a count reaches 3
   without anyone noticing.

This one step is what makes every future detection possible. Without it, sources 2–4 are
all you have.

## Source 2 — Git history (strongest objective evidence)

Git remembers what you don't. Look for the same *kind* of change recurring.

```bash
git log --oneline -60
git log --oneline --name-only -40 | sort | uniq -c | sort -rn | head -25
```

What you're looking for:

- The same file *types* changed together repeatedly (e.g. a new `*Consumer.java` always
  arrives with a `*ConsumerTest.java` and a topic entry in the docs) — that trio is a recipe
- Commit messages with a recurring verb+noun shape ("add consumer for X", "add consumer for Y")
- A directory that grows by near-identical files over time

Three occurrences in git history is real evidence, not a guess.

## Source 3 — Code duplication (evidence the repetition already happened)

If a shape has been implemented several times, the results are sitting in the repo.

```bash
# example: how many things follow the same structural shape?
ls -1 **/*Consumer.java 2>/dev/null | wc -l
grep -rl "@KafkaListener" --include=*.java src | wc -l
```

Look for N ≥ 3 files that are structurally the same and differ only in the domain nouns.
Then read two of them side by side and ask: **did the author have to make the same
decisions each time?** If yes, those decisions belong in a skill. If the files are
identical boilerplate with no decisions, the answer may be a base class or a generator —
not a skill.

## Source 4 — Repeated corrections (highest-value signal, hardest to see)

The strongest signal a skill is missing is a correction the human has had to make more than
once. These are recorded — check:

- `ai/PROJECT_MEMORY.md` → Known Gotchas and Conventions log
- Review comments captured anywhere in the repo
- Any note that starts "remember to..." or "we always..."

A rule that had to be stated twice is a rule that isn't written down where the AI reads it.
That is a skill (or a rule-file line), not a personality flaw.

## Source 5 — This session only (weak, but free)

Within the current conversation you *can* see repetition directly. If you have been asked to
do structurally the same thing three times in this session, say so. But treat it as a
`Count: 1` shape in the ledger — a single session's repetition is often just one big task,
not a recurring pattern.

## Steps

1. **Check the ledger first** (`ai/skills/_candidates.md`) — rows at `Count >= 3` that aren't
   in `Rejected`.
2. **Corroborate with git and the codebase** (sources 2 and 3) for anything you're about to
   raise. A ledger count backed by git history is a strong case; a ledger count with nothing
   in git may be a mis-tallied shape.
3. **Apply the filters** below before raising anything.
4. **Raise it as a proposal, not an action.** Output the format below and stop. Writing a skill is
   `ai/skills/manage-skills/references/writing-a-skill.md` — and it needs a human decision first.
5. **Update the ledger** with this task's own shape before you finish.

## Filters — reasons NOT to raise a candidate

Run every candidate through these. Most fail at least one:

- **Already covered** — an existing skill fits, or would fit with one added step. Extending
  beats creating; propose the extension instead.
- **No project-specific decisions** — if the task is the same in any Spring Boot repo, the
  model already knows it. A skill adds value only where *this repo* made choices.
- **It's a rule, not a recipe** — a single constraint ("always X") belongs as a line in
  `ai/BACKEND_RULES.md`, not a whole skill folder.
- **It's a "why", not a "how"** — belongs in `ai/patterns/`.
- **Fewer than 3 occurrences** — record it, don't raise it. Two is a coincidence.
- **Already rejected** — check the `Rejected` table; don't re-litigate.
- **The real fix is code** — if every occurrence is identical boilerplate with no decisions,
  the answer is a base class, an annotation, or a generator. Say that instead.

## Output Format

```text
### Skill gap detected: <task shape>

Evidence:
- Ledger: Count 3, last seen <date>
- Git: <N> commits matching this shape (list 2-3)
- Codebase: <N> structurally similar implementations at <paths>
- Repeated correction: <quote from PROJECT_MEMORY, if any>

Decisions the author had to make each time:
- <the thing that varies and requires judgment>
- <another>

Recommendation: [new skill `<name>` | extend `<existing-skill>` | rule line in <file> | code fix, not a skill]

Not proposing to write it — that's your call.
```

If nothing meets the bar, say exactly that. "No gaps found" is a valid and useful result;
inventing one to seem helpful pollutes the template with skills nobody triggers.

## Don't

- Don't claim a count you can't point at a source for — no memory, no estimate, no vibes
- Don't write the skill in the same breath as detecting the gap; detection proposes, a human decides
- Don't raise a candidate that's already in the `Rejected` table
- Don't skip updating the ledger at the end of a task — that's the step that makes next month's
  detection work at all

## Related

`ai/skills/_candidates.md` (the ledger) · `ai/skills/manage-skills/references/writing-a-skill.md`
(what to do once a gap is confirmed) · `ai/PROJECT_MEMORY.md` (repeated corrections live here) ·
`AGENTS.md` (Skills Map)
