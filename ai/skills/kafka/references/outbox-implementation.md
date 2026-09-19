# Implement the Transactional Outbox

Follows `ai/patterns/outbox-pattern.md` (read it first — it explains the why) and
`/adr/ADR-003-use-outbox.md`.

## Steps

1. **Outbox table migration** — a new Liquibase changelog for `outbox_event` (id, aggregate_type,
   aggregate_id, event_type, payload, created_at, dispatched_at). Index on
   `(dispatched_at, created_at)` for the relay's poll query. Never edit historical changelogs.
2. **Outbox write** — in the same service-layer `@Transactional` method as the business change,
   persist the outbox row via a small `OutboxService`/repository. The envelope fields (eventId,
   eventType+version, correlationId) are set here — see `docs/messaging/schemas.md`.
3. **Relay** — a scheduled poller (or CDC if the platform provides Debezium) that reads undispatched
   rows in `created_at` order, publishes to Kafka with the aggregate id as the partition key, and
   marks rows dispatched **after** a confirmed publish. Handle the "published but crash before
   marking" case — that's why consumers dedupe on eventId.
4. **Concurrency** — if the service runs multiple replicas, make the relay safe under competition:
   `FOR UPDATE SKIP LOCKED` on the poll query, or a distributed lock via the repo's existing
   Redisson setup — match what sibling services already do.
5. **Retention cleanup** — a scheduled job deleting dispatched rows older than the retention window,
   following `ai/BACKEND_RULES.md`: explicit retention condition, batched deletes, and a test
   asserting both what's deleted and what remains.
6. **Observability** — a metric/log for outbox lag (oldest undispatched row age); a silently-stuck
   relay is the failure mode you most want to see coming.
7. **Tests** — integration tests for: business write + outbox row committed atomically (and rolled
   back together on failure), relay publishes and marks dispatched, redelivery after a simulated
   crash between publish and mark, and cleanup retention behavior.

## Don't

- Don't publish directly to Kafka inside the business transaction "just this once"
- Don't skip the cleanup job — the outbox table grows unbounded otherwise
- Don't build a second, slightly different outbox next to an existing one — reuse/extend what's
  there

## Related

`ai/patterns/outbox-pattern.md` · `/adr/ADR-003-use-outbox.md` ·
`ai/skills/kafka/references/producer.md` · `docs/messaging/schemas.md`
