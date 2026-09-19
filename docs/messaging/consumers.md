# Consumers

> Register every consumer here. Recipe: `ai/skills/kafka/references/consumer.md`.

Group naming: `<service>.<purpose>` (e.g. `payments-service.order-intake`).

Rules of the road:

- **At-least-once**: every consumer dedupes on `eventId` or is naturally idempotent — state which in
  the table.
- Ordering only within a partition; never across partitions.
- Transient failures → retry per `retry-policy.md`; permanent failures → DLQ per `dlq.md`. Never
  infinite in-place retries.

<!-- TODO: replace with your real data — the rows below are a fictional example -->
| Consumer (service) | Group | Topic | Idempotency strategy | DLQ |
| --- | --- | --- | --- | --- |
| payments-service | `payments-service.order-intake` | `orders.order.created` | processed_events table on eventId | `orders.order.created.dlq` |
| orders-service | `orders-service.payment-status` | `payments.payment.completed` | naturally idempotent (status upsert) | `payments.payment.completed.dlq` |
