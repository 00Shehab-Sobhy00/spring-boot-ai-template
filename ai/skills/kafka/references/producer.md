# Add a Kafka Producer

Follows `ai/patterns/async-events.md` and `docs/messaging/producers.md`. If the publish must be
atomic with a DB write (it usually must), use the outbox — see step 1.

## Steps

1. **Decide: outbox or direct?** If the event describes a state change committed to this service's
   DB, publish **via the outbox** (`ai/skills/kafka/references/outbox-implementation.md`), not a
   direct `KafkaTemplate.send` inside the transaction. Direct publishing is only acceptable for
   events with no DB-side transaction to stay consistent with (rare).
2. **Topic** — use an existing topic from `docs/messaging/kafka-topics.md` if one fits; if a new
   topic is needed, follow `ai/skills/kafka/references/topic.md` first and register it in the
   catalog.
3. **Envelope** — `eventId` (UUID), `eventType` + version (`order.created.v1`), `occurredAt`,
   `correlationId`, versioned payload. Full conventions: `docs/messaging/schemas.md`.
4. **Partition key** — choose deliberately (usually the aggregate id) so events for the same
   aggregate stay ordered on one partition. Document the choice in the topic catalog entry.
5. **Serialization** — match the repo's existing serializer setup (JSON/Avro/whatever is
   configured); don't introduce a second serialization format on the same cluster without an ADR.
6. **Failure handling** — producer-side errors must be visible: log with correlation id, and surface
   metrics if the repo has them. Never silently drop a failed publish.
7. **Tests** — a unit test for the event mapping/envelope, and an integration test (embedded Kafka
   or Testcontainers) asserting the message actually lands on the topic with the right key and
   payload.
8. **Docs** — register/refresh the event in `docs/messaging/kafka-topics.md` and
   `docs/messaging/schemas.md`.

## Don't

- Don't publish inside the business transaction without an outbox — see
  `ai/patterns/outbox-pattern.md` for why
- Don't put PII or secrets in event payloads that fan out to unknown future consumers
- Don't break payload compatibility on an existing topic — bump the event version instead

## Related

`ai/patterns/async-events.md` · `ai/patterns/outbox-pattern.md` ·
`ai/skills/kafka/references/topic.md` · `docs/messaging/producers.md` · `docs/messaging/schemas.md`
