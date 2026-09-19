---
name: create-merge-request
description: >
  Prepare and open a merge request or pull request from finished local work — resolve the source
  and target branch, write a factual description, and create it via the configured MCP server, the
  CLI, or by handing the user a ready-to-paste description. Use when asked to open an MR/PR, publish
  a branch for review, or finish a feature by submitting it.
metadata:
  when_to_use: ["open a merge request", "create an MR", "open a PR", "publish this for review", "submit the feature", "raise a pull request"]
---
<!-- evidence-token: SKCREA-1FUOLI — cite in the AI Run Report -->

# Create a Merge Request

The last step of `deliver-feature`, and only ever the last step: an MR opened before the work is
verified wastes a reviewer's attention, which is the scarcest resource in the process.

## Preconditions — check, don't assume

Stop and say so if any of these fail. Do not open the MR anyway with a caveat buried in the body.

- [ ] Implementation complete, tests written and passing
- [ ] `review-pr` run against the diff, blockers resolved
- [ ] `sync-docs` close-out done — docs land in the *same* MR as the code
- [ ] Commits pushed to the remote (an MR from unpushed commits is empty)
- [ ] No unrelated changes in the diff

## Resolve the target

1. **Source branch** — the current branch. If it's `main`/`master`/`develop`, stop: there's nothing
   to merge, the work belongs on a feature branch (`deliver-feature` Step 1).
2. **Target branch** — from the user, or the repository's documented default. If it can't be
   verified safely, **ask** rather than guessing; merging into the wrong branch is expensive to
   undo.
3. **Project id** — in this order: user-provided value → the id recorded in this repo's
   configuration → the `origin` remote, if it clearly points at the same project → the relevant
   environment variable → ask.

Never invent a project id, branch name, or MR URL. A fabricated link is worse than no link, because
it looks like success.

## Create it

Whichever path is available, in order of preference:

1. **MCP server**, if one is configured for your forge (see `ai/agents/README.md` for the config
   shape). Call it with the resolved source, target, and project id.
2. **CLI** — `glab mr create` / `gh pr create`, if the tool is installed and authenticated.
3. **Neither available** — don't fail silently. Output the complete title and description as text,
   plus the exact command or the "new merge request" URL, so the user finishes it in one paste.

If a configured MCP server is unavailable or unauthenticated, say exactly what's missing and stop.
Don't fall back to a fabricated result.

## Write the description

Factual, short, reviewer-first. What a reviewer needs is what changed, what proves it works, and
where to look hardest.

```text
## What & why
<one paragraph; link the ticket; cite BR-nnn if a business rule is involved>

## Changes
- <layer-level bullets, not a file list — the diff already lists files>

## Verification
- <exact commands run and their outcome>
- <what was NOT verified, and why>

## Risks / rollout
- <breaking changes, migration ordering, flag, or "none">
```

Reuse the `sync-docs` close-out block for the docs line and the review output for the risk line —
they were written for exactly this.

## Don't

- Don't open an MR to make progress visible; that's what a draft branch is for
- Don't summarize the diff file-by-file — reviewers can read a diff, they can't read your intent
- Don't claim tests pass without having run them in this session
- Don't include secrets, tokens, internal hostnames, or customer data in the description
- Don't mark it ready for review when the checklist above has an unticked box — open it as a draft
  and say why

## Related

`ai/skills/deliver-feature/` · `ai/skills/review-pr/` · `ai/skills/sync-docs/` ·
`.github/PULL_REQUEST_TEMPLATE.md` (the checklist reviewers use)
