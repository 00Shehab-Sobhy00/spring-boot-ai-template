> Reference pattern. Cross-checked against `ai/ARCHITECTURE.md` and `ai/BACKEND_RULES.md` — those
> files win if anything here conflicts.
<!-- evidence-token: PATASYN-U6LL9A — cite in the AI Run Report -->

# Pattern: Async / Domain Events

## Intent

Tell other services "something happened" without coupling to who's listening, using Kafka as the
backbone.

## When to Use

- Other services need to react to a state change but don't need to block the caller
- You want to decouple producer and consumer lifecycles/scaling
- The fact is useful to more than one future consumer (fan-out)

## When Not to Use

- The caller needs a synchronous answer right now (use a REST/Feign call)
- Strong read-after-write consistency is required within the same request (event delivery is
  asynchronous by nature)

## Shape in This Codebase

```text
Service (after a successful business transaction)
  -> writes an outbox row in the SAME DB transaction   (see outbox-pattern.md)
      -> a relay/publisher reads the outbox and publishes to Kafka
          -> Consumer service(s) process the event, idempotently
```

Direct `KafkaTemplate.send(...)` calls from inside the same transaction as the business write are
avoided in favor of the outbox — see `outbox-pattern.md` for why.

## Event Envelope

Every event carries, at minimum:

- `eventId` (UUID, used for consumer-side idempotency)
- `eventType` + `version` (e.g. `order.created.v1`)
- `occurredAt`
- `correlationId` / trace id
- a versioned `payload`

Full schema conventions: `docs/messaging/schemas.md`. Topic catalog:
`docs/messaging/kafka-topics.md`.

## Pitfalls

- Publishing directly inside the business transaction without an outbox — a Kafka publish can
  succeed while the DB commit rolls back, or vice versa
- Consumers that assume in-order, exactly-once delivery — design for at-least-once and out-of-order
  arrival
- Breaking payload compatibility on a topic without a version bump

## Related

- `outbox-pattern.md`, `saga-pattern.md`
- Recipes: `ai/skills/kafka/references/producer.md`, `ai/skills/kafka/references/consumer.md`,
  `ai/skills/kafka/references/topic.md`
- `docs/messaging/`
