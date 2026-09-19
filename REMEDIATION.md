# Remediation Changelog

Fixes applied to this template after an end-to-end integration test: a real five-service Spring
Boot repository (93 Java files, six business rules owned by three teams) with the template
installed, six workflow branches run through every check — one honest run, one correct refusal,
and four adversarial runs.

Every fix below was verified against that repository using the files in this template, not a copy.

---

## Fixed

### 1. The business-rule check rewarded silence over disclosure

`ai/impact-map.yaml`, `scripts/check-docs-impact.py`

The `business-rule` rule triggered on the *string* `BR-nnn` appearing in an added diff line. An
agent that silently changed a registered rule's condition and omitted the `// BR-nnn` comment
never tripped it and merged green; an agent that honestly annotated the same change was blocked.
The mechanism selected against the careful agent.

Added a second rule, `business-rule-drift`, working from a different signal. It parses the
registered ids out of `docs/business/rules.md`, then flags any diff hunk that **removes or
modifies** lines within three lines of a `BR-nnn` annotation. Omitting the comment no longer
helps — the annotation is still in the context of the hunk that was disturbed.

Requires the new `scope: enforcement` in `check-docs-impact.py`. Attribution is proximity-bounded
on purpose: an early version scanned the whole hunk and swept in every `BR` comment in the file,
burying the real one under false "not mentioned" warnings on a legitimate PR.

### 2. The `api` rule contradicted the feign-client skill

`ai/impact-map.yaml`

`ai/skills/feign-client/SKILL.md` step 3 requires dedicated wire DTOs for a downstream contract.
Those land in `client/dto/`, which the `api` rule matched, classifying the PR as a REST API change
and demanding the `create-rest-api` evidence token — for a file the agent correctly never read.
CI then emitted `INSTRUCTION-RETENTION-FAILURE` with a diagnosis that was simply wrong, and the
agent had no compliant way out: citing the token violates `ai/CAPACITY.md`, renaming the package
violates the skill.

The `api` rule now excludes `client/dto` and `adapter/dto`. The `feign` rule claims those paths
instead, so they still require a components/networking doc update — just not an API one.

### 3. ArchUnit shipped pointed at a package that does not exist

`enforcement/archunit/ArchitectureRulesTest.java`, `enforcement/archunit/README.md`

`CONTROLLERS` was `..controllers..` (plural) while every other layer glob was singular. Against
the conventional Spring `controller` layout the controller layer matched zero classes, so three
rules and one layer of the layered-architecture rule passed vacuously. Verified by injecting a
Controller-to-Repository violation: shipped globs found 0, corrected globs found 2.

The README claimed `base_package_is_not_empty` guarded against this. It did not — that check only
asserts the *overall* import is non-empty, which stays true with 93 classes imported and one glob
wrong.

- `CONTROLLERS` is now `..controller..`, with `CONTROLLERS_ALT` covering the plural spelling; all
  controller rules use `resideInAnyPackage(...)`.
- New `layer_globs_all_match_classes` asserts every named layer matched at least one class and
  names the empty ones.
- `main()` now runs every rule, including `controllers_are_annotated` and both guards — previously
  the eval path was weaker than the JUnit path.
- Fixed a comment that described an unbounded-delete rule sitting above an annotation rule.
- The install header now tells you to set the `package` declaration to match the directory.

### 4. The topic-catalog generator found nothing and exited 0

`scripts/generate-topic-catalog.py`

Against a repo with ten registered topics across five services it reported `0 topic/role pairs`,
wrote a catalogue saying `_none found_`, and **exited 0**. Two independent causes:

- The topic regex allowed exactly three dot-separated segments, so versioned names
  (`ledger.entry.posted.v1`) never matched.
- The produce heuristics only saw an inline string literal on the same line as a `send(` call, or
  a constant literally named `TOPIC*`. The conventional holder-class style
  (`send(LedgerTopics.ENTRY_POSTED, ...)`) was invisible — a well-structured codebase produced an
  empty catalogue.

Now resolves `static final String` declarations into a constant map and follows references at the
call site, accepts an optional `.v<n>` segment and `.retry`, and exits non-zero when a repo that
clearly uses Kafka yields no topics. On the test repo this went from 0 to 7 resolved pairs, and
the stale-row cross-check began firing for the first time.

### 5. The evidence-token check was defeated by two greps

`scripts/check-ai-report.py`, `ai/CAPACITY.md`, `ai/.evidence-canary.md`

`CAPACITY.md` claimed fabricating tokens "requires reading the file anyway". It does not: one
`grep -rho 'evidence-token: ...' ai/` harvests every token without opening anything. In testing
the naive version was caught only by accident, because it also picked up a literal placeholder
written inside `CAPACITY.md`'s own prose. Filtering that one string produced 34 valid tokens and
a green report.

Removing the placeholder alone would have made harvesting *easier*, so a deliberate replacement
was added: `ai/.evidence-canary.md` holds a real-looking token, is required by no rule and linked
from nowhere, and `check-ai-report.py` fails any report citing it. A blanket scan picks it up; a
genuine reader never encounters it.

`CAPACITY.md` now states the actual guarantee — a token proves the file was reachable, not that it
was read or retained.

### 6. `Model: human` disabled every integrity check for one word

`scripts/check-ai-report.py`

Nothing can verify the claim, but the bypass should cost an attribution. `Model: human` now
requires `Attested-by: @<handle>` in the PR body. CI should additionally verify the handle is a
repository collaborator.

### 7. The eval harness scored the wrong repository

`scripts/check-docs-impact.py`, `scripts/check-ai-report.py`

Both scripts anchored `ROOT` to their own location and passed `cwd=ROOT` to every git call.
`eval/run.sh` invokes them from a worktree of a *different* repository, so they diffed the
template instead of the agent's work and recorded `docs-impact: pass` for every run — inflating
compliance across the board and silently under-reporting the "not capable" list.

`ROOT` now resolves via `git rev-parse --show-toplevel` from the working directory, with
`TEMPLATE_TARGET_ROOT` as an explicit override. `MAP` still resolves against the script's own tree.

Detection uses git rather than probing for a `.git` directory, because in a worktree — exactly how
`eval/run.sh` runs — `.git` is a file, and the first version of this fix silently fell back.

### 8. The `forbid` check in the eval scorer never fired

`eval/score.py`

`re.search(rx, patch)` was called without `re.M` while the task patterns are `^`-anchored to match
added diff lines, so `^` only ever matched the start of the whole patch string. Three seeded runs
whose diffs all contained a Controller holding a Repository — the exact layering violation the
template exists to prevent — scored 100% compliance and were rated **trusted**. With `re.M` the
same runs score 0% and are correctly rated not-capable.

### 9. The components inventory over-reported

`scripts/generate-components-inventory.py`

- `@RestControllerAdvice` classes were counted as controllers, because `@RestController` is a
  prefix of the annotation. Now uses a `(?![A-Za-z])` boundary.
- Any topic literal in a `*Topics`/`*Publisher` file was reported as published, so declared-but-
  unsent constants appeared as outbound contracts that did not exist. On the test repo this
  produced phantom entries for three services. A topic is now only reported when a `send`/
  `publish` call site references it, by literal or resolved constant. Genuinely dynamic sends (an
  outbox relay using `event.getTopic()`) stay unresolved rather than guessed.

### 10. Missing failure reason

`ai/CAPACITY.md`, `scripts/check-ai-report.py`

The reason enum had no value for "the request contradicts a registered rule owned by another
team", which is the outcome the grounding step is designed to produce. Added
`rule-ownership-conflict`.

---

## Bug introduced during remediation, and caught

`business-rule-drift` carries `code: ''` because it is content-triggered, and an empty regex
matches every path. `check-ai-report.py` only skipped `scope: content`, so the new rule demanded
the `sync-docs` token on every PR. It now skips any non-path scope generically.

---

## Deliberately not changed

- **`Docs-Impact: none — <reason>` still bypasses the documentation checks.** It is a designed
  escape hatch, and hardening it needs a reviewer-identity check CI performs, not a script change.
- **Markdown checks still pass a controller calling a Feign client directly.** That case is what
  the ArchUnit rules exist for, and they catch it. It is the intended division of labour.
- **The `ledger` rule still fires on nearly every PR.** It is `severity: warn` and noisy, but
  changing its cadence is a judgement call for whoever adopts the template.

---

## Verification

All checks pass on this template: links, skill frontmatter, impact-table sync, context budget,
markdownlint (111 files, 0 errors). `ArchitectureRulesTest.java` compiles under javac 21.

Behaviour was confirmed on the integration repository with these exact files:

| Scenario | Before | After |
| --- | --- | --- |
| Honest PR adding a Feign client and wire DTO | blocked by a false retention failure | passes |
| Silent change to a registered rule's condition | all checks green | blocked, names the rule and file |
| Same change, annotated | blocked | blocked |
| Report built from harvested tokens | passed | blocked by the canary |
| `Model: human` with no attribution | passed | blocked |
| Controller calling a client directly | caught by ArchUnit only | unchanged |
| Correct refusal on a cross-team rule conflict | worked, imprecise reason | works, own reason code |
| Eval run with an undocumented controller | recorded pass | recorded fail |
| Eval runs containing the forbidden layering pattern | rated trusted | rated not-capable |
