# Prompt: Security Review

Paste this for a security-focused pass over a diff, endpoint, or service.

---

Review `<scope>` for security issues. Report concrete findings with file/line, not a generic
checklist recital.

**Check:**

1. **Input handling** — request DTO validation actually constrains what matters (not just
   `@NotNull`); no string-concatenated SQL/JPQL; no unvalidated data flowing into queries, file
   paths, headers, or redirects.
2. **AuthN/AuthZ** — every new endpoint has the right authorization check; no object-level
   authorization gaps (user A reading user B's resource by guessing an id); internal-only endpoints
   aren't exposed through the public ingress (`helm/` routing).
3. **Secrets & PII** — no secrets/tokens/credentials in code, config committed to git, logs, error
   messages, or event payloads (`ai/BACKEND_RULES.md`, Logging; `ai/AI_BEHAVIOR.md`, Safety
   Defaults). Event payloads deserve extra attention — they fan out to unknown future consumers.
4. **Error responses** — no stack traces, class names, or internal details leaking in API error
   bodies; 4xx vs 5xx classification doesn't reveal more than it should
   (`docs/api/error-catalog.md`).
5. **Dependencies** — new dependencies in `pom.xml`: are they necessary (an existing lib may already
   cover it), maintained, and free of known CVEs?
6. **Data at rest / in transit** — anything sensitive newly persisted or published: is it minimized,
   and does it belong in this service at all (`ai/ARCHITECTURE.md`, service owns its data)?
7. **Infra** — containers run non-root (`ai/skills/deployment/references/docker.md`); no secrets in
   images or Helm values committed to git; debug/actuator endpoints not publicly routed.

**Output format:**

- **Blockers** — exploitable or data-exposing issues; must fix
- **Hardening** — defense-in-depth improvements, listed separately
- **Notes** — informational

If you're uncertain whether something is exploitable, say so explicitly and state what would confirm
it — don't silently downgrade it to a note.
