---
name: kafka
description: >
  All Kafka and messaging work in this repo — producing events, consuming them, creating topics,
  the transactional outbox, and dead-letter queues. Use when publishing or handling events,
  adding a topic or listener, or dealing with poison messages and stuck consumers.
metadata:
  when_to_use: ["publish an event", "add a consumer", "new topic", "outbox", "DLQ", "poison message", "consumer is stuck", "Kafka"]
---
<!-- evidence-token: SKKAFK-BLPYC4 — cite in the AI Run Report -->

# Kafka & Messaging

One skill covering the whole messaging surface. Pick the task below and read **only** that
reference — they load on demand, so the ones you don't need cost nothing.

## Pick your task

| You want to... | Read |
| --- | --- |
| Publish a domain event | `references/producer.md` |
| Handle/react to an event | `references/consumer.md` |
| Create or register a topic | `references/topic.md` |
| Make a DB write + publish atomic | `references/outbox-implementation.md` |
| Deal with poison messages / a blocked partition | `references/dead-letter-queue.md` |

Most tasks touch two of these. Adding a new event usually means **topic → outbox → producer**;
handling one means **consumer → dead-letter-queue**.

## Rules That Apply to Everything Here

Read these before opening any reference — they're the invariants the whole messaging layer
depends on, and every reference assumes them.

**1. Delivery is at-least-once. Always.**
Every consumer must dedupe on `eventId` or be naturally idempotent. Duplicates are not an edge
case — they are guaranteed to happen eventually. Never design as if exactly-once exists.

**2. A DB write plus a publish goes through the outbox.**
Publishing directly inside the business transaction can emit an event for a change that rolled
back, or commit a change nobody heard about. See `ai/patterns/outbox-pattern.md` for why this is
not negotiable, and `/adr/ADR-003-use-outbox.md` for the decision record.

**3. Ordering holds only within a partition.**
And only if the producer keys by aggregate id. Never assume ordering across partitions or topics.

**4. Every topic is registered in the catalog.**
`docs/messaging/kafka-topics.md` is the source of truth. A topic that isn't in it doesn't
officially exist — and won't be found by the next person looking for it.

**5. The standard envelope on every event.**
`eventId` (the consumer's idempotency key), `eventType` + version, `occurredAt`, `correlationId`,
versioned payload. Full conventions in `docs/messaging/schemas.md`.

**6. Never break payload compatibility on a live topic.**
Additive changes are fine within a version. Anything else gets a new event version, with a
migration plan recorded in `ai/PROJECT_MEMORY.md`.

**7. No PII or secrets in payloads.**
Events fan out to consumers that don't exist yet. Treat every payload as permanently public
inside the platform.

## Don't

- Don't `KafkaTemplate.send()` inside a business transaction — use the outbox
- Don't retry a permanently-failing message in place; it blocks every message behind it
- Don't create a per-feature micro-topic when a domain topic fits — topic sprawl makes the
  catalog useless
- Don't assume exactly-once delivery, in any code path, ever

## Related

`ai/patterns/async-events.md` · `ai/patterns/outbox-pattern.md` · `ai/patterns/retry-pattern.md` ·
`docs/messaging/` (topic catalog, schemas, retry policy, DLQ) · `ai/skills/create-integration-test/`
