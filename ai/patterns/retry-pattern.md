> Reference pattern. Cross-checked against `ai/BACKEND_RULES.md` (Integrations) — that file wins if
> anything here conflicts.
<!-- evidence-token: PATRETR-BB4S03 — cite in the AI Run Report -->

# Pattern: Retry / Backoff / Circuit Breaking

## Intent

Handle transient failures in calls to other services (Feign, HTTP clients) without hammering a
struggling downstream or hanging the caller forever.

## When to Use

- The failure is plausibly transient (timeout, connection reset, `503`)
- The call is idempotent, or made idempotent via an idempotency key — retrying a non-idempotent
  write can duplicate side effects

## When Not to Use

- The downstream returned a `4xx` — that's a client/request problem; retrying an identical request
  won't fix it
- The operation isn't idempotent and there's no dedupe key to make a retry safe

## Shape in This Codebase

```text
Client call
  -> explicit connect/read timeout (never "whatever the default is")
  -> bounded retries with exponential backoff + jitter (not a tight retry loop)
  -> circuit breaker trips after a failure threshold, to stop hammering a downstream that's already struggling
  -> failure surfaces as an explicit external/5xx error — never swallowed
```

## Conventions

- Set timeouts explicitly per client — remember that local/staging proxy or service-mesh behavior
  can add latency that isn't representative of production; see `docs/deployment/networking.md`
- Cap retry attempts (e.g. 2–3) with backoff — an unbounded retry loop just moves the outage to your
  own service
- Log each retry attempt with correlation id and attempt number, so a string of retries is visible
  in one trace
- Distinguish "downstream said no" (don't retry) from "we couldn't tell what happened" (safe to
  retry, if idempotent)

## Pitfalls

- Retrying a non-idempotent `POST` with no dedupe key — can create duplicate orders/charges/records
- No circuit breaker — a slow downstream cascades into thread/connection pool exhaustion in this
  service
- Retrying on `4xx` responses, which just repeats a request that will fail identically

## Related

- Recipe: `ai/skills/kafka/references/consumer.md` (consumer-side retry → DLQ is a related but
  distinct concern, see `dead-letter-queue` skill)
- `ai/BACKEND_RULES.md` (Integrations)
- `docs/messaging/retry-policy.md`
