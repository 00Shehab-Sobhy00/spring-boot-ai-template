# ADR-002: Use Redis (Cache-Aside) for Hot Read Paths

- **Status**: Accepted
- **Date**: 2024-02-01 <!-- template date — replace with yours -->
- **Deciders**: Platform team

## Context

A small number of read paths are measurably hot and dominated by repeated reads of slowly-changing
data; the database was becoming the bottleneck on those paths specifically. General read latency
elsewhere is fine — this is a targeted problem, not a platform-wide one.

## Options Considered

1. **Redis, cache-aside, opt-in per path** — targeted relief, explicit invalidation per use. Cons: a
   second data location; staleness/invalidation is now an application concern.
2. **In-process caches (Caffeine)** — no infra. Cons: per-instance inconsistency across replicas;
   cold caches on every deploy/scale event.
3. **Read replicas** — no app changes. Cons: cost; helps throughput, not repeated-identical-read
   latency; replication lag is its own staleness.
4. **Do nothing / optimize queries only** — always the first step (see
   `ai/skills/database/references/optimize-query.md`), but insufficient for the measured hot paths
   after query optimization.

## Decision

Redis (with Redisson where distributed primitives are needed), applied **cache-aside and opt-in**:
caching is added per read path with a measured need, an explicit TTL, and an invalidation strategy —
never as a default layer. Rules: `ai/patterns/cache-aside.md`; guardrail in `ai/REVIEW.md` (no
caching without need + invalidation plan).

## Consequences

- Positive: targeted latency/load relief; a shared, deploy-surviving cache across replicas; Redisson
  available for locks (e.g. the outbox relay).
- Negative / accepted costs: staleness management; Redis as an availability consideration (reads
  must degrade to the DB, not fail); one more moving part per environment.
- Follow-ups: `ai/skills/redis-cache/`, key/TTL conventions in the pattern doc.
