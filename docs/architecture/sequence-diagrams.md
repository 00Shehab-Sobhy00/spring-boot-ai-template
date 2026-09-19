# Sequence Diagrams

> Template — one diagram per business-critical flow. Add a diagram whenever a flow crosses more than
> two services or involves the outbox/saga machinery; those are the flows nobody can hold in their
> head from code alone.

## Example: Order Creation (with outbox)

<!-- TODO: replace with your real data — the flow below is a fictional example -->
```mermaid
sequenceDiagram
  participant C as Client
  participant O as orders-service
  participant DB as Orders DB
  participant R as Outbox Relay
  participant K as Kafka
  participant P as payments-service

  C->>O: POST /v1/orders
  O->>DB: tx { insert order + insert outbox_event }
  O-->>C: 201 Created
  R->>DB: poll undispatched outbox rows
  R->>K: publish orders.order.created (key=orderId)
  R->>DB: mark dispatched
  K-->>P: orders.order.created
  P->>P: process idempotently (dedupe on eventId)
```

## Flows to Document Here

- [ ] Order creation / fulfillment saga (with compensations — see `ai/patterns/saga-pattern.md`)
- [ ] Payment webhook handling (external → internal boundary)
- [ ] The DLQ replay path (`docs/messaging/dlq.md`)
