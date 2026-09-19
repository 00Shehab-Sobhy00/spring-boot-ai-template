# ADR-001: Use Kafka for Inter-Service Events

- **Status**: Accepted
- **Date**: 2024-01-15 <!-- template date — replace with yours -->
- **Deciders**: Platform team

## Context

Services need to react to each other's state changes without tight synchronous coupling: multiple
consumers per event, independent scaling, and tolerance for a consumer being down without losing
facts. Direct REST fan-out couples the producer to every consumer and makes the producer's
availability depend on all of theirs.

## Options Considered

1. **Kafka** — durable log, per-partition ordering, replay, mature Spring integration. Cons:
   operational weight, at-least-once semantics push idempotency onto consumers.
2. **RabbitMQ** — simpler ops, rich routing. Cons: weaker replay/retention story for event-log use;
   ordering guarantees less natural for aggregate streams.
3. **Synchronous REST fan-out** — no new infra. Cons: producer availability coupled to every
   consumer; no replay; fan-out logic accretes in producers.
4. **DB-as-queue polling** — no new infra. Cons: doesn't scale across consumers, chatty, reinvents a
   log badly.

## Decision

Kafka, as the platform-wide backbone for inter-service events. Topics follow the catalog in
`docs/messaging/kafka-topics.md`; envelope per `docs/messaging/schemas.md`; every consumer is
idempotent because delivery is at-least-once.

## Consequences

- Positive: decoupled lifecycles, replayability, per-aggregate ordering via keys, one paved road for
  async.
- Negative / accepted costs: cluster operations; consumers must dedupe (eventId); developers must
  design for out-of-order and duplicate delivery.
- Follow-ups: `ai/patterns/async-events.md`, consumer/producer skills, retry + DLQ policies
  (`docs/messaging/`), and ADR-003 for publish atomicity.
