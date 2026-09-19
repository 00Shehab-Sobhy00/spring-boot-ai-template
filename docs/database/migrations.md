# Migrations (Liquibase)

Authoritative rules live in `ai/BACKEND_RULES.md` (Persistence); this page is the operational
how-to.

## Workflow

1. New changelog file under `src/main/resources/liquibase/changelog/`, named
   `<YYYYMMDD>-<seq>-<short-description>.xml` (match the existing naming in the service).
2. Register it at the end of `master.xml`.
3. **Never modify a historical changelog** — not for typos, not for "it just merged." A follow-up
   migration fixes forward.
4. Test data for integration tests goes under `src/test/resources/liquibase/`, kept in sync with the
   schema.
5. Rollback sections: include them if the service's existing changelogs do; be honest when a change
   isn't cleanly rollbackable (data-destructive) and say what the recovery plan is instead.

## High-Risk Changes

Extra care (and usually an expand/contract, multi-deploy approach) for:

- Dropping/renaming columns still read by running instances during deploy
- Adding NOT NULL to populated tables (backfill first, constrain second)
- Index creation on very large tables (use the DB's online/concurrent mechanism where available)
- Any data migration mixed into a schema migration — prefer separating them

## Cleanup / Purge Scripts

Explicit retention condition, FK-safe order, batched deletes — see `ai/BACKEND_RULES.md`, and the
test rule in `ai/TESTING.md`: assert what was deleted **and** what remains.
