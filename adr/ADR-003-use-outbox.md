# ADR-003: Use the Transactional Outbox for Event Publishing

- **Status**: Accepted
- **Date**: 2024-02-20 <!-- template date — replace with yours -->
- **Deciders**: Platform team

## Context

With Kafka adopted (ADR-001), services must publish events about committed DB changes. DB commit and
Kafka publish are two systems with no shared transaction: publishing directly inside the business
flow can emit events for rolled-back changes, or commit changes whose events were never sent. Both
failure modes surfaced in early incidents as "ghost events" and "lost events."

## Options Considered

1. **Transactional outbox + relay** — event row committed atomically with the business change; a
   relay publishes afterwards. Cons: extra table + relay component; delivery becomes at-least-once
   with slight added latency.
2. **Publish-then-commit / commit-then-publish** — simplest code. Cons: exactly the inconsistency
   windows we're trying to eliminate; unfixable by ordering alone.
3. **Kafka transactions spanning "DB + publish"** — Kafka transactions don't span an external RDBMS;
   doesn't solve the core problem.
4. **CDC (Debezium) on business tables directly** — no outbox table. Cons: couples the event
   contract to internal schema; every schema change risks the public event shape.

## Decision

Transactional outbox: business change + `outbox_event` row in the same JPA transaction; a relay
(poller with `FOR UPDATE SKIP LOCKED`, or CDC on the *outbox table* where provisioned) publishes and
marks dispatch; a retention job purges dispatched rows. Consumers dedupe on `eventId` (required
anyway by ADR-001's at-least-once stance).

## Consequences

- Positive: no lost/ghost events; the event contract stays decoupled from internal schema;
  crash-safe by construction.
- Negative / accepted costs: outbox table + relay to operate; publish latency = relay poll interval;
  a stuck relay is a new failure mode — hence the outbox-lag metric requirement.
- Follow-ups: `ai/patterns/outbox-pattern.md`,
  `ai/skills/kafka/references/outbox-implementation.md`, lag alerting in the runbook.
