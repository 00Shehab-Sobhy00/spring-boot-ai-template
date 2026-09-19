# Architecture Decision Records

Significant, hard-to-reverse decisions live here — with the context and trade-offs, so future
readers (human or AI) know *why*, not just *what*.

- **When to write one**: new core technology, a consistency model choice, a cross-service
  convention, anything you'd have to explain to a new senior engineer with "well, the reason is…".
- **When not to**: small conventions and gotchas → `ai/PROJECT_MEMORY.md` instead.
- **Lifecycle**: `Proposed → Accepted → (later) Deprecated / Superseded by ADR-XXX`. Accepted ADRs
  are effectively immutable — supersede, don't edit.
- **Template**: `template.md`. Numbering: sequential, zero-padded.

| # | Title | Status |
| --- | --- | --- |
| 001 | [Use Kafka for inter-service events](ADR-001-use-kafka.md) | Accepted |
| 002 | [Use Redis (cache-aside) for hot reads](ADR-002-use-redis.md) | Accepted |
| 003 | [Use the transactional outbox for event publishing](ADR-003-use-outbox.md) | Accepted |
