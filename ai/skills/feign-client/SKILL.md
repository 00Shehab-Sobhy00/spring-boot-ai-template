---
name: feign-client
description: >
  Add or modify a Spring Cloud OpenFeign client for calling another microservice, with explicit
  timeouts, error decoding, and correct internal-vs-external error mapping. Trigger when the user
  asks to call another service, add a client, or fix Feign timeout/error behavior.
metadata:
  when_to_use: ["call another service", "add a Feign client", "the client times out", "integrate with X-service"]
---
<!-- evidence-token: SKFEIG-U71ASI — cite in the AI Run Report -->

# Add a Feign Client

Follows `ai/BACKEND_RULES.md` (Integrations), `ai/ARCHITECTURE.md` (clients are called from
Services, never Controllers), and `ai/patterns/retry-pattern.md`.

## Steps

1. **Check for an existing client first.** If another feature in this service (or a sibling service
   you can mirror) already calls the target service, extend that client — don't create a parallel
   one for the same downstream.
2. **Interface** — a `@FeignClient` interface in the module's client/adapter package. Name it after
   the downstream service (`PaymentsClient`), methods after the operation. The URL/service-id comes
   from configuration, never hardcoded.
3. **DTOs for the wire** — dedicated request/response records for the downstream contract. Don't
   reuse this service's own API DTOs or entities — the two contracts evolve independently and
   coupling them breaks one when the other changes.
4. **Timeouts — explicit, always.** Set connect and read timeouts per client in configuration; never
   rely on defaults. Remember mesh/proxy layers add their own timeouts on top — see
   `docs/deployment/networking.md`, and say which layer you tuned.
5. **Error decoding** — a custom `ErrorDecoder` (or the module's existing one) that maps downstream
   responses into typed exceptions, classified as **EXTERNAL** per `docs/api/error-catalog.md`:
   - downstream 5xx / timeout → our 502/504 with `origin: EXTERNAL` and the downstream detail in
     logs (with correlation id), never in our response body
   - downstream 4xx caused by *our* request → that's our bug (internal 5xx-territory) — but if the
     end-client's input was the true cause, map it back to our 4xx with a precise code
6. **Retries** — only for idempotent calls, bounded with backoff, per
   `ai/patterns/retry-pattern.md`. Decide which layer owns retries (app vs mesh) and don't set both
   without accounting for multiplication.
7. **Resilience** — circuit breaker on clients whose downstream can brown-out (matching whatever
   resilience library the repo already uses); propagate the correlation id header on every call.
8. **Tests** — unit test the error decoder mappings; integration test against WireMock (or the
   repo's stub tool) covering: success, downstream 5xx, timeout, and malformed response. Cover the
   Feign failure paths — that's exactly what `ai/TESTING.md` prioritizes.

## Don't

- Don't call a Feign client from a controller — service layer only
- Don't let downstream DTOs or errors leak raw into our API responses
- Don't add a retry to a non-idempotent call without a dedupe/idempotency key
- Don't hardcode URLs or per-env values — configuration/profiles only

## Related

`ai/BACKEND_RULES.md` (Integrations) · `ai/patterns/retry-pattern.md` · `docs/api/error-catalog.md`
· `docs/deployment/networking.md`
