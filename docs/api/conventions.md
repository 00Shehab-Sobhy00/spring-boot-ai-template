# API Conventions (Consumer-Facing Summary)

Full pattern rationale: `ai/patterns/rest-api.md`. This page is the short contract for anyone
consuming our APIs.

- **Base paths**: `/v<major>/<resource>` — plural nouns, no verbs (`POST /v1/orders`).
- **Versioning**: breaking change ⇒ new major version path; old versions get a deprecation window.
- **Pagination**: `page` (0-based) + `size`; responses include `totalElements`, `totalPages`. No
  unbounded lists.
- **Idempotency**: retry-able state-changing POSTs accept an idempotency key header (name per
  `ai/PROJECT_MEMORY.md`).
- **Errors**: envelope per `error-catalog.md`; branch on `code`, not `message`.
- **Timestamps**: ISO-8601 UTC instants. **Money**: decimal-as-string + ISO-4217 currency.
