---
name: redis-cache
description: >
  Add a cache-aside layer with Redis/Redisson for a specific read path, with a clear key
  convention, TTL, and invalidation strategy. Trigger when the user asks to cache something or
  speed up a hot read path with Redis.
metadata:
  when_to_use: ["cache this", "add Redis caching", "speed up this endpoint with a cache"]
---
<!-- evidence-token: SKREDI-OGKMLQ — cite in the AI Run Report -->

# Add Redis Caching (Cache-Aside)

Follows `ai/patterns/cache-aside.md` and `ai/REVIEW.md` (Performance: don't cache without a clear
need + invalidation plan).

## Steps

1. **Confirm the need.** What's the measured hot path, and how stale can the data be before it
   matters? If there's no clear answer, say so and suggest measuring first rather than caching
   speculatively.
2. **Key convention** — `<service>:<entity>:<id>` (namespaced, matching this repo's existing Redis
   key patterns if any already exist — check for a `redisson/` config or existing cache usage
   first).
3. **Read path** — look up the key; on miss, read from the source of truth (repository/client),
   populate the cache with an explicit TTL, then return.
4. **Write path** — write to the source of truth first, then actively invalidate (not just
   overwrite) the corresponding key(s). If a write affects a range/list of cached keys, invalidate
   all of them, or key-version instead of trying to track every affected entry.
5. **TTL** — set one deliberately based on how stale the data can tolerably be; don't default to
   "forever."
6. **Failure mode** — if Redis is unavailable, the read path should degrade to the source of truth,
   not fail the request.
7. **Tests** — cover cache hit, cache miss + populate, and invalidation-on-write. If this repo has a
   way to test against a real Redis (Testcontainers), use it for the invalidation path.

## Don't

- Don't cache without an invalidation plan — that's the #1 way this pattern goes wrong
- Don't let cached payload shape drift from the DB shape without a versioning plan for old cached
  entries
- Don't introduce a second caching library/approach if Redisson (or whatever's already configured)
  already covers the need

## Related

`ai/patterns/cache-aside.md` · `ai/REVIEW.md` (Performance)
