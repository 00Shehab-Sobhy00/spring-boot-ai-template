> Reference pattern. Cross-checked against `ai/ARCHITECTURE.md` and `ai/BACKEND_RULES.md` — those
> files win if anything here conflicts. Formal decision record: `/adr/ADR-003-use-outbox.md`.
<!-- evidence-token: PATOUTB-C7MLOC — cite in the AI Run Report -->

# Pattern: Transactional Outbox

## Intent

Guarantee that a DB write and the resulting event publish either both happen or neither does,
without a distributed transaction across the database and Kafka.

## Problem It Solves

Writing to the database and publishing to Kafka are two separate systems. If you do them as two
independent steps, a crash between them leaves you with a DB change nobody heard about, or an event
about a change that got rolled back.

## Shape in This Codebase

1. A business change and an `outbox_event` row are written **in the same JPA transaction** — same
   atomicity guarantee as any other entity in that transaction.
2. A relay (a scheduled poller, or CDC via Debezium if provisioned) reads unpublished outbox rows
   and publishes them to Kafka.
3. On successful publish, the relay marks the row dispatched (or deletes it, depending on retention
   needs).
4. A cleanup job purges old dispatched rows on a retention window — following the batched, FK-safe
   delete rules in `ai/BACKEND_RULES.md`.

```sql
-- indicative shape only — see the real migration under src/main/resources/liquibase
outbox_event (
  id            uuid primary key,
  aggregate_type varchar,
  aggregate_id   varchar,
  event_type     varchar,
  payload        jsonb,
  created_at     timestamp,
  dispatched_at  timestamp null
)
```

## Idempotency

Consumers must dedupe on `eventId`, because the relay guarantees **at-least-once** delivery, not
exactly-once. A crash between "published to Kafka" and "marked dispatched" will redeliver.

## Pitfalls

- Treating the outbox as a general-purpose queue — it's specifically for reliably crossing the
  DB/Kafka boundary, not a task queue
- Forgetting the cleanup job, letting the outbox table grow unbounded
- Skipping the outbox "because this one event doesn't matter much" — inconsistency has a way of
  mattering eventually; if it truly doesn't matter, question whether it needs to be an event at all

## Related

- `async-events.md`
- Recipe: `ai/skills/kafka/references/outbox-implementation.md`
- Decision record: `/adr/ADR-003-use-outbox.md`
