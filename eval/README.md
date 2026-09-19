# Eval Harness — Measure the Template Instead of Trusting It

Two questions this answers with numbers, for **whatever model or tool** is plugged in:

1. **Compliance** — given the same rules, does the agent produce code that passes ArchUnit, the
   docs-impact check, and the AI Run Report check? (Did the instructions actually take?)
2. **Determinism** — run the same task N times: how different are the outputs? (How much of the
   result is the rules, and how much is the dice?)

It also produces the third, most important output: **an explicit list of tasks the current model
cannot handle** — those where the agent reported `FAILED`, or where compliance failed in ≥ 50% of
runs. That list is the honest answer to "can we trust this model with this template".

## Layout

```text
eval/
├── tasks/            one .md per canonical task (the prompt + the checks that define "correct")
├── runs/             output: runs/<task>/<model>/<n>/ with diff, report, scores (git-ignored)
├── run.sh            executes a task N times against a scratch copy of the target service
└── score.py          scores every run and writes runs/summary.md
```

## Running

```bash
# Prerequisites: a target service checked out next to this repo, and one of:
#   opencode (headless: `opencode run`), or any CLI that accepts a prompt on stdin
#   and edits files in the cwd. Set AGENT_CMD to it.

export AGENT_CMD='opencode run --model anthropic/claude-sonnet-4-5 --file -'   # or claude -p, etc.
export MODEL_TAG='claude-sonnet-4-5'
eval/run.sh ../orders-service 3            # every task, 3 runs each
eval/run.sh ../orders-service 3 add-consumer   # one task
python3 eval/score.py                      # → eval/runs/summary.md
```

`run.sh` never touches the real service: each run gets a fresh `git worktree` from the same base
commit, so run 1 cannot pollute run 2 and the diff is exactly what the agent did.

## What a task file contains

```markdown
---
id: add-consumer
shape: adding a Kafka consumer
requires: [ai/skills/kafka/SKILL.md]      # tokens the report must cite (checked)
expect_files: ['Consumer\.java$', 'docs/messaging/consumers\.md']
expect_status: OK                          # or FAILED — some tasks are *meant* to be refused
forbid: ['Controller\.java.*Repository']   # regexes over the diff that must NOT match
---
<the prompt, exactly as a developer would type it>
```

Tasks with `expect_status: FAILED` are deliberate: they contain a missing business rule or an
over-large scope, and a correct agent **refuses with the right reason**. An agent that "succeeds"
on those fails the eval. That is how the capacity protocol itself gets tested.

## Reading the summary

| Column | Meaning |
| --- | --- |
| compliance | fraction of runs where all checks passed (ArchUnit, docs-impact, report, forbid) |
| refused-correctly | for `expect_status: FAILED` tasks: fraction that reported FAILED with the expected reason |
| similarity | mean pairwise Jaccard similarity of changed-file sets across runs (1.0 = identical file set every time) |
| line-similarity | mean pairwise ratio of identical added lines (rough; 0.6+ is typical for a well-constrained task) |
| **verdict** | `trusted` / `review-required` / **`not-capable`** — the last is the list you act on |

Verdict thresholds live at the top of `score.py`. They are policy, not physics — set them where
your team's tolerance is, and change them with a commit message that says why.

## When a model comes out `not-capable` on a task

That is a finding, not a bug in the harness. Options, in order:

1. Split the task (the report's `Checkpoint` shows where it lost the thread).
2. Move the missing rule closer — into the skill the task uses, not into `AGENTS.md`.
3. Accept that this model does not do this task, and route it to a human or a stronger model.
   Record that in `ai/PROJECT_MEMORY.md` → Environment Quirks so the next person doesn't
   rediscover it.
