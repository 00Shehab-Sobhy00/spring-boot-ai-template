---
name: create-service
description: >
  Add a new service-layer class (business logic) with correct dependency injection, transaction
  boundaries, and error handling. Trigger when the user asks to add business logic, a use case,
  or a new service/component.
metadata:
  when_to_use: ["add business logic", "new service class", "implement this use case"]
---
<!-- evidence-token: SKCREA-XTCXHB — cite in the AI Run Report -->

# Create a Service (Business Logic)

Follows `ai/ARCHITECTURE.md` (Service owns business logic) and `ai/BACKEND_RULES.md`
(Spring/transactions/exceptions).

## Steps

1. **Placement** — under the module's `components` (or equivalent business-logic package), matching
   sibling services' naming and location.
2. **Dependencies** — constructor injection only, no field injection. Depend on repository/client
   interfaces, not concrete implementations, if that's the existing convention in this module.
3. **Transaction boundary** — `@Transactional` at the service method, scoped as narrowly as the
   business operation allows. Don't wrap read-only calls in a broader transaction than needed.
4. **Business rules** — validation that depends on domain state (not just shape) belongs here, even
   if request-shape validation already happened at the API boundary.
5. **Error handling** — throw typed exceptions with stable error codes on business rule violations;
   don't swallow exceptions — log with context, then rethrow or map. Distinguish "our domain said
   no" from "a downstream call failed" (see `ai/BACKEND_RULES.md` → Exceptions).
6. **Cross-service calls** — through an existing client/adapter, called from the service (never from
   the controller directly).
7. **Tests** — unit test the service with its collaborators mocked (repository, clients). Cover the
   happy path and the important failure/edge paths per `ai/TESTING.md`. Do not mock the class under
   test.

## Don't

- Don't let a service grow into a "god service" mixing unrelated concerns — extract when
  responsibilities diverge
- Don't reach past the client/adapter into another service's internals
- Don't introduce a second DI style (e.g. field injection) alongside constructor injection already
  in use

## Related

`ai/ARCHITECTURE.md` · `ai/BACKEND_RULES.md` · `ai/skills/create-rest-api/` ·
`ai/skills/create-integration-test/`
