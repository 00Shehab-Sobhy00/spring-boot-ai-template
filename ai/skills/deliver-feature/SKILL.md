---
name: deliver-feature
description: >
  Run a multi-step feature from intake to finished: inspect git state, decide the branch, sequence
  the work across layers (API, persistence, tests), reconcile, review, and close out. Use for any
  request that spans more than one file or one concern — "add feature X", "implement Y end to end",
  "build and ship Z". Not for a one-line fix.
metadata:
  when_to_use: ["implement this feature", "add X end to end", "build and ship this", "deliver this feature", "work through this ticket", "do the whole thing"]
---
<!-- evidence-token: SKDELI-NFB0EQ — cite in the AI Run Report -->

# Deliver a Feature End to End

Most non-trivial work fails not on any single step but on the **sequence**: schema invented after
the endpoint is written, tests bolted on last, review skipped because the change "felt small," docs
never touched. This skill is the sequence. It doesn't restate the rules — each step points at the
rule file or skill that owns it.

Use it when a request spans layers. Skip it for a one-line fix, a typo, or a single-file change
that stays inside one concern.

## Step 0 — Ground yourself before planning

Read before you plan; a plan built on assumptions produces work that has to be redone.

1. `git status` and `git branch --show-current` — what's already in flight?
2. Read the actual files the request touches (controller, entity, sibling implementations).
3. Check `ai/PROJECT_MEMORY.md` for a gotcha covering this area.
4. For business-meaning work, read `docs/business/business-overview.md` and check
   `docs/business/rules.md` for an existing `BR-nnn` that governs the behavior.

## Step 0.5 — Capacity check (`ai/CAPACITY.md`)

Before planning, count. This is where most silent failures are decided.

- Files you will edit, services you will touch, rule/skill/pattern files you will need.
- Over the budget in `ai/CAPACITY.md` (12 files / 3 services / 6 rule files)? Propose the split
  and stop, or declare `FAILED / scope-too-large`. Do not "try anyway".
- Open a **checkpoint** block now and update it after every step below. If, at any update, you
  cannot reconstruct a decision you locked earlier — that is context loss; stop with
  `FAILED / context-overflow` and hand over the checkpoint.
- Record the evidence token of every rule file as you read it; the AI Run Report needs them.

## Step 1 — Decide the branch, deliberately

Branch choice is part of delivery planning, not an afterthought.

| Situation | Do |
| --- | --- |
| Already on a focused branch for this work | Continue there |
| On `main`/`master`/`develop` and the request is a real feature | Create a dedicated branch before editing |
| Current branch holds unrelated uncommitted changes | **Stop and ask.** Never silently mix work into someone else's in-flight changes |
| User said explicitly to stay put | Stay put |

Prefer a new branch when the task spans multiple files, changes public API behavior, or is likely
to end in a merge request. Never create or switch branches when there are conflicting or
unexplained local changes.

## Step 2 — Sequence the work by layer

Order matters: the data shape constrains the contract, and the contract constrains the tests.

1. **Persistence first** when the data shape changes — `database` skill. A new changelog file,
   never an edit to an existing one. Entity, repository, and changelog stay aligned.
2. **Contract second** — `create-rest-api` (or `kafka` for an event contract). DTOs before wiring;
   validation on the request; correct status codes; no entity leaking into a response.
3. **Business rule third** — if the change adds a domain condition (a threshold, a window, an
   eligibility check), it needs a `BR-nnn` id in `docs/business/rules.md` and a `// BR-nnn` comment
   on the condition *and* on its test. If the rule isn't already registered, that's a question for
   a human — do not invent the rationale.
4. **Tests fourth** — `create-integration-test`, plus a concurrency test if the path can run on more
   than one replica (`ai/TESTING.md`).
5. **Reconcile.** If steps touched adjacent files or overlapping behavior, read the combined result
   as one change, not as separate edits. This is where inconsistencies actually surface.

## Step 3 — Verify narrowly, then broaden

Run the smallest verification that proves the behavior, then widen. Read the *first* meaningful
failure, not the last stack-trace line. Separate a real regression from an environment problem
(missing container, local DB, absent proxy — see `PROJECT_MEMORY.md` → Environment Quirks).

## Step 4 — Review before declaring done

Run `review-pr` against your own diff and report it as Blockers / Suggestions / Notes. Reviewing
your own work catches the layering slip and the missing validation cheaply, before a human spends
attention on it. If the change touches auth, input handling, or data exposure, also run
`ai/prompts/security-review.md`.

## Step 5 — Close out

Run `sync-docs`. The task is not finished until its close-out block exists: what docs were updated,
what needs a human, what knowledge was captured, and the ledger line — followed by the **AI Run
Report** (`ai/CAPACITY.md`). `OK` only if nothing is unverified, assumed, or pending a human;
otherwise `DEGRADED`, and `FAILED` with a reason and checkpoint if a stop condition fired. If the
user wants the work published, `create-merge-request` is the last step — after implementation,
verification, and review, never before.

## Report

End with a short summary: what changed, what was verified (exact commands), what was *not* verified,
and any remaining risk. "Done" without a verification line is not done.

## Stop conditions

Any of these ends the task with `FAILED` or `DEGRADED` — never with a guess (`ai/CAPACITY.md`):
a rule contradiction, a domain condition without `BR-nnn`, a verification failure you can't
attribute, a file you're editing but didn't read, a generated file you're about to hand-edit,
a public contract you're about to break.

## Don't

- Don't delegate the thinking: decide the sequence yourself, then execute it
- Don't start editing before Step 0 — exploration after the fact is rework
- Don't skip Step 5 because the change felt small; the docs-impact check will catch it anyway
- Don't batch unrelated improvements into a feature branch (`AGENTS.md` → Non-Goals)

## Related

`ai/skills/sync-docs/` · `ai/skills/create-merge-request/` · `ai/skills/review-pr/` ·
`ai/agents/README.md` (when this workflow is worth splitting across subagents instead)
