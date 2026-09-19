# Kafka Topic Catalog

> **Every topic must be registered here** — this is the source of truth
> `ai/skills/kafka/references/topic.md` checks against. A topic that isn't in this table doesn't
> officially exist.

Naming scheme: `<domain>.<entity>.<event>` (e.g. `orders.order.created`). DLQs: `<topic>.dlq`.

<!-- TODO: replace with your real data — the rows below are a fictional example -->
| Topic | Owner (producer) | Key | Partitions | Retention | Schema | Consumers |
| --- | --- | --- | --- | --- | --- | --- |
| `orders.order.created` | orders-service | orderId | 6 | 7d | [schemas.md#ordercreated-v1](schemas.md) | payments-service, notifications-service |
| `payments.payment.completed` | payments-service | paymentId | 6 | 7d | [schemas.md#paymentcompleted-v1](schemas.md) | orders-service |
| `orders.order.created.dlq` | (platform) | — | 1 | 30d | same + failure headers | manual replay |

## Adding a Topic

Follow `ai/skills/kafka/references/topic.md`, then add the row here in the same PR that introduces
the topic. Include the *why* behind non-default partition/retention choices in the PR description or
`ai/PROJECT_MEMORY.md`.
