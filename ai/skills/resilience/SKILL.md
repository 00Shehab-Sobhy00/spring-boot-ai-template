---
name: resilience
description: >
  Keep a service healthy when its dependencies aren't — circuit breakers, rate limiting,
  bulkheads, timeouts, and graceful shutdown. Use when a downstream is flaky, when protecting
  against overload, or when deploys drop in-flight requests.
metadata:
  when_to_use: ["circuit breaker", "rate limit", "bulkhead", "resilience4j", "downstream is slow", "cascading failure", "graceful shutdown", "requests dropped during deploy"]
---
<!-- evidence-token: SKRESI-FXMJVG — cite in the AI Run Report -->

# Resilience

Retries alone are not resilience — a retry against a struggling downstream makes the outage
worse. This skill covers the patterns that contain failure instead of amplifying it.

| You want to... | Read |
| --- | --- |
| Stop hammering a failing dependency | `references/circuit-breaker.md` |
| Protect against overload / abusive callers | `references/rate-limiting.md` |
| Stop one slow dependency exhausting all threads | `references/bulkhead.md` |
| Deploy without dropping in-flight work | `references/graceful-shutdown.md` |

Retry and backoff themselves live in `ai/patterns/retry-pattern.md` — read that first; these
patterns sit on top of it.

## The Order to Apply Them

Reaching for a circuit breaker before setting a timeout is the classic mistake. Apply in this
order — each one is nearly useless without the one above it:

1. **Timeouts** — an unbounded wait is the root cause of most cascading failures. Every outbound
   call gets an explicit connect and read timeout. No exceptions.
2. **Bounded retries with backoff + jitter** — only for idempotent operations.
3. **Circuit breaker** — stop calling a dependency that is clearly down.
4. **Bulkhead** — contain the blast radius so one slow dependency can't consume every thread.
5. **Rate limiting** — protect yourself from callers, and downstreams from you.
6. **Graceful degradation** — decide what the service does when a *non-critical* dependency is
   gone. Serving a partial response usually beats a 500.

## Non-Negotiables

**1. Every outbound call has an explicit timeout.** Default timeouts in HTTP clients are often
infinite or minutes long. An unbounded wait turns a slow downstream into your outage.

**2. Layers stack — count them.** App-level retries multiply with mesh-level retries. Three app
retries × three mesh retries = nine requests hitting an already-struggling service. Decide which
layer owns retries per route and write it down (`docs/deployment/networking.md`).

**3. Failing fast beats failing slow.** A fast 503 lets the caller react. A request that hangs for
60 seconds holds a thread, a connection, and the caller's patience.

**4. Degradation is a product decision, not a technical one.** "What should the user see if
recommendations are down?" is answered in `docs/business/business-overview.md`, not invented in
the catch block.

**5. Configure per dependency, not globally.** A payment provider and an internal cache warrant
completely different timeouts, thresholds, and fallbacks.

**6. Resilience config is observable.** Circuit-breaker state changes, rate-limit rejections, and
bulkhead saturation must emit metrics — otherwise the first sign is a confused user. See
`ai/skills/observability/`.

## Don't

- Don't add a circuit breaker before setting timeouts — it will never trip correctly
- Don't retry non-idempotent operations without an idempotency key
- Don't share one thread pool across fast and slow dependencies
- Don't silently swallow a fallback — count it, log it, alert if the rate is abnormal
- Don't tune any of this from local measurements; local has no mesh
  (`docs/deployment/networking.md`)

## Related

`ai/patterns/retry-pattern.md` · `ai/skills/feign-client/SKILL.md` ·
`ai/skills/observability/SKILL.md` · `docs/deployment/networking.md` · `docs/api/error-catalog.md`
