# Event Schemas

> Source of truth for event envelopes and payload versions. Producers and consumers both link here.

## Standard Envelope

```json
{
  "eventId": "uuid — consumer idempotency key",
  "eventType": "orders.order.created",
  "version": 1,
  "occurredAt": "ISO-8601 instant",
  "correlationId": "trace/correlation id",
  "payload": { }
}
```

## Compatibility Rules

- Additive changes (new optional field) — allowed within the same version.
- Breaking changes (remove/rename/retype a field, change semantics) — new `version`, producers
  dual-publish or consumers dual-read during migration, tracked in `ai/PROJECT_MEMORY.md` → Active
  Migrations.
- No PII/secrets in payloads — events fan out to unknown future consumers.

## Schemas

<!-- TODO: replace with your real data — the schemas below are a fictional example -->
### OrderCreated v1

| Field | Type | Notes |
| --- | --- | --- |
| orderId | uuid | aggregate id, also the partition key |
| customerId | uuid | |
| totalAmount | decimal-as-string | avoid float |
| currency | ISO-4217 | |

### PaymentCompleted v1

| Field | Type | Notes |
| --- | --- | --- |
| paymentId | uuid | |
| orderId | uuid | |
| status | enum: COMPLETED, FAILED | |
