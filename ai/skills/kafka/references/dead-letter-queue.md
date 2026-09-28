<!-- evidence-token: SKKDLQ-G4DXLD — cite in the AI Run Report -->

# Add / Use a Dead-Letter Queue

Follows `docs/messaging/dlq.md` and `docs/messaging/retry-policy.md`. A DLQ handles *permanent*
failures; transient failures are the retry policy's job — classify first.

## Steps

1. **Classify the failure.** Transient (timeouts, temporary downstream errors) → bounded retry with
   backoff, no DLQ. Permanent (unparseable payload, schema violation, a business rule that can never
   pass for this message) → DLQ after the retry budget is exhausted, or immediately for
   clearly-unrecoverable cases.
2. **DLQ topic naming** — `<original-topic>.dlq` (or the repo's established suffix per
   `docs/messaging/dlq.md`). One DLQ per source topic, not one global dumping ground.
3. **Preserve context** — the DLQ record must carry the original payload plus headers: original
   topic/partition/offset, exception class + message, failure timestamp, attempt count, correlation
   id. A DLQ record you can't diagnose is a black hole.
4. **Commit semantics** — the original message's offset is committed only after a *successful* DLQ
   handoff; if writing to the DLQ itself fails, the consumer must not silently ack the original.
5. **Alerting** — DLQ depth > 0 should be visible (metric + alert). A silent DLQ is where data goes
   to die.
6. **Replay path** — define how messages get replayed after a fix (a replay consumer, a manual tool,
   or re-publish to the source topic) and document it in `docs/messaging/dlq.md`. Replays go through
   the same idempotency check as normal delivery.
7. **Tests** — a poison message ends up on the DLQ with full context headers, the source partition
   keeps moving, and a replayed message is processed exactly once thanks to idempotency.

## Don't

- Don't retry a permanent failure forever in place — it blocks every message behind it on that
  partition
- Don't strip the failure context when dead-lettering — the payload alone is not enough to diagnose
- Don't create a single shared DLQ for all topics — per-source-topic DLQs keep ownership and replay
  tractable

## Related

`docs/messaging/dlq.md` · `docs/messaging/retry-policy.md` ·
`ai/skills/kafka/references/consumer.md`
