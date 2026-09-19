# Optimize a Query

Follows `ai/REVIEW.md` (SQL Efficiency) and `ai/BACKEND_RULES.md` (Persistence).

## Steps

1. **Find the actual query**, not just the repository method — check the generated SQL (logs,
   `show-sql`, or a query plan) rather than guessing from the JPQL/method name.
2. **Check for N+1** — a loop that triggers one query per iteration, usually from lazy-loaded
   associations accessed inside a loop. Fix with a fetch join, an `@EntityGraph`, or a batch query —
   pick whichever matches how sibling queries in this module already solve it.
3. **Check for unbounded loads** — `findAll()` or an unpaginated collection where a projection,
   page, or limit would do. Add pagination per `ai/patterns/rest-api.md` if this is API-facing.
4. **Check indexes** — is the query filtering/joining/ordering on an indexed, selective column?
   Propose an index via a new Liquibase migration if one is missing (never edit a historical
   migration).
5. **Check `SELECT *`** — narrow to the columns actually used where the ORM/mapping allows it.
6. **For cleanup/purge queries specifically** — confirm: an explicit retention condition (never an
   unbounded delete), FK-safe order (children before parents), and batching for large tables. See
   `ai/BACKEND_RULES.md` (Persistence).
7. **Verify** — re-check the query plan/log after the change, and add or update a test that would
   catch a regression (e.g. asserting query count, if this repo has that tooling).

## Don't

- Don't add an index speculatively without evidence the column is actually filtered/joined/ordered
  on
- Don't add caching as a first response to a slow query — that's `ai/patterns/cache-aside.md`, and
  it's a different fix for a different problem (caching hides latency, it doesn't fix an N+1)
- Don't rewrite unrelated queries in the same file while you're in there

## Related

`ai/REVIEW.md` (SQL Efficiency) · `ai/BACKEND_RULES.md` (Persistence) · `ai/patterns/cache-aside.md`
· `ai/skills/database/references/create-entity.md`
