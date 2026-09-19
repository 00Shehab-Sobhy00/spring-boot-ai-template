> Part of the [AI agent configuration](../AGENTS.md). This is the team's **living** knowledge base —
> the tribal knowledge that doesn't fit an ADR and isn't a fixed rule.
<!-- evidence-token: MEMO-ER3F8C — cite in the AI Run Report -->

# Project Memory

This file is different from everything else in `ai/`:

| File | Nature | Who edits it |
| --- | --- | --- |
| `ARCHITECTURE.md`, `BACKEND_RULES.md`, `TESTING.md`, `REVIEW.md`, `AI_BEHAVIOR.md` | Stable rules, rarely change | Humans, deliberately |
| `/adr/*.md` | Formal, dated, effectively immutable once accepted | Humans, via PR |
| **`PROJECT_MEMORY.md` (this file)** | Living notes, expected to change often | Humans **and** the AI agent, during normal work |
| opencode global memory (`~/.config/opencode/AGENTS.md`) | Personal, local, not committed | The agent, per developer machine |

Use this file for the things a new senior engineer would otherwise have to learn the hard way. Keep
entries short — one or two lines. Move anything that grows past a paragraph into a proper doc under
`/docs/` or an ADR, and leave a pointer here instead.

## How the agent should use this file

- Read it before investigating a bug or making a non-trivial change — it often explains "why is this
  weird" faster than the code does.
- When you (the agent) discover something durable and non-obvious during a task — a gotcha, a
  footgun, a "we tried X and it didn't work" — propose an addition here at the end of the task
  instead of letting it evaporate with the chat.
- Do not record anything here that belongs in an ADR (a real architectural decision) or that's
  already covered by a rule file — link to those instead of duplicating them.
- Never record secrets, credentials, tokens, or real customer data here. This file is committed to
  source control.

## Conventions & Decisions Log

Small decisions that don't warrant a full ADR. Format: `YYYY-MM-DD — decision — why`.

- _2024-01-01 — Example: switched the idempotency key header from `Idempotency-Key` to
  `X-Idempotency-Key` — aligns with the platform-wide gateway convention._

## Known Gotchas / Footguns

- _Example: the staging Istio sidecar adds ~150ms to the first request after a pod restart — don't
  tune client timeouts based on a cold-start staging measurement._

## Environment Quirks

- **`scripts/check-ai-report.py` on a Windows console**: its output contains `→`, which cp1252
  cannot encode — the INSTRUCTION-RETENTION-FAILURE branch used to die mid-print and return exit 1
  instead of its deliberate exit 4. The script now reconfigures stdout to UTF-8; keep that if you
  touch the top of the file, or the strongest check in the template silently reports the wrong code.
- **Skills discovery**: opencode reads them via the `skills` array in `opencode.json`, which points
  at `ai/skills`. Skills live only in `ai/skills/` — there is no duplicated copy anywhere,
  deliberately (one authoritative source). No symlinks are used (they're unreliable on Windows
  without Developer Mode, and extracting the repo zip with Explorer or `Expand-Archive` turns them
  into empty 0 KB stubs).
- _Example: local Feign calls to `payments-service` fail with a connection reset if the local proxy
  isn't running — start it before running integration tests locally._

## Deprecated / Do Not Use

- _Example: the `LegacyNotificationClient` is deprecated in favor of `NotificationClientV2`; new
  code must not add call sites to the old client._

## Active Migrations

- _Example: migrating from a shared `notifications` table to per-service outbox tables — service X
  still writes to both during the transition, see ADR-00X._

## Glossary

- _Add domain terms and internal acronyms here as they come up — anything a new hire would have to
  ask about._
