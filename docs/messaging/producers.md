# Producers

> Register every producer here. Recipe: `ai/skills/kafka/references/producer.md`.

Rules of the road (details in `ai/patterns/async-events.md`):

- Events tied to a DB change publish via the **outbox** (`ai/patterns/outbox-pattern.md`) — no
  direct `send()` inside the business transaction.
- Partition key = aggregate id, so per-aggregate ordering holds.
- Envelope per `schemas.md`: eventId, eventType+version, occurredAt, correlationId, payload.
- No PII/secrets in payloads.

<!-- TODO: replace with your real data — the rows below are a fictional example -->
| Producer (service) | Topic | Via outbox? | Notes |
| --- | --- | --- | --- |
| orders-service | `orders.order.created` | ✅ | relay: scheduled poller, 500ms |
| payments-service | `payments.payment.completed` | ✅ | |
