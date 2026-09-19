---
name: sync-docs
description: >
  Keep the repo's documentation in step with a code change: map what changed (endpoint, topic,
  entity, client, config, metric, business rule, decision) to the docs that must be updated, apply
  the updates, and report what needs a human. Run at the end of every non-trivial task and on a
  PR diff. Trigger on "update the docs", "what docs does this touch", "sync docs", "docs impact".
metadata:
  when_to_use: ["sync docs", "update the docs", "docs impact", "which docs change", "close out this task", "document what I just did"]
---
<!-- evidence-token: SKSYNC-KU8H6F — cite in the AI Run Report -->

# Sync Documentation With a Change

Documentation goes stale because updating it is a *separate* chore. This skill makes it a
**side effect of the change**: every change type has a known set of target docs, and the task
is not done until each target is either updated or explicitly handed to a human.

Follows `AGENTS.md` (single-source rule), `ai/AI_BEHAVIOR.md` (Recording New Knowledge),
`docs/business/README.md`.

## Steps

1. **Enumerate what changed.** Use the diff (`git diff --name-only <base>` or the files you
   touched this session). Classify each file by the *kind* of change using the impact table.
2. **Generated first, hand-written second.** If a target doc is generated (see
   `docs/GENERATED.md`), do not edit it by hand — run or mention the generator. Only edit the
   hand-written columns/sections (owner, retention rationale, business meaning).
3. **Apply the impact table.** For each row that matches, open the target doc and make the
   smallest correct edit. Match the existing format of the table/section — don't restructure.
4. **Business meaning check.** For any new `if`/validation/threshold on a *domain* field, ask:
   is this a business rule? If yes, it gets a `BR-nnn` id in `docs/business/rules.md` and a
   `// BR-nnn` comment on the condition and its test (see that file for the convention). If
   you're not sure whether it's a rule, list it under "Needs a human" — never invent business
   rationale.
5. **Knowledge capture.** Non-obvious gotcha or convention → `ai/PROJECT_MEMORY.md`.
   Hard-to-reverse decision with alternatives → propose an ADR (don't write it unasked).
6. **Ledger.** Add/increment this task's shape in `ai/skills/_candidates.md`
   (`ai/skills/manage-skills/references/detecting-gaps.md`).
7. **Report** in the close-out format below. Keep it short; it's a checklist, not prose.
8. **AI Run Report.** After the close-out block, emit the report defined in `ai/CAPACITY.md` — status,
   reason, the evidence tokens of every rule/skill/pattern you read, what was verified. CI parses it.

## Impact Table

The table below is **generated** from `ai/impact-map.yaml` — the same file that drives
`scripts/check-docs-impact.py` in CI and the token check in `scripts/check-ai-report.py`. Edit the
YAML, run `scripts/render-impact-table.py`, never edit the table by hand (CI checks it is in sync).

<!-- BEGIN GENERATED: impact-table (source: ai/impact-map.yaml) -->

| Changed (path or construct) | Update | Rule tokens required in the AI Run Report | CI |
| --- | --- | --- | --- |
| `Controller\.java$` / `(?<!/client)(?<!/adapter)/dto/.*\.java$` | OpenAPI annotations in code; `docs/api/error-catalog.md` for new codes; `docs/api/README.md` link if a new spec file appears | `ai/ARCHITECTURE.md`, `ai/skills/create-rest-api/SKILL.md` | error |
| `Listener\.java$` / `Consumer\.java$` | `docs/messaging/consumers.md`; `docs/architecture/components.md` "Subscribes" column | `ai/skills/kafka/SKILL.md` | error |
| `Producer\.java$` / `Publisher\.java$` / `Topics?\.java$` | `docs/messaging/kafka-topics.md` (owner, key, retention, *why*), `docs/messaging/producers.md`, `docs/messaging/schemas.md` (envelope + payload version), `components.md` "Publishes" | `ai/skills/kafka/SKILL.md`, `ai/patterns/outbox-pattern.md` | error |
| `(Retry` / `Dlq` / `DeadLetter)[^/]*\.java$` | `docs/messaging/retry-policy.md`, `docs/messaging/dlq.md` | `ai/skills/kafka/SKILL.md`, `ai/patterns/retry-pattern.md` | error |
| `src/main/resources/liquibase/` | `docs/database/schema-conventions.md` only if a convention changed; ADR if a modeling decision; `PROJECT_MEMORY.md` → Active Migrations for expand/contract in flight | `ai/BACKEND_RULES.md`, `ai/skills/database/SKILL.md` | error |
| `Client\.java$` / `FeignClient` / `/client/dto/.*\.java$` | `components.md` "Consumes" column + diagram; `docs/deployment/networking.md` if it needs proxy/mesh config | `ai/skills/feign-client/SKILL.md`, `ai/skills/resilience/SKILL.md` | error |
| `application[^/]*\.ya?ml$` | `docs/deployment/environments.md`; comment in `helm/values.yaml` if it has a chart value | `ai/BACKEND_RULES.md` | error |
| `helm/templates/` | `helm/README.md` ground rules if a rule changed; `docs/deployment/runbook.md` if it affects rollout | `ai/skills/deployment/SKILL.md` | error |
| `src/main/java/.*(Alert` / `Metric` / `Metrics)[^/]*\.java$` | `docs/observability/metrics-catalog.md`; `slos.md`; **every alert gets a `runbook.md` row** | `ai/skills/observability/SKILL.md` | error |
| `(Flag` / `Toggle)[^/]*\.java$` | `ai/patterns/feature-flags.md` inventory section; removal date in `PROJECT_MEMORY.md` | `ai/patterns/feature-flags.md` | warn |
| Added line containing `BR-[0-9]{3}` | `docs/business/rules.md` (`BR-nnn`) — or hand to a human | `ai/skills/sync-docs/SKILL.md` | error |
| `` | An annotated `BR-nnn` condition was modified or removed. Update that rule's row in `docs/business/rules.md` (or hand to its Owner) — the owner column is who may change it. | `ai/skills/sync-docs/SKILL.md` | error |
| `ai/ARCHITECTURE\.md$` | `enforcement/archunit/ArchitectureRulesTest.java` — the rule you changed in prose must change in the executable form too, same PR | `ai/ARCHITECTURE.md` | error |
| `src/main/java/` | `ai/skills/_candidates.md` (task shape) | — | warn |
| New microservice | `components.md` inventory row + per-service section + diagram; `docs/architecture/context.md`; `docs/deployment/environments.md` | — | guidance |
| Domain term used for the first time | `docs/business/domain-glossary.md` | — | guidance |
| Deprecating a class/endpoint/topic | `PROJECT_MEMORY.md` → Deprecated / Do Not Use; deprecation window in `docs/api/conventions.md` terms | — | guidance |

<!-- END GENERATED: impact-table -->

CI does not only check that a target doc *changed*. It checks that the doc diff adds a real line
and that identifiers introduced in code (topic names, class names, `BR-nnn`, config keys, metric
names) appear in it. "Touched the file" is not "updated the file".

## Close-Out Format

```text
### Docs sync
Updated:
- docs/messaging/kafka-topics.md — added `orders.order.cancelled` row
- docs/messaging/producers.md — OrdersEventPublisher
Generated (needs regeneration in CI, not edited): docs/api/orders-service.yaml
Needs a human:
- Is the 15-minute cancellation window a contractual rule? → docs/business/rules.md
Knowledge: proposed 1 line for ai/PROJECT_MEMORY.md (Known Gotchas)
Ledger: "adding a Kafka producer" → Count 2

### AI Run Report
Status: OK
Reason: none
Model: <as reported by the tool>
Task-shape: adding a Kafka producer
Rules-read: CAPA-…, BEHV-…, BACK-…
Skills-applied: SKKAFK-…, SKSYNC-…
Patterns-applied: PATOUTB-…
Files-edited: 4
Verified: mvn -q test -pl orders-service
Unverified: none
Assumptions: none
Needs-human: Is the 15-minute cancellation window a contractual rule?
Checkpoint: n/a
```

(That example is `DEGRADED` by definition — `Needs-human` is non-empty — and CI will say so.)

## Don't

- Don't hand-edit a generated file — it's overwritten on the next build and your edit vanishes
  silently
- Don't write business rationale you inferred from code; a wrong "why" is worse than a missing one
- Don't restructure a doc while syncing it — smallest correct edit, same format as the neighbors
- Don't skip the "Needs a human" section to look finished; an honest empty list is fine, a hidden
  gap is not
- Don't write `Status: OK` with anything unverified — `ai/CAPACITY.md` defines OK; CI enforces it
- Don't record secrets, hostnames of internal systems, or customer data in any doc

## Related

`ai/impact-map.yaml` · `ai/CAPACITY.md` · `docs/GENERATED.md` · `docs/business/rules.md` ·
`ai/PROJECT_MEMORY.md` · `ai/skills/_candidates.md`
· `ai/prompts/sync-docs.md` (the headless/PR version) · `.github/workflows/template-checks.yml`
(what CI enforces)
