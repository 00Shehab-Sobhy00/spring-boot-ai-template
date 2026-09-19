# Dead-Letter Queues

> Recipe: `ai/skills/kafka/references/dead-letter-queue.md`. One DLQ per source topic, named
> `<topic>.dlq`.

## Required Failure Context (headers)

Every DLQ record carries: original topic/partition/offset, exception class + message, failure
timestamp, attempt count, correlation id — plus the untouched original payload.

## Monitoring

- DLQ depth is a first-class metric; depth > 0 pages/alerts the owning team.
- A message sitting in a DLQ for > 7 days without triage is an incident-review item.

## Replay Procedure

1. Diagnose from the failure headers — fix the code/config/data cause first.
2. Replay via `<the platform's replay tool / consumer — fill in>` back to the source topic.
3. Consumer idempotency (dedupe on eventId) guarantees a replay can't double-apply.
4. Record the incident cause in `ai/PROJECT_MEMORY.md` if it reveals a durable gotcha.

## DLQ Inventory

See the DLQ rows in `kafka-topics.md` — they're registered in the same catalog.
