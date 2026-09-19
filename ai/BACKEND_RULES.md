> Part of the [AI agent configuration](../AGENTS.md). Authoritative source for Java/Spring coding
> standards — loaded via `opencode.json` and linked from `AGENTS.md` rather than duplicated.
<!-- evidence-token: BACK-0W9PD6 — cite in the AI Run Report -->

# Java

- Java 25

# Spring

- Constructor injection only
- No field injection
- Prefer records for immutable DTOs where practical

# Transactions

- Use `@Transactional` only on the service layer
- Keep transaction boundaries explicit and as narrow as practical

# Validation

- Jakarta Validation
- Validate request payloads at the API boundary (`@Valid` / constraints on DTOs)
- Keep deeper business validation in the service layer when rules depend on domain state

# Exceptions

- Global Exception Handler (`@ControllerAdvice` / `@RestControllerAdvice`)
- Domain / business failures via typed service exceptions and stable error codes
- Distinguish validation / client errors (4xx) from internal and external failures (5xx). See
  `docs/api/error-catalog.md` for the full error taxonomy, including how to tell an internal domain
  failure apart from a downstream/partner failure.
- Do not swallow exceptions; log with context, then rethrow or map
- Never expose stack traces or secrets in API error bodies

# Persistence

- Prefer Spring Data repositories for standard CRUD
- Keep custom queries in the persistence layer (repository / DAO), not in controllers
- No business logic inside repositories
- Apply schema changes through a migration tool only (Liquibase —
  `src/main/resources/liquibase/master.xml` + `changelog/`). Do not bypass with ad-hoc production
  DDL unless explicitly asked.
- **Never modify a historical Liquibase changelog. Always create a new migration file**, even for a
  one-line fix to something recently merged.
- When writing cleanup / purge scripts (e.g. expired sessions, tokens, or contexts older than a
  retention window):
  - Delete only rows that match an explicit retention condition (date/status) — never an unbounded
    full-table delete
  - Delete in an order that respects foreign keys (children before parents)
  - Prefer batched deletes for large tables to avoid long locks
  - A cleanup/purge test must assert both what was deleted **and** what must remain

# Integrations

- Call other services through dedicated clients / adapters
- Make timeouts, retries, and error mapping explicit. **Every outbound call has an explicit connect
  and read timeout** — an unbounded wait is the root cause of most cascading failures
- Circuit breakers, bulkheads, and rate limits: `ai/skills/resilience/`
- Treat downstream failures as external errors in the API response model
- Be aware of proxy, mTLS, and service-mesh behavior — local/staging often differ from production.
  See `docs/deployment/networking.md` before tuning timeouts or health checks.

# Logging

- SLF4J. Structured (JSON) output in every deployed environment — free text can't be queried at
  scale
- Context goes in MDC, not concatenated into the message string
- **Every log line carries the correlation/trace id.** Note that `@Async`, executors, and scheduled
  tasks lose MDC unless propagation is configured — see
  `ai/skills/observability/references/tracing.md`
- Clear MDC when the scope ends; thread pools reuse threads and stale MDC values attach to unrelated
  requests
- Use appropriate levels: info for state transitions and business events, warn for recoverable
  issues, error for failures
- Never log passwords, tokens, full Authorization headers, or PII — including inside downstream
  exception messages
- Avoid logging full large payloads by default
- Full guidance: `ai/skills/observability/references/logging.md`

# API / Nullability

- Controllers return `ResponseEntity` with clear HTTP status
- Prefer explicit not-found / empty modeling over ambiguous null returns from public service APIs

# Dependencies

- Add a dependency only when nothing already present covers the need — check the existing `pom.xml`
  first
- New dependencies must pass the CVE scan in CI; a new high/critical finding blocks the build
- Do not pin or hardcode versions that the parent POM / BOM already manages

# Configuration

- Externalize configuration (application yaml / properties)
- No secrets hardcoded in source
- Environment-specific values via profiles or environment overrides

# Testing

- Unit-test services for business rules and edge cases
- Cover transaction boundaries and inter-service failure paths
- Prefer focused tests over brittle end-to-end coverage for every change
- Full policy: `ai/TESTING.md`

# Code Style

- Prefer constructor injection (`@RequiredArgsConstructor` or explicit constructors)
- Keep methods focused; avoid big services
- Prefer immutability for DTOs
- Do not introduce a second parallel style in the same module

# See Also

- Layering rules: `ai/ARCHITECTURE.md`
- Task recipes that apply these rules: `ai/skills/create-service/`,
  `ai/skills/database/references/create-entity.md`,
  `ai/skills/database/references/optimize-query.md`
