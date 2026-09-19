> Reference pattern. The how-to lives in `ai/skills/spring-security/`; this file is the *which
> mechanism, when, and why*.
<!-- evidence-token: PATSECU-L84EY9 — cite in the AI Run Report -->

# Pattern: Authentication & Authorization

## Intent

Pick the right auth mechanism per traffic type, and keep authentication (who are you) cleanly
separated from authorization (what may you do).

## Decision Table

| Traffic | Mechanism | Why |
| --- | --- | --- |
| Public / user-facing API | **JWT resource server** (tokens issued by the platform IdP via OIDC + PKCE) | Stateless, horizontally scalable, one IdP owns credentials |
| Service → service (inside the mesh) | mesh **mTLS** for transport identity, plus **client-credentials JWT** where business-level authorization is needed | Transport identity alone can't express "may this service cancel orders?" |
| Partner / external system → us | OAuth2 **client credentials** per partner, minimal scopes | Revocable per partner, auditable, no shared secrets in requests |
| Internal ops/admin tooling, non-public | **HTTP Basic** behind the mesh, secrets from the secret manager | Lowest ceremony; acceptable *only* because it never leaves the trust boundary |
| Webhooks *into* us (Stripe etc.) | Provider's **signature verification** (HMAC), never IP allowlists alone | The provider defines the mechanism; verify every payload |

## Principles

- **Deny by default.** Every chain ends in `authenticated()`/deny; exceptions are explicit and
  reviewed.
- **AuthN at the edge, authZ everywhere.** The token is validated once at entry; *authorization* is
  checked again at the business layer (`@PreAuthorize` + object-level ownership checks in services).
  URL rules alone cannot prevent user A reading user B's resource.
- **Validate the full token**: signature, expiry, issuer, **audience**. Audience is the classic
  omission — see the skill.
- **Short-lived access tokens, refresh at the IdP.** Resource servers never mint or extend tokens.
- **401 vs 403 mean different things** (`docs/api/error-catalog.md`): 401 = we don't know who you
  are; 403 = we know, and no. Don't leak resource existence to unauthorized users — pick 403-vs-404
  policy platform-wide and record it in `ai/PROJECT_MEMORY.md`.
- **Secrets** live in the secret manager; token/claim contents never appear in logs or error bodies.

## Pitfalls

- A `permitAll()` added for a demo that ships to prod
- Trusting mesh mTLS as if it were authorization ("it's internal traffic, so it's allowed to do
  anything")
- Sharing one OAuth2 client id across many services — revocation and audit become impossible
- Skipping webhook signature verification because "the endpoint URL is secret" (it isn't)

## Related

- How-to: `ai/skills/spring-security/`
- Review pass: `ai/prompts/security-review.md`
- Error semantics: `docs/api/error-catalog.md`
