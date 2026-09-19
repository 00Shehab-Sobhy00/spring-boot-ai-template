---
name: database
description: >
  Persistence work in this repo — adding JPA entities and Liquibase migrations, and diagnosing
  or fixing slow queries. Use when adding a table or column, persisting something new, or when
  a query is slow or the DB is under load.
metadata:
  when_to_use: ["add an entity", "new table", "add a column", "persist this", "this query is slow", "optimize this SQL", "N+1", "why is this endpoint slow"]
---
<!-- evidence-token: SKDATA-NSTRSG — cite in the AI Run Report -->

# Database & Persistence

| You want to... | Read |
| --- | --- |
| Add an entity, table, or column | `references/create-entity.md` |
| Diagnose or fix a slow query | `references/optimize-query.md` |

The two meet constantly: most slow queries trace back to a missing index that should have been
added with the entity. When adding an entity, think about how it will be queried; when fixing a
query, the fix is often a new migration.

## Rules That Apply to Both

**1. Never modify a historical Liquibase changelog.** Not for a typo, not for something that
merged an hour ago. Always a new changelog file, registered in `master.xml`. Fix forward.

**2. Indexes are decided with evidence, not intuition.** Add one when you know a column is
filtered, joined, or ordered on — and verify with the query plan afterwards. Speculative indexes
cost write performance for nothing.

**3. Business logic never lives in repositories or entities.** Custom queries live in the
persistence layer; the rules that use them live in services. See `ai/ARCHITECTURE.md`.

**4. Cleanup and purge queries have three requirements**, always: an explicit retention
condition (never an unbounded delete), FK-safe order (children before parents), and batching on
large tables. The test must assert both what was deleted **and** what survived.

**5. Entities never leave the repository layer.** No entity is returned from a controller, and
no DTO reaches persistence.

## Don't

- Don't edit a historical migration
- Don't reach for caching as the first response to a slow query — caching hides latency, it doesn't
  fix an N+1
- Don't use `findAll()` where a projection, page, or limit would do
- Don't mix a JPA entity with an in-memory/live state object

## Related

`ai/BACKEND_RULES.md` (Persistence) · `docs/database/migrations.md` ·
`docs/database/schema-conventions.md` · `ai/REVIEW.md` (SQL Efficiency) ·
`ai/patterns/cache-aside.md`
