# Add a Kafka Consumer

Follows `ai/patterns/async-events.md`, `docs/messaging/consumers.md`, and
`docs/messaging/retry-policy.md`.

## Steps

1. **Consumer group** — follow the repo's naming convention (see `docs/messaging/consumers.md`); one
   logical group per service per topic-purpose. Don't reuse another feature's group id.
2. **Listener** — thin, like a controller: deserialize, validate the envelope, delegate to a service
   method. Business logic lives in the service, not the listener.
3. **Idempotency** — dedupe on `eventId`. Delivery is at-least-once; the same event *will* arrive
   twice eventually. Persist processed event ids (or make the operation naturally idempotent) —
   decide which and say why.
4. **Ordering assumptions** — only rely on ordering within a partition, and only if the producer
   keys by aggregate id. Never assume cross-partition ordering.
5. **Error handling** — distinguish:
   - *Transient* (downstream timeout, DB hiccup): retry with backoff per
     `docs/messaging/retry-policy.md`
   - *Permanent* (poison message, unparseable payload, business rule that will never pass): route to
     the DLQ per `ai/skills/kafka/references/dead-letter-queue.md` — do **not** retry forever and
     block the partition
6. **Offset management** — commit only after successful processing (or after a successful DLQ
   handoff for a permanent failure), matching the repo's existing ack mode.
7. **Tests** — integration test that publishes to a test topic and asserts the observable side
   effect, plus a test for the duplicate-delivery path (same event twice → one side effect) and a
   poison-message → DLQ test.
8. **Docs** — register the consumer in `docs/messaging/consumers.md`.

## Don't

- Don't put business logic in the listener method
- Don't retry a permanently-failing message in place — it blocks the partition for every message
  behind it
- Don't assume exactly-once delivery, ever

## Related

`ai/patterns/async-events.md` · `ai/skills/kafka/references/dead-letter-queue.md` ·
`docs/messaging/consumers.md` · `docs/messaging/retry-policy.md` ·
`ai/skills/create-integration-test/`
