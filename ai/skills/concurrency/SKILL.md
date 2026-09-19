---
name: concurrency
description: >
  Handle concurrent access safely — distributed locks, optimistic and pessimistic locking,
  transaction isolation, and idempotency. Use when multiple instances or requests can touch the
  same record, when a scheduled job runs on every replica, or when you see lost updates.
metadata:
  when_to_use: ["distributed lock", "Redisson", "race condition", "lost update", "optimistic locking", "two instances running the same job", "isolation level", "duplicate processing"]
---
<!-- evidence-token: SKCONC-WH4BEP — cite in the AI Run Report -->

# Concurrency & Locking

In a multi-replica service, "it works on one instance" proves nothing. Every scheduled job runs
on every pod; every record can be updated by two requests at once.

## Pick the Right Mechanism

Reaching for a distributed lock first is the common mistake — it's the heaviest option and often
unnecessary.

| Situation | Use | Why |
| --- | --- | --- |
| Two requests update the same row; conflict is **rare** | **Optimistic locking** (`@Version`) | No lock held; conflict detected at commit, caller retries |
| Conflict is **likely**, and the update is short | **Pessimistic lock** (`SELECT … FOR UPDATE`) | Serialize at the DB; correct but blocks |
| Claim rows from a queue-like table across replicas | `FOR UPDATE SKIP LOCKED` | Each worker takes different rows; no contention |
| A scheduled job must run **once across all pods** | **Distributed lock** (Redisson) | The DB can't express "only one instance runs this" |
| The same message/request may arrive twice | **Idempotency key**, not a lock | Cheaper and more correct than locking |
| Counter or flag under contention | Atomic DB update (`SET x = x + 1`) | One statement, no read-modify-write race |

**Ask first: can this be made idempotent instead of locked?** Idempotency scales; locks are a
bottleneck and a failure mode.

## Distributed Locks (Redisson)

Only when there is genuinely no DB-level way to express the constraint. Rules:

1. **Always set a lease time.** A lock held by a pod that dies is a lock nobody can release. Lease
   time must exceed the worst-case execution time — or use a watchdog that extends it while alive.
2. **Always acquire with a timeout.** Blocking forever on a lock turns contention into a hang.
3. **Always release in `finally`.** And only if you actually hold it.
4. **Never hold a lock across a network call or a long transaction.** Same rule as any lock.
5. **The lock is not a transaction.** Acquiring a lock does not make your DB writes atomic, and
   committing does not release the lock. Reason about both separately.
6. **Assume the lock can be lost.** Redis failover, GC pause, network partition — a distributed
   lock is a strong hint, not a guarantee. Where correctness truly depends on it, add a
   database-level guard (unique constraint, conditional update) as the real safety net.

## Transaction Isolation

Default isolation (usually READ_COMMITTED) permits non-repeatable reads and phantom reads.

- Read-modify-write inside one transaction is **not** safe by default — that's what `@Version`
  or `FOR UPDATE` is for.
- Raising the isolation level is rarely the right fix: it trades a subtle bug for lock contention
  and deadlocks. Prefer explicit locking or an atomic statement.
- Never assume a `@Transactional` method is serialized with itself. It isn't.

## Non-Negotiables

**1. Every scheduled job must be safe to run on every replica.** Either it's idempotent, or it
takes a distributed lock, or it's a leader-elected singleton. "We only run one pod" is not a
design — it's an accident waiting for an autoscaler.

**2. Consistent lock ordering.** If an operation takes two locks, always in the same order —
sorted by key. Otherwise: deadlock.

**3. Concurrency bugs need concurrency tests.** A sequential test proves nothing. Use a
`CountDownLatch` to release N threads simultaneously and assert exactly one winner. See
`ai/TESTING.md`.

**4. No shared mutable state in singleton beans.** Spring beans are singletons by default;
request-scoped data in a field is a race in production and invisible in local testing.

## Don't

- Don't use a distributed lock where an idempotency key or a unique constraint would do
- Don't hold any lock during I/O
- Don't acquire a lock without both a lease time and an acquisition timeout
- Don't rely solely on a distributed lock for correctness — back it with a DB constraint
- Don't raise the isolation level to paper over a missing `@Version`

## Related

`ai/REVIEW.md` (Thread Safety) · `ai/TESTING.md` (concurrency tests) · `ai/skills/database/` ·
`ai/skills/redis-cache/` · `ai/patterns/outbox-pattern.md` (SKIP LOCKED relay)
