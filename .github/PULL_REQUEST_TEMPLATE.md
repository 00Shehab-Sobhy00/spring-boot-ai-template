## What & why

<!-- One paragraph. Link the ticket. If a business rule is involved, cite its BR-nnn id. -->

## Checklist (the same one `ai/REVIEW.md` reviewers use)

- [ ] Layering respected — no Controller→Repository, no entity in an API response
  (`ai/ARCHITECTURE.md`; `enforcement/archunit/` fails the build if not)
- [ ] Every new outbound call has explicit connect + read timeouts
- [ ] DB write + event publish goes through the outbox
- [ ] Scheduled jobs are idempotent or take a distributed lock
- [ ] Logs carry the correlation id, including async paths; no secrets/PII
- [ ] Migrations: new changelog file only; purge SQL is bounded, FK-safe, batched
- [ ] Tests: business rules, failure paths, and the concurrency case where relevant
  (`ai/TESTING.md`)
- [ ] Public contracts backward compatible (or the break is called out below)

## Docs sync (`ai/skills/sync-docs/SKILL.md`)

<!-- Paste the close-out block. CI fails if code in a documented area changed and its docs did
     not change *substantively*. For a genuinely doc-neutral PR, uncomment the next line. -->
<!-- Docs-Impact: none — <reason> -->

**Updated:**

-

**Needs a human:**

-

Knowledge captured: <!-- PROJECT_MEMORY / ADR / none -->
Ledger: <!-- task shape → count -->

## AI Run Report (`ai/CAPACITY.md` — parsed by CI, every line required)

<!-- If no AI agent produced this change: Status: OK, Model: human, Rules-read: n/a -->

### AI Run Report

Status:
Reason: none
Model:
Task-shape:
Rules-read:
Skills-applied:
Patterns-applied: none
Files-edited:
Verified:
Unverified: none
Assumptions: none
Needs-human: none
Checkpoint: n/a

<!-- DEGRADED can only merge with a human's explicit acceptance — uncomment and give the reason: -->
<!-- Accepted-Degraded: <reason> -->

## Breaking changes / rollout

<!-- none | describe, with the flag or phased plan (ai/patterns/feature-flags.md) -->
