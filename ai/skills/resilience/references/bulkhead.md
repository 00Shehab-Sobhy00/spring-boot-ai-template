# Bulkhead

Named after ship compartments: one flooded section must not sink the vessel.

## The Problem It Solves

One slow downstream consumes every thread in the shared pool. Requests that have nothing to do
with that dependency now queue behind it. The whole service goes down because one dependency
got slow — not even down, just *slow*.

## Steps

1. **Identify the risky dependencies** — anything external, anything historically slow, anything
   you don't control.
2. **Give each its own bounded pool** (or a semaphore limiting concurrent calls). The bound is the
   point: once saturated, calls to *that* dependency fail fast while everything else keeps working.
3. **Size it from real concurrency**, not optimism. A pool larger than the downstream can serve
   just moves the queue.
4. **Decide the saturation response.** Reject fast with a typed EXTERNAL error, or fall back —
   never queue unboundedly. An unbounded queue is the bulkhead with a hole in it.
5. **Separate the truly critical paths.** In this stack that also means: don't let a slow HTTP
   dependency starve the threads consuming Kafka, and vice versa.
6. **Instrument saturation** — a pool that's regularly full is a capacity signal, not a mystery.

## Related to Thread Safety

Bulkheads assume the work is safe to run concurrently. If shared mutable state is involved,
review `ai/REVIEW.md` (Thread Safety) first — parallelism on top of a race condition just finds
the bug faster.

## Don't

- Don't use one pool for fast internal calls and slow external ones
- Don't make the queue unbounded — that recreates the original problem
- Don't size pools by copying another service's numbers
