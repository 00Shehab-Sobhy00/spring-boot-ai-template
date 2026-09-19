> Reference pattern. Cross-checked against `ai/REVIEW.md` (Performance section) — that file wins if
> anything here conflicts.
<!-- evidence-token: PATCACH-672QUP — cite in the AI Run Report -->

# Pattern: Cache-Aside (Redis / Redisson)

## Intent

Reduce load on the database / downstream calls for read-heavy, tolerant-of-slight-staleness data —
without introducing caching everywhere by default.

## Before Reaching for This Pattern

Per `ai/REVIEW.md`: **do not add caching unless there is a clear need and an invalidation
strategy.** Caching without a clear invalidation plan is a common source of "why is this data stale"
bugs. Confirm there's an actual, measured hot path first.

## Shape in This Codebase

```text
Read:
  1. Look up the key in Redis
  2. On hit: return it
  3. On miss: read from the DB/repository, populate Redis with a TTL, then return it

Write:
  1. Write to the DB (source of truth)
  2. Invalidate (don't just overwrite) the corresponding cache key
```

## Conventions

- **Key naming**: `<service>:<entity>:<id>` (e.g. `orders:order:1234`) — collisions between
  unrelated entities are a real risk without a namespace
- **TTL**: always set one; "cache forever" is rarely correct and turns a cache into an untracked
  second source of truth
- **Invalidation**: on write, actively evict/update the key — don't rely on TTL expiry alone if
  staleness would be user-visible
- **Serialization**: keep cached payloads small and versioned; a schema change to the cached shape
  needs a plan for old entries still in Redis (key versioning, e.g. `orders:order:v2:1234`, is
  simpler than trying to migrate cached bytes)

## Pitfalls

- Caching a value that changes more often than its TTL implies, producing visibly stale reads
- Cache stampede: many requests miss at once and all hit the DB simultaneously — consider a short
  lock/single-flight for expensive keys
- No plan for what happens if Redis is unavailable — reads should degrade to the DB, not fail the
  request

## Related

- Recipe: `ai/skills/redis-cache/`
- `ai/REVIEW.md` (Performance)
