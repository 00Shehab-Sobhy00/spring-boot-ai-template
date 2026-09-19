# Business Documentation

This folder makes the AI (and new engineers) understand **what the system is for**, not just how
it's built. Technical rules live in `ai/`; the *domain* lives here.

- `business-overview.md` — the one-pager: what the product does, for whom, and the money/value flow.
  **Fill this in first** — it's the highest-leverage document in the whole template for AI output
  quality.
- `rules.md` — the business rules register: one `BR-nnn` id per rule, referenced from the code and
  test that enforce it, cross-checked by `scripts/check-business-rules.sh`. This is the only part of
  the business docs that CI can verify against the code.
- `domain-glossary.md` — the ubiquitous language: every domain term, defined once. AI agents (and
  humans) must use these exact terms in code and docs.
- Add per-domain deep dives as `<domain>.md` (e.g. `payments.md`, `fulfillment.md`) when a domain's
  rules outgrow the overview.

Wiring: `AGENTS.md` routes agents here for "why does the business need this" questions. Keep entries
short and factual — a business doc that reads like marketing copy helps nobody.
