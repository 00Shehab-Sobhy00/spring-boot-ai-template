> Part of the [AI agent configuration](../AGENTS.md). Authoritative source for review criteria —
> also used by `ai/skills/review-pr/`.
<!-- evidence-token: REVW-XBZCRY — cite in the AI Run Report -->

# Before Finishing

Check:

- Naming
- Complexity
- Performance
- Thread Safety
- Null Safety
- SQL efficiency
- Duplicate logic

Suggest improvements separately from the main change summary (do not mix "what changed" with
"optional follow-ups").

# Naming

- Names reflect intent (behavior / domain), not implementation noise
- Avoid abbreviations unless already standard in the module
- Keep package, class, and method names consistent with existing style

# Complexity

- Prefer simple control flow over clever nesting
- Extract methods when a block has a clear responsibility
- Avoid god services / methods that mix unrelated concerns
- Prefer early returns over deep `if/else` pyramids when it improves clarity

# Performance

- Watch accidental N+1 queries and repeated remote calls in loops
- Avoid loading large collections when a projection / page / limit is enough
- Do not add caching unless there is a clear need and invalidation strategy — see
  `ai/patterns/cache-aside.md`
- Be careful with blocking calls on hot paths

# Thread Safety

- Do not share mutable state across requests without synchronization
- Prefer immutable DTOs / value objects where practical
- Be explicit about concurrent access for caches, counters, and shared buffers
- Assume service beans are singletons — keep them stateless regarding request data

# Null Safety

- Do not return ambiguous nulls from public APIs when empty/not-found can be explicit
- Validate inputs at boundaries
- Handle Optional / nullable downstream responses deliberately (no blind dereferencing)
- Prefer clear not-found / validation errors over NullPointerException

# SQL Efficiency

- Prefer indexed, selective filters over broad scans
- Avoid `SELECT *` when only specific columns are needed (where applicable)
- For cleanup / purge: constrained deletes, FK-safe order, batched deletes for large tables
- Keep heavy query logic in the persistence layer, not in controllers
- Deeper checklist: `ai/skills/database/references/optimize-query.md`

# Duplicate Logic

- Reuse existing mappers, validators, error codes, and clients when they already solve the problem
- Do not copy-paste near-identical blocks across services without extracting a clear shared helper
- Do not invent a second parallel pattern next to an existing one in the same module — check
  `ai/patterns/` first

# API & Errors

- Confirm HTTP status and error body match the failure type (client vs internal vs external) — see
  `docs/api/error-catalog.md`
- Ensure error messages are precise and safe (no secrets / PII / stack traces)

# Observability & Resilience

- Can an on-call engineer who didn't write this tell what it does? (metric, trace, or log for each
  new path)
- Does every new outbound call have an explicit timeout?
- Do new metric tags have bounded cardinality? (no ids, paths, or exception messages)
- Does every log line in the new code carry the correlation id — including async paths?
- New alert added? Does it have a runbook entry?

# Tests & Safety

- Related tests updated or added for behavior changes
- No secrets, credentials, or real PII introduced
- No bypass of migrations with ad-hoc production DDL unless explicitly requested

# Review Output Format

When reviewing or self-checking, separate:

1. **Blockers** — must fix before finish
2. **Suggestions** — optional improvements, listed separately
3. **Notes** — observations that are informational only
