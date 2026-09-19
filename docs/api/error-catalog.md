# Error Catalog

> Authoritative error taxonomy. Referenced by `ai/BACKEND_RULES.md` (Exceptions), `ai/REVIEW.md`
> (API & Errors), and the review skills/prompts.

## The Two Axes

Every failure is classified on two axes, and the response must make both clear:

1. **Whose fault** — client (4xx) vs server (5xx)
2. **Whose server** — *internal* (our domain/application failed) vs *external* (a downstream
   service, partner, or enabler like Stripe failed)

The external distinction matters for on-call triage: an error message must let you tell *at a
glance* whether the failure originated in this service or in a dependency — with safe details only,
never leaked secrets or stack traces.

## Standard Error Envelope

```json
{
  "code": "ORDER_NOT_FOUND",
  "message": "Order 123 was not found",
  "origin": "INTERNAL | EXTERNAL",
  "correlationId": "…",
  "details": [ { "field": "…", "issue": "…" } ]
}
```

`code` values are stable — clients may branch on them; never rename one without a deprecation path.

## Status Mapping

| Situation | Status | origin | Example code |
| --- | --- | --- | --- |
| Request shape invalid (Jakarta validation) | 400 | INTERNAL | `VALIDATION_FAILED` |
| AuthN missing/invalid | 401 | INTERNAL | `UNAUTHENTICATED` |
| AuthZ denied | 403 | INTERNAL | `FORBIDDEN` |
| Resource doesn't exist | 404 | INTERNAL | `ORDER_NOT_FOUND` |
| Business rule violation | 409 or 422 (pick one platform-wide and stick to it) | INTERNAL | `ORDER_ALREADY_CANCELLED` |
| Rate limited | 429 | INTERNAL | `RATE_LIMITED` |
| Our bug / unexpected internal failure | 500 | INTERNAL | `INTERNAL_ERROR` |
| Downstream/partner returned an error | 502 | EXTERNAL | `PAYMENT_PROVIDER_ERROR` |
| Downstream/partner timed out or unreachable | 504 | EXTERNAL | `PAYMENT_PROVIDER_TIMEOUT` |

Notes:

- A downstream's **4xx caused by our bad request** is still our 5xx-territory bug to fix — but
  classify carefully: if the client's input was the actual cause, map it back to a 4xx with a
  precise code.
- Never surface a raw downstream error body to the client; translate to our envelope, keep the
  downstream detail in logs with the correlation id.

## Anti-Patterns

- `500` with a generic message for what is actually a client error
- Distinguishing internal vs external only in logs but not in the response `origin`
- Stack traces, class names, SQL, or secrets in any error body
