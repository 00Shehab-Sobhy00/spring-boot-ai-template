# Prompt: Architecture Review

Paste this when a change is big enough to review against the architecture itself — a new service, a
new integration, a cross-service change, or a diff that "feels like it's fighting the structure."

---

Review `<scope>` against this repo's architecture rules. The rule files win over personal
preference; where the *rules themselves* seem wrong for this case, say so explicitly and propose an
ADR rather than quietly deviating.

**Check:**

1. **Layering** — Controller → Service → Repository only; no controller→repository or
   controller→client shortcuts; entities not leaking past the repository; DTOs not reaching
   persistence (`ai/ARCHITECTURE.md`).
2. **Service boundaries** — each service still owns its data; no new cross-service DB access;
   cross-service interaction goes through APIs/events/clients only. Is this change putting logic in
   the *right* service, or the convenient one?
3. **Sync vs async** — is a synchronous call being used where an event fits better (or vice versa)?
   Check against `ai/patterns/rest-api.md` and `ai/patterns/async-events.md`. Multi-service
   transactions must be explicit sagas with compensations (`ai/patterns/saga-pattern.md`), not hope.
4. **Consistency guarantees** — any DB-write-plus-publish path uses the outbox
   (`ai/patterns/outbox-pattern.md`); any new eventual consistency is acknowledged and acceptable to
   the business case, not accidental.
5. **Pattern consistency** — does the change reuse the established patterns (`ai/patterns/`) or
   quietly introduce a parallel second way of doing the same thing (`ai/REVIEW.md`, Duplicate
   Logic)?
6. **Backward compatibility** — public API fields and persisted data stay compatible; breaking
   changes are versioned and called out, never silent (`ai/BACKEND_RULES.md`).
7. **Decision hygiene** — if this change makes a significant, hard-to-reverse choice (new tech, new
   topic taxonomy, new consistency model), it needs an ADR in `/adr/` — check whether one exists or
   should.

**Output format:**

- **Violations** — where the change breaks a stated rule, with the rule cited
- **Tensions** — where the change is legal but strains the architecture; describe the long-term cost
- **ADR candidates** — decisions embedded in this change that deserve a formal record
- **Aligned** — brief confirmation of what's consistent, so it's clear what was checked
