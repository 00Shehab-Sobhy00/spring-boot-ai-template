---
name: create-rest-api
description: >
  Scaffold a new REST endpoint (controller + request/response DTOs + service method + mapper +
  error mapping + tests) following this repo's layered architecture and API conventions.
  Trigger when the user asks to add/create an endpoint, API, controller, or route.
metadata:
  when_to_use: ["add an endpoint", "new API", "create a controller", "expose this as REST", "add a route for X"]
---
<!-- evidence-token: SKCREA-26C7Z3 — cite in the AI Run Report -->

# Create a REST API Endpoint

Follows `ai/ARCHITECTURE.md` (layering), `ai/BACKEND_RULES.md` (Spring conventions), and
`ai/patterns/rest-api.md` (conventions). Read those if this is your first time touching this repo's
API layer.

## Steps

1. **Confirm the contract first.** Resource name (plural noun), HTTP method, path (with version
   prefix), request/response shape, and which errors are possible. If any of this is ambiguous,
   state your assumption and proceed rather than blocking on it.
2. **Request/response DTOs** — records under `common/dto`. Add Jakarta validation constraints on the
   request DTO. Never reuse a JPA entity as a DTO.
3. **Controller method** — thin. Delegates to the service, returns `ResponseEntity<ResponseDto>`
   with an explicit status code. No business logic, no repository/client calls here.
4. **Service method** — business logic and the `@Transactional` boundary live here (service layer
   only, per `BACKEND_RULES.md`). Calls the mapper and repository/client as needed.
5. **Mapper** — DTO ↔ domain/entity conversion, placed with the existing mappers in `common/mappers`
   (match the existing mapping style in the module — MapStruct, manual, or whatever is already used;
   don't introduce a second mapping approach).
6. **Error mapping** — reuse existing typed exceptions and the global exception handler. Only add a
   new exception type if no existing one fits; if you do, make sure it's mapped to the right 4xx/5xx
   per `docs/api/error-catalog.md`.
7. **Tests** — a controller/API test for request validation and status codes, and a service unit
   test for the business logic and its failure paths. See `ai/TESTING.md` for what to prioritize.
8. **Docs** — if the service maintains OpenAPI annotations, add them; note the new endpoint in
   `docs/api/` if that's where this project tracks its API surface.

## Don't

- Don't add caching, retries, or a new library "while you're in there" — that's scope creep per
  `ai/AI_BEHAVIOR.md`
- Don't invent a new error-handling style if one already exists in this module
- Don't return an unbounded collection — paginate per `ai/patterns/rest-api.md`

## Related

`ai/patterns/rest-api.md` · `ai/BACKEND_RULES.md` · `docs/api/error-catalog.md` ·
`ai/skills/create-service/` · `ai/skills/create-integration-test/`
