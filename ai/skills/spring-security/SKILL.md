---
name: spring-security
description: >
  Add or modify Spring Security configuration: securing endpoints, HTTP Basic for internal tools,
  JWT resource-server validation, and OAuth2/OIDC integration — with the platform's best practices.
  Trigger when the user asks to secure an endpoint, add auth, validate tokens, or configure roles.
metadata:
  when_to_use: ["secure this endpoint", "add authentication", "validate the JWT", "OAuth2 setup", "role-based access", "permitAll this path"]
---
<!-- evidence-token: SKSPRI-V70Z43 — cite in the AI Run Report -->

# Spring Security (Basic / JWT / OAuth2)

Companion pattern with the *when-to-use-which* reasoning: `ai/patterns/security-authentication.md`.
This skill is the how-to. Error responses follow `docs/api/error-catalog.md` (401 = unauthenticated,
403 = forbidden — never confuse them).

## Steps (all variants)

1. **Find the existing `SecurityFilterChain`** — extend the service's existing security config;
   never add a second parallel chain for the same paths without an explicit ordering reason.
2. **Deny by default** — `anyRequest().authenticated()` (or denied) as the terminal rule; open
   specific paths (`/actuator/health/**`, docs) explicitly. A new endpoint should be *secured by
   accident*, not exposed by accident.
3. **Stateless** — API services use `SessionCreationPolicy.STATELESS`; no server-side sessions, and
   CSRF disabled *only because* the API is stateless token-based (say so in a comment — future
   readers will ask).
4. **Authorization at both layers** — URL-level rules in the chain for coarse access, plus
   `@PreAuthorize` on service methods for business-level checks. **Object-level checks** (user A
   can't read user B's order by guessing an id) are business logic in the service — the filter chain
   can't do that for you.
5. **Never roll your own crypto/token parsing** — use Spring Security's provided support; passwords
   (if any are stored) via the delegating `PasswordEncoder` (bcrypt/argon2), never MD5/SHA-plain.
6. **Error behavior** — 401 vs 403 correct; bodies via the standard error envelope; no leaking
   whether a username exists; auth failures logged with correlation id but never with
   credentials/tokens.
7. **Tests** — `@WithMockUser` / JWT-builder test support for: anonymous → 401, wrong role → 403,
   correct role → 200, and the object-level check (other user's resource → 403/404 per platform
   convention).

## Variant A — HTTP Basic (internal/ops tools only)

- Acceptable only for internal, non-public tooling behind the mesh — never for public or partner
  traffic.
- Credentials from the secret manager via config, never in code/values files.
- Always over TLS (in-cluster mTLS counts).

## Variant B — JWT Resource Server (the default for service APIs)

- `spring-boot-starter-oauth2-resource-server`; validate via the issuer's JWKS
  (`issuer-uri`/`jwk-set-uri` in config, per env).
- **Validate everything**: signature, `exp`, `iss`, and `aud` — audience validation is the one most
  often skipped; without it a token minted for another service is accepted here.
- Map claims → authorities in one converter bean; keep role/claim names consistent platform-wide
  (record the mapping in `ai/PROJECT_MEMORY.md`).
- Keep tokens out of logs and error bodies; clock skew tolerance small and explicit.
- Expected lifetimes are short; renewal is the client's problem (refresh flow at the IdP), not the
  resource server's.

## Variant C — OAuth2/OIDC Client (when *we* call an IdP or act on a user's behalf)

- Authorization Code + PKCE for anything user-facing; **client credentials** for pure
  service-to-service where the platform uses it; never the deprecated implicit or password grants.
- Client secrets from the secret manager; distinct clients per service (no shared platform-wide
  client id).
- Request the minimal scopes needed; treat scope creep like dependency creep.
- Token acquisition/refresh via Spring's `OAuth2AuthorizedClientManager` — don't hand-roll the
  refresh dance.

## Don't

- Don't `permitAll()` a path "temporarily" — temporary permits become permanent incidents
- Don't do authorization only at the URL layer and skip object-level checks in the service
- Don't accept a JWT without audience validation
- Don't log tokens, credentials, or full Authorization headers — ever

## Related

`ai/patterns/security-authentication.md` · `docs/api/error-catalog.md` ·
`ai/prompts/security-review.md` · `ai/PROJECT_MEMORY.md`
