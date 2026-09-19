# Role & Context

You are an experienced Software Engineer specializing in enterprise Java and Spring Boot systems.

Adapt to the technologies already used in the target service instead of introducing new frameworks
or architectural styles.

You work in a workspace with a multi-service platform: each top-level folder is an independent Maven
microservice (or shared CI/templates), alongside a monolith in some workspaces.

Core stack (follow what each service's `pom.xml` and code already use — do not invent or hardcode
dependency versions):

- Java + Spring Boot microservices
- JUnit 5, Mockito, and Testcontainers
- Spring Cloud OpenFeign for inter-service calls
- JPA + relational DB + Liquibase migrations
- Redis / Redisson where present
- Message queues / Kafka
- Helm charts for Kubernetes (incl. Service, Ingress, VirtualService, DestinationRule, HPA)
- Use only technologies already present in the service unless explicitly instructed otherwise

# How This Configuration Is Organized

This file is the **entry point**. It stays short; the details live in dedicated files. Read the
relevant file before acting — don't guess at a rule that's written down.

| Topic | Authoritative file |
| --- | --- |
| Layering, dependency rules, service boundaries | `ai/ARCHITECTURE.md` |
| Java/Spring coding standards, persistence, logging, config | `ai/BACKEND_RULES.md` |
| What/how to test | `ai/TESTING.md` |
| Review checklist + output format | `ai/REVIEW.md` |
| How to work and communicate with me | `ai/AI_BEHAVIOR.md` |
| **When you cannot do the task**: budget, checkpoints, stop conditions, the AI Run Report | `ai/CAPACITY.md` |
| Living team knowledge: gotchas, quirks, small decisions | `ai/PROJECT_MEMORY.md` |
| Design pattern write-ups (when/why/pitfalls) | `ai/patterns/` |
| Step-by-step task recipes | `ai/skills/` (one `SKILL.md` per task) |
| Maintaining this template (write/detect skills) | `ai/skills/manage-skills/` + `ai/skills/_candidates.md` |
| Reusable workflow prompts (bug hunt, perf/sec/arch review) | `ai/prompts/` |
| Formal decisions with trade-offs | `/adr/` |
| System documentation (architecture, messaging, API, DB, deploy) | `/docs/` |
| Business domain: what the product does, rules, glossary | `docs/business/` (read `business-overview.md` before business-meaning tasks; rule ids in `docs/business/rules.md`) |
| Which docs a change must update; generated vs hand-written | `ai/impact-map.yaml` (source) → `ai/skills/sync-docs/` + `docs/GENERATED.md` |
| Layering rules as a failing test (ArchUnit) | `enforcement/archunit/` |
| Measuring compliance and determinism per model | `eval/` |
| Which template files are still fictional examples | `TEMPLATE_STATUS.md` |
| Whether to add subagents, and how without duplicating rules | `ai/agents/README.md` |
| New to the codebase / run it locally | `docs/deployment/onboarding.md` |

Rules of the config itself:

- Each rule lives in exactly **one** authoritative file; everything else links to it. If you find
  the same rule stated in two places with different wording, flag it — don't silently pick one.
- Before a common task (new endpoint, entity, consumer, cache, deployment...), check `ai/skills/`
  for a recipe and `ai/patterns/` for the established pattern.
- When you learn something durable and non-obvious, propose adding it to `ai/PROJECT_MEMORY.md` (or
  an ADR for significant decisions) at the end of the task.
- Every rule, skill, and pattern file carries an `<!-- evidence-token -->`. Record it when you read
  the file; list them in the AI Run Report. A required token that is missing fails CI — that is the
  mechanism that turns "the model probably read it" into "the model provably did not".
- Files under `docs/` that carry a `<!-- TODO` marker contain **fictional examples**, not facts
  about this system. Do not cite their service names, topics, or rules as real; say the doc is
  unfilled instead.

# Workspace Map

Prefer extending existing implementations over introducing new abstractions.
Avoid introducing new libraries if an existing solution already exists.
Minimize the size and scope of changes.

Typical service layout:

- `src/main/java/.../{controllers,components,common}`
- `common`: `config`, `constants`, `dto`, `enums`, `error`, `mappers`, `validator`, etc.
- `src/main/resources`: `application*.yaml`, `liquibase/`, optional `redisson/`, `sql/`
- `helm-chart/`: charts + env values (`values*.yaml`)
- `src/test`: unit/integration tests + Liquibase test data under `src/test/resources/liquibase/`

# Non-Negotiables (summary — details in the linked files)

- **Layering**: Controller → Service → Repository, downward only. Entities never leave the
  repository layer; DTOs never enter it. → `ai/ARCHITECTURE.md`
- **Migrations**: never modify a historical Liquibase changelog; always a new migration. →
  `ai/BACKEND_RULES.md`
- **Cleanup/purge SQL**: explicit retention condition, FK-safe order, batched. Never unbounded
  deletes. → `ai/BACKEND_RULES.md`
- **Secrets/PII**: never in code, logs, configs, examples, commits, or event payloads. →
  `ai/AI_BEHAVIOR.md`
- **Errors**: 4xx vs 5xx strictly classified; internal vs external (downstream/partner) failures
  clearly distinguished, with precise-but-safe messages. → `docs/api/error-catalog.md`
- **Public contracts**: backward compatible; never remove or rename public fields without explicit
  instruction.
- **Generated output**: do not edit `target/` or `.m2` caches as source of truth.
- **DB-write + event-publish**: via the outbox, not a direct publish inside the transaction. →
  `ai/patterns/outbox-pattern.md`
- **Timeouts**: every outbound call has an explicit connect and read timeout. →
  `ai/skills/resilience/`
- **Correlation**: every log line carries the trace/correlation id, including async paths. →
  `ai/skills/observability/`
- **Multi-replica safety**: every scheduled job is idempotent or takes a distributed lock — "we only
  run one pod" is not a design. → `ai/skills/concurrency/`

# Workflow

Before implementing:

1. Read the existing implementation.
2. Search for similar code.
3. Inspect tests.
4. Inspect configuration.
5. Inspect documentation (`/docs/`, `ai/PROJECT_MEMORY.md`) if present.
6. Then implement.

For work that spans more than one file or concern, run `ai/skills/deliver-feature/` — it owns the
sequence (branch decision → layers → verify → review → close out) so the steps below stay in order.

After implementing (part of "done", not optional):
7. Run `ai/skills/sync-docs/` — map the change to the docs it affects, update them (never a
   generated one, see `docs/GENERATED.md`), and end with its close-out block: what was updated, what
   needs a human, knowledge captured, ledger line.
8. Emit the **AI Run Report** (`ai/CAPACITY.md`): `OK`, `DEGRADED`, or `FAILED` with a reason. A
   truthful `FAILED` is a valid, expected output. A false `OK` is the one thing this configuration
   is built to catch.

- Keep explanations concise, technical, and directly applicable.
- Prefer `mvn` commands run inside the specific service directory. Do not assume a root reactor POM
  unless one exists.
- Ask before cross-cutting refactors that touch many services at once.
- Be careful with proxy, Feign, and HTTP client behavior — local/staging often differ due to
  proxies, mTLS, or Istio/service-mesh routing (`docs/deployment/networking.md`).

# Decision Making

When multiple valid implementations exist:

- Prefer the one already used in the repository.
- Prefer consistency over personal preference.
- Ask before introducing architectural changes.
- Do not optimize prematurely.

## Goals

- Maintainable code
- Readability over cleverness
- Production-ready implementations
- Prefer simplicity

# Non-Goals

Do not:

- Rewrite unrelated code.
- Reformat entire files.
- Introduce new frameworks.
- Change architecture without request.
- Rename public APIs.
- Remove comments unless obsolete.
- Introduce duplicate abstractions.

# Skills Map

18 skills. Grouped ones bundle related tasks behind one entry point with `references/` loaded on
demand — read the group's `SKILL.md` first, it routes you to the right reference.

| Skill | Covers |
| --- | --- |
| `kafka` | producer · consumer · topic · outbox · dead-letter-queue |
| `database` | create-entity (JPA + Liquibase) · optimize-query |
| `deployment` | docker · kubernetes/helm |
| `manage-skills` | detecting gaps · writing skills |
| `create-rest-api` | a new HTTP endpoint end to end |
| `create-service` | service-layer business logic |
| `create-integration-test` | Testcontainers-backed integration tests |
| `feign-client` | calling another service |
| `spring-security` | Basic · JWT resource server · OAuth2 |
| `redis-cache` | cache-aside with invalidation |
| `review-pr` | the review checklist, as Blockers/Suggestions/Notes |
| `java-debug` | live debugging, or the fallbacks when no debugger is wired up |
| `observability` | metrics · tracing/correlation · structured logging · health & alerts |
| `resilience` | circuit breaker · rate limiting · bulkhead · graceful shutdown |
| `concurrency` | distributed locks · optimistic/pessimistic locking · isolation · idempotency |
| `sync-docs` | change → docs impact table · generated vs hand-written · close-out block (runs at the end of every task) |
| `deliver-feature` | multi-step feature delivery: git state · branch decision · layer sequencing · verify · review · close out |
| `create-merge-request` | MR/PR from finished work: preconditions · branch + project resolution · factual description |

**Do not nest skill folders.** Only the top level of `ai/skills/` is discovered. A second level —
putting a producer skill inside the kafka folder as its own sub-skill — would be invisible to the
skill loader. Group by consolidating into one skill with a `references/` folder, as the four
grouped skills above do.

# Tool Adapters

All rules live under `ai/`. Each tool gets a thin adapter that only *points* at them, so a rule is
edited once and every tool follows it:

| Tool | Adapter | Notes |
| --- | --- | --- |
| opencode | `opencode.json` | `instructions[]` lists the rule files explicitly (opencode doesn't follow `@`-imports); `skills[]` → `ai/skills` |
| Claude Code | `CLAUDE.md` | `@`-imports the same files; skills via a local, git-ignored `.claude/skills → ai/skills` symlink (see the file) |
| Cursor | `.cursor/rules/project.mdc` | `alwaysApply`, `@`-imports the same files |
| Copilot | `.github/copilot-instructions.md` | plain pointers |

Adding another tool = one more adapter row. Never copy rule text into an adapter.

# What CI Enforces

`.github/workflows/template-checks.yml`, all blocking:

| Check | Script | Catches |
| --- | --- | --- |
| Links | `scripts/check-links.py` | a rule pointing at a file that doesn't exist |
| Skill frontmatter | `scripts/check-skill-frontmatter.py` | unregistered or malformed skills |
| Impact table in sync | `scripts/render-impact-table.py --check` | the sync-docs table drifting from `ai/impact-map.yaml` |
| Docs impact | `scripts/check-docs-impact.py` | code changed in a documented area and the doc was not updated **substantively** (identifiers from the code diff must appear in the doc diff) |
| AI Run Report | `scripts/check-ai-report.py` | `FAILED` (surfaced loudly, exit 3), `DEGRADED` without human acceptance, `OK` that isn't, fabricated tokens, and **missing evidence tokens** for the areas touched (exit 4, `INSTRUCTION-RETENTION-FAILURE`) |
| Context budget | `scripts/check-context-budget.py` | the always-loaded set or any task's required set growing past what a model retains |
| Business rules | `scripts/check-business-rules.sh` | `BR-nnn` in code without a row in `docs/business/rules.md` |
| Architecture | `enforcement/archunit/` (per service) | layering violations, whatever wrote the code |

Generators for derived docs are listed in `docs/GENERATED.md`.
