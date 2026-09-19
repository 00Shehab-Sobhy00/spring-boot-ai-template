> Reference pattern. Cross-checked against `ai/ARCHITECTURE.md` — that file wins if anything here
> conflicts.
<!-- evidence-token: PATSAGA-EFQERB — cite in the AI Run Report -->

# Pattern: Saga (Cross-Service Transaction)

## Intent

Coordinate a business transaction that spans multiple services/databases, where a real distributed
transaction isn't available (see `ai/ARCHITECTURE.md` — no direct DB access across services).

## When to Use

- A single business operation requires multiple services to each commit a local change
- Partial success is possible and must be compensated, not just retried blindly

## When Not to Use

- Everything needed fits inside one service's transaction — just use `@Transactional`
- A simple fire-and-forget notification — that's `async-events.md`, not a saga

## Choreography vs Orchestration

| | Choreography | Orchestration |
| --- | --- | --- |
| How it works | Each service reacts to the previous service's event and emits its own | A dedicated orchestrator/service calls each step and tracks state |
| Good for | A small number of steps, loosely coupled | Many steps, need visibility/retries in one place |
| Downside | Hard to see the whole flow in one place as it grows | Orchestrator becomes a coupling point / single place of failure |

Default to **choreography** for 2–3 steps. Prefer **orchestration** once a saga has enough steps
that "what state is this order actually in?" becomes hard to answer by reading event logs.

## Compensating Actions

Every forward step that can partially succeed needs an explicit compensating action:

```text
Reserve inventory     -> compensate: Release inventory
Charge payment        -> compensate: Refund payment
Create shipment        -> compensate: Cancel shipment
```

Compensations must be idempotent — the same compensation may be triggered more than once.

## Pitfalls

- Treating a saga as "just retry the whole thing" instead of designing explicit compensations
- No timeout/give-up path — a saga stuck waiting forever for a step that will never complete
- Compensations that aren't idempotent, causing double-refunds or double-releases on retry

## Related

- `async-events.md`
- Microservice boundary rules: `ai/ARCHITECTURE.md`
