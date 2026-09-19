# Retry Policy (Messaging)

> Platform-wide defaults; per-consumer deviations must be listed at the bottom with a reason.

## Classification First

| Failure | Examples | Action |
| --- | --- | --- |
| **Transient** | downstream timeout, DB connection hiccup, temporary 5xx | Retry with backoff (below) |
| **Permanent** | unparseable payload, schema violation, business rule that can never pass | No retry — straight to DLQ with context (`dlq.md`) |
| **Ambiguous** | unknown error from a call that may or may not have taken effect | Retry only if the operation is idempotent; otherwise DLQ and flag for manual review |

## Default Transient Policy

- Attempts: 3 (initial + 2 retries)
- Backoff: exponential with jitter, base 1s, cap 30s
- After exhaustion: DLQ with full failure context
- In-place blocking retries are bounded and short; anything longer uses the non-blocking retry topic
  mechanism if the platform has one

App-level retries stack with mesh-level retries — see `ai/patterns/retry-pattern.md` and
`docs/deployment/networking.md` before changing either layer.

## Deviations

| Consumer | Deviation | Why |
| --- | --- | --- |
| _none yet_ | | |
