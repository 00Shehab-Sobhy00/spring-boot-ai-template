# Prompt: Performance Review

Paste this when reviewing a service, endpoint, or change specifically for performance.

---

Review `<scope: endpoint / service / diff>` for performance. Ground every finding in this codebase's
actual code — no generic advice.

**Check, in order of typical impact:**

1. **Query behavior** — N+1s from lazy associations in loops, unbounded `findAll`s, missing
   pagination, `SELECT *` where a projection would do, missing/unselective indexes. (Deep checklist:
   `ai/skills/database/references/optimize-query.md`.)
2. **Remote calls** — repeated Feign/HTTP calls in loops, missing timeouts, sequential calls that
   could be avoided or batched, retry storms (app-level retries multiplied by mesh-level retries —
   `ai/patterns/retry-pattern.md`).
3. **Transactions** — transaction boundaries wider than needed, remote calls held inside a DB
   transaction, long-running transactions blocking connections.
4. **Memory & allocation** — loading large collections into memory, large payloads logged by
   default, unbounded caches or maps acting as accidental caches.
5. **Threading & blocking** — blocking calls on hot paths, shared mutable state, thread-pool
   exhaustion risks from slow downstreams (`ai/REVIEW.md`, Thread Safety).
6. **Caching** — only after the above: is there a *measured* hot path that justifies cache-aside
   (`ai/patterns/cache-aside.md`)? Flag existing caches with no invalidation strategy as risks, not
   wins.

**Output format:**

- **Findings** — each with: location, why it's a problem, estimated impact (high/medium/low), and
  the specific fix
- **Measurements needed** — anything you'd want profiled/measured before acting
- **Non-issues** — things that look suspicious but are fine here, and why (prevents re-litigating
  them next review)

Do not propose micro-optimizations that hurt readability unless the measured impact justifies them
(`ai/AI_BEHAVIOR.md`, How to Decide).
