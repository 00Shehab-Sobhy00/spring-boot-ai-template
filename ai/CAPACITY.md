> Part of the [AI agent configuration](../AGENTS.md). Authoritative source for **how the agent
> declares its own limits**. Every other rule file assumes the agent read and retained it; this file
> is what makes that assumption checkable instead of hoped-for.
<!-- evidence-token: CAPA-Q7N2XM — cite this in every AI Run Report. Do not copy it elsewhere. -->

# Capacity Protocol

A wrong "done" is the most expensive output you can produce. A truthful "I could not do this, and
here is why" is cheap, and it is the only outcome the pipeline can act on. This file defines the
three outcomes, when each applies, and the report CI parses to enforce them.

You are a language model. You have a finite context window, no memory between sessions, and you
will not notice when an instruction has scrolled out of your working memory. The rules below are
designed so that **that failure is detected mechanically** rather than assumed away.

# The Three Outcomes

| Status | Meaning | What CI does |
| --- | --- | --- |
| `OK` | Every step done, every verification run, every required rule cited | Passes (if the rest of the report checks out) |
| `DEGRADED` | Work is complete but something was **not verified**, **skipped**, or **assumed** | Fails unless a human adds `Accepted-Degraded: <reason>` to the PR body |
| `FAILED` | The task could not be completed correctly by this agent in this session | Fails, hard, with the reason in the CI log. This is the intended path, not an error |

`FAILED` is not a bad outcome. Silently shipping half a feature is.

# Failure Reasons (use exactly one)

| Reason | When to use it |
| --- | --- |
| `context-overflow` | You can no longer reliably recall a rule or file you read earlier in this session; or the task needs more files than you can hold (see budget below) |
| `contradictory-rules` | Two rule files say different things and `AGENTS.md`'s single-source rule doesn't resolve it |
| `missing-business-rule` | A domain condition has no `BR-nnn` and no human confirmed it — you may not invent it |
| `rule-ownership-conflict` | The request contradicts a registered rule owned by another team; only that Owner can amend it (`docs/business/rules.md` Owner column) |
| `unverifiable` | You cannot run the verification the task needs (no container runtime, no DB, no proxy) and the change is not safe to ship unverified |
| `scope-too-large` | The task exceeds the budget below and cannot be split without a human decision |
| `tooling` | A required tool, generator, or dependency is unavailable in this environment |
| `instructions-ambiguous` | The request admits two materially different implementations and asking wasn't possible |

# Budget — When to Stop and Split

These are not suggestions; they are the point at which your output quality is known to degrade.

- **> 12 source files to edit** in one task → split into ordered sub-tasks, each with its own report,
  or declare `FAILED / scope-too-large` and propose the split.
- **> 3 services touched** → stop and ask (`AGENTS.md` → "Ask before cross-cutting refactors").
- **> 6 rule/skill/pattern files needed** for one task → write a checkpoint (below) before file 4.
- **Any rule file you cannot summarize in two lines from memory right now** → re-read it before
  continuing. If re-reading would push out something else you still need → `FAILED /
  context-overflow`.

# Checkpoints — Externalize What You Cannot Hold

For any task run through `ai/skills/deliver-feature/`, keep a running checkpoint in your response
(or, if the tool supports files, in `.ai-run/checkpoint.md`, git-ignored). Update it after every
step of the skill:

```text
CHECKPOINT
Step: 2/5 (contract)
Rules read (token): ARCH-…, BACK-…, SKCREA-…
Decisions locked: PATCH endpoint, DTO OrderCancelRequest, BR-012 applies
Files done: OrderController.java, OrderCancelRequest.java
Files pending: OrderService.java, OrderControllerTest.java, docs/api/error-catalog.md
Unverified so far: none
```

If, when you go to update the checkpoint, you cannot reconstruct a "Decisions locked" line you
wrote earlier — that is the signal. Stop. Status `FAILED / context-overflow`. Report what is done,
what is pending, and the checkpoint. A human or a fresh session can resume from it.

# Subagent Handoff — One Report, Not One Per Agent

This section applies only if you dispatched a subagent (see `ai/agents/README.md`). If you did
not, skip it.

A subagent exists to buy a **separate context window**, nothing else. It is not a separate
signatory. CI parses exactly one `### AI Run Report` per PR — the **caller's**. A subagent never
writes its own `Status:` block into the PR body, and the caller never pastes a subagent's report
in verbatim as if it were a second, independent one.

**Budget crosses the boundary asymmetrically:**

- Files the subagent *read* while exploring do **not** count against the caller's file/service/
  rule-file budget in the section above — that avoided cost is the entire point of delegating.
- Files the subagent *edited* count exactly like files you edited yourself, in `Files-edited` and
  in the 12-file ceiling for the task as a whole.

**Folding the subagent's outcome into your own report:**

- If the subagent reports it completed and verified its slice: you may cite the rule tokens it
  reports reading, but say so in the checkpoint (`Verified via subagent: <task>, tokens: …`) rather
  than presenting them as tokens you personally read. The "do not copy tokens from other reports"
  rule above is about pasting a *different session's* report to fake retention; relaying what a
  subagent you dispatched *in this same task* actually read is a legitimate handoff, not that — but
  it must be labeled, not silently merged in as your own.
- If the subagent reports it could **not** complete its slice (its own version of `FAILED` or
  `DEGRADED`, even if it never formatted it as one): treat that exactly as if you had hit the
  blocker yourself. Do not silently route around it and mark the overall task `OK`. Reflect it in
  your own `Status`, `Reason`, and `Unverified`/`Needs-human` fields — a subagent's unresolved
  failure, absorbed silently by the caller, is precisely the "wrong done" this file exists to
  prevent.
- A subagent that returns only "done" with nothing under "what I did not do" gives you nothing to
  reconcile with. Treat that as `Unverified`, not as a clean result — the omission is the finding.
  
# Stop Conditions — Do Not Continue Past These

1. A rule file contradicts another and neither is marked authoritative for the point in question.
2. A domain condition you are about to write has no `BR-nnn`.
3. A verification command fails and you cannot tell whether it is a regression or the environment.
4. The diff you are producing touches a file you did not read.
5. You are about to hand-edit a file listed in `docs/GENERATED.md`.
6. You are about to remove or rename a public field, endpoint, or topic without explicit instruction.
7. You notice you already "completed" a step you have no evidence of completing.

Each of these ends the task with `FAILED` or `DEGRADED` and a report. None of them is resolved by
guessing.

# Evidence Tokens

Every rule file, skill, and pattern carries a line like
`<!-- evidence-token: PREFIX-nnnnnn -->` (a real one looks like `ARCH-` followed by six
alphanumerics). This example deliberately does not use the real token syntax, so that a blind
`grep` for the marker cannot harvest it as if it were a genuine token. When you read a file,
record its token. The AI Run Report
lists them. `ai/impact-map.yaml` says which tokens are required for which kind of change;
`scripts/check-ai-report.py` fails the PR if one is missing.

The token is not a formality. If it is missing, the most likely explanation is that the file was
never read or did not survive in context — which is exactly the case that should fail. Do not
guess tokens, do not copy them from other reports, do not list files you did not read. A wrong
token is worse than a missing one because it converts a detectable failure into a hidden one.

**What this check does and does not prove.** Citing a token proves the token was obtainable from
the repository. It does not prove the file was read, and it does not prove the rules survived in
context — a single `grep` over `ai/` returns every token without opening anything. The check
reliably catches the common honest failure (a file that was never consulted) and it catches
fabrication. It is a speed bump against a determined bypass, not proof of retention. Treat a
green token check as "no evidence of a context failure", not as "the rules were applied".

One active countermeasure exists: a canary token lives in a file that no rule requires and nothing
links to, so citing it is evidence the report was assembled by scanning for the marker rather than
by reading. Blanket-harvesting every token in `ai/` therefore fails the check.

# AI Run Report — Required Format

Paste this in the PR body (the PR template has the slot). CI parses it; every field is required.
Keep values on one line each. Lists are comma-separated.

```text
### AI Run Report
Status: OK | DEGRADED | FAILED
Reason: none | <one of the failure reasons above>
Model: <model id as reported by the tool, or "unknown">
Task-shape: <how you described it in the ledger, under 8 words>
Rules-read: CAPA-…, BEHV-…, ARCH-…
Skills-applied: SKCREA-…, SKSYNC-…
Patterns-applied: none | PATOUTB-…
Files-edited: <count>
Verified: <exact commands run, comma-separated> | none
Unverified: none | <what was not run and why>
Assumptions: none | <each assumption, comma-separated>
Needs-human: none | <questions>
Checkpoint: n/a | <last checkpoint block, or a path to it>
```

Rules for the report:

- `Status: OK` requires `Unverified: none`, `Assumptions: none`, `Needs-human: none`. Anything
  else is `DEGRADED` by definition — CI enforces this.
- `Status: FAILED` requires a `Reason` that is not `none`, and a `Checkpoint` that is not `n/a`.
- `Rules-read` must contain the token of every file listed under `always_required` in
  `ai/impact-map.yaml`, plus every `requires` entry of every area the diff touched.
- `Verified` lists commands, not adjectives. "tests pass" is not a value; `mvn -q test
  -pl orders-service` is.

# What This Does Not Solve

Be honest about the limits of this file, so nobody over-trusts it:

- It detects **absence** of evidence (a token not cited). It cannot prove a file was *understood*.
- It relies on the agent being truthful in the report. A model that fabricates tokens defeats it —
  which is why tokens are random and never listed in `AGENTS.md`, so fabrication requires reading
  the file anyway.
- Non-determinism is measured (`eval/`), not eliminated.
