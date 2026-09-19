> Reference pattern. Cross-checked against `ai/ARCHITECTURE.md` and `ai/BACKEND_RULES.md` — those
> files win if anything here conflicts.
<!-- evidence-token: PATREST-6UENF7 — cite in the AI Run Report -->

# Pattern: REST API

## Intent

A predictable, versionable HTTP contract for synchronous request/response use cases between clients
(or other services) and this service.

## When to Use

- The caller needs an immediate response to act on
- The operation is naturally request/response, not a fire-and-forget fact about something that
  happened (for that, see `async-events.md`)

## When Not to Use

- Long-running work — return `202 Accepted` with a status endpoint, or model it as an event instead
- Pure inter-service facts ("Order was created") — publish an event; don't make every consumer poll
  a REST endpoint

## Shape in This Codebase

```text
Controller          -> @RestController, thin, returns ResponseEntity<XyzResponse>
  -> Request DTO     -> record, @Valid + Jakarta constraints
  -> Service          -> business logic, @Transactional boundary
    -> Mapper         -> DTO <-> domain/entity
    -> Repository      -> Spring Data
  <- Response DTO     -> record, never the JPA entity
```

## Conventions

- **Resource naming**: plural nouns, no verbs — `POST /orders`, not `POST /createOrder`
- **Versioning**: path-based, `/v1/...`; a breaking change gets a new version, not a mutated
  existing one
- **Pagination**: `page` + `size` query params, response includes `totalElements`/`totalPages`;
  never return an unbounded collection
- **Idempotency**: state-changing `POST` endpoints that might be retried by a client or gateway
  accept an idempotency key header (see `PROJECT_MEMORY.md` for the header name in use) and dedupe
  on it
- **Errors**: standard error envelope, 4xx vs 5xx split per `docs/api/error-catalog.md` — never a
  raw stack trace or exception message

## Pitfalls

- Controller reaching into a Repository or another service's client directly (forbidden — see
  `ARCHITECTURE.md`)
- Returning the JPA entity straight from a controller (leaks persistence concerns, breaks the DTO
  boundary)
- Ambiguous `null` instead of an explicit not-found (`404`) or empty collection

## Related

- Recipe: `ai/skills/create-rest-api/`
- Error taxonomy: `docs/api/error-catalog.md`
- Layering rules: `ai/ARCHITECTURE.md`
