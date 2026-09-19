# Create a Kafka Topic

Follows `docs/messaging/kafka-topics.md` (the topic catalog — every topic must be registered there).

## Steps

1. **Check the catalog first** — `docs/messaging/kafka-topics.md`. If an existing topic already
   carries this kind of event, use it rather than fragmenting related events across topics.
2. **Name** — follow the established scheme in the catalog (e.g. `<domain>.<entity>.<event>` like
   `orders.order.created`). Consistency with existing names beats personal preference.
3. **Partitions** — size for the ordering key's cardinality and expected throughput. More partitions
   = more parallelism but you can't reduce them later without a migration; when unsure, match
   comparable existing topics and note the reasoning.
4. **Replication factor** — match the cluster standard used by sibling topics (typically 3 in
   production clusters); don't go below it for anything stateful.
5. **Retention** — deliberate, per topic purpose: short for transient signals, longer for events
   consumers may need to replay. Record the choice and the why in the catalog entry.
6. **Where it's defined** — declare the topic wherever this repo declares them (IaC, an admin config
   class, or ops-managed). Don't rely on broker auto-creation for anything production-bound.
7. **Register it** — add the topic to `docs/messaging/kafka-topics.md` with: name, owner service,
   key, partitions, retention, schema link, and consumers.

## Don't

- Don't rely on `auto.create.topics.enable` for production topics
- Don't create a per-feature micro-topic when an existing domain topic fits — topic sprawl makes the
  catalog useless
- Don't pick partition count arbitrarily — it's the one setting that's painful to change later

## Related

`docs/messaging/kafka-topics.md` · `ai/skills/kafka/references/producer.md` ·
`ai/skills/kafka/references/consumer.md` · `/adr/ADR-001-use-kafka.md`
