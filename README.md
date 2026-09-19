# Spring Boot Enterprise AI Template

A complete AI configuration template for enterprise Java / Spring Boot microservice platforms, with
thin adapters for **opencode, Claude Code, Cursor, and Copilot**. Drop it into a repo and every tool
works from a single set of rules, patterns, recipes, and docs — everything authoritative lives under
`ai/` (cross-tool `AGENTS.md` + `SKILL.md` formats); the adapters only point at it.

## The One Design Rule

> **Every rule lives in exactly one file. Everything else links to it.**

The authoritative content lives under `ai/` (and `docs/`, `adr/`). `opencode.json` is a thin adapter
that *points* at those files — so you edit a rule once and the agent picks it up. No drift, no
duplicated copies to keep in sync.

## What Makes It Model-Agnostic

Markdown rules are a request. These are enforcement, and they work the same whichever model or tool
wrote the code:

| Failure mode of spec/rule-driven AI work | What this template does about it | Where |
| --- | --- | --- |
| Rules silently not applied | Layering rules are an ArchUnit test that fails the build | `enforcement/archunit/` |
| Docs "touched" to pass CI | Docs-impact checks that identifiers from the code diff appear in the doc diff | `scripts/check-docs-impact.py` |
| Same rule in two places drifting apart | One YAML drives the sync-docs table *and* the CI check | `ai/impact-map.yaml` |
| Model read a rule, then lost it mid-task | Every rule file carries a random evidence token; the AI Run Report must cite the ones required for the areas touched, or CI fails with `INSTRUCTION-RETENTION-FAILURE` | `ai/CAPACITY.md`, `scripts/check-ai-report.py` |
| Model can't do the task and says "done" anyway | Three-state outcome (`OK` / `DEGRADED` / `FAILED`) with a fixed reason list and a resumable checkpoint; `FAILED` is surfaced loudly, `DEGRADED` needs a human's explicit acceptance, `OK` is downgraded if anything is unverified | `ai/CAPACITY.md` |
| Instruction load creeps past what a model retains | Token budget per always-loaded set and per task area, checked in CI | `scripts/check-context-budget.py` |
| Non-determinism assumed instead of measured | Run each canonical task N times per model; score compliance and similarity; output the list of tasks this model is **not capable** of | `eval/` |
| Fictional bootstrap docs | Service inventory generated from code | `scripts/generate-components-inventory.py` |

What it still does not solve — on purpose, so nobody over-trusts it — is listed at the bottom of
`ai/CAPACITY.md`.

## Layout

```text
├── AGENTS.md                  # Entry point: role, stack, non-negotiables, and a routing table to everything else
├── opencode.json              # opencode adapter — CLAUDE.md, .cursor/rules/, .github/copilot-instructions.md are the others
├── TEMPLATE_STATUS.md         # which files are still fictional examples — delete when fully personalized
├── enforcement/archunit/      # ai/ARCHITECTURE.md as a failing test — copy into each service
├── eval/                      # per-model compliance + determinism harness; outputs the "not-capable" list
│
├── ai/                        # ← the authoritative content
│   ├── ARCHITECTURE.md        #   layering, dependency rules, service boundaries
│   ├── BACKEND_RULES.md       #   Java/Spring standards, persistence, logging, config
│   ├── TESTING.md             #   what/how to test
│   ├── REVIEW.md              #   review checklist + Blockers/Suggestions/Notes format
│   ├── AI_BEHAVIOR.md         #   how the agent works & communicates
│   ├── CAPACITY.md            #   OK / DEGRADED / FAILED protocol, budgets, checkpoints, evidence tokens, AI Run Report
│   ├── impact-map.yaml        #   SINGLE SOURCE: change → docs to update → rule tokens required (drives CI + sync-docs table)
│   ├── PROJECT_MEMORY.md      #   LIVING team knowledge: gotchas, quirks, small decisions
│   ├── patterns/              #   when/why/pitfalls: rest-api, async-events, outbox, saga, cache-aside, retry,
│   │                          #   security-authentication, design-patterns
│   ├── skills/                #   18 step-by-step task recipes (SKILL.md format, Agent Skills standard) — incl. deliver-feature and sync-docs
│   ├── agents/                #   OPTIONAL subagent layer — empty by default; README explains when it pays off
│   └── prompts/               #   paste-in workflows: bug-investigation, performance/security/architecture review
│
├── docs/                      # system documentation (templates with worked examples)
│   ├── GENERATED.md           #   registry: which docs are derived from code, and by what
│   ├── architecture/          #   context, components, sequence diagrams (C4 + mermaid)
│   ├── messaging/             #   topic catalog, producers, consumers, retry policy, DLQ, schemas
│   ├── api/                   #   error catalog (4xx/5xx + internal/external), conventions
│   ├── database/              #   migrations workflow, schema conventions
│   ├── business/              #   business overview, glossary, rules register (BR-nnn ids linked from code)
│   └── deployment/            #   environments, networking/mesh gotchas, runbook
│
├── adr/                       # decision records: template + Kafka, Redis, Outbox examples with real trade-offs
│
├── scripts/                   # CI checks: link checker, skill frontmatter, docs-impact, topic + business-rule cross-checks
├── .github/                   # PR template, copilot adapter, template-checks workflow
├── docker/                    # reference multi-stage Dockerfile + local docker-compose stack
├── helm/                      # reference chart: deployment/service/ingress/virtualservice/destination-rule/hpa
└── k8s/                       # raw manifests that legitimately bypass Helm (rare, must justify)
```

## How the Pieces Relate

| Layer | Question it answers | Changes how often |
| --- | --- | --- |
| `AGENTS.md` | "Where is everything, and what's non-negotiable?" | Rarely |
| `ai/*.md` rule files | "What must the code look like / how should you work?" | Rarely, deliberately |
| `ai/patterns/` | "**Why** do we do it this way, and when not to?" | Occasionally |
| `ai/skills/` | "**How exactly** do I do task X here, step by step?" | When the process changes |
| `ai/prompts/` | "Run this whole workflow (bug hunt, sec review) properly" | Occasionally |
| `adr/` | "Why did we choose this, and what did it cost?" | Append-only |
| `ai/PROJECT_MEMORY.md` | "What would a new senior learn the hard way?" | **Constantly** — humans *and* the agent add to it |
| `docs/` | "How does the system actually work?" | With the system |

## Getting Started

1. **Copy the template** into your repo root (or a shared configs repo).
2. **Personalize the facts**: service names in `docs/architecture/components.md`, real topics in
   `docs/messaging/kafka-topics.md`, real dates/deciders in the ADRs, your idempotency header in
   `ai/PROJECT_MEMORY.md`.
3. **Prune what you don't use** — no Redis? Delete `redis-cache` skill, `cache-aside` pattern,
   ADR-002, and their references.
4. **opencode picks it up automatically** via `opencode.json`: the rule files load as instructions,
   and all skills under `ai/skills` are discovered — no copies, no symlinks, nothing to drift or
   break on Windows.
5. **Keep it alive** — the template only pays off if `PROJECT_MEMORY.md`, the topic catalog, and the
   ADR index stay current. Three mechanisms do that:
   - the agent ends every task with `ai/skills/sync-docs/` (change → docs impact table → close-out
     block);
   - derived docs are generated, not written (`docs/GENERATED.md`);
   - CI refuses drift: broken paths, invalid skills, and code changed in a documented area without
     its docs (`.github/workflows/template-checks.yml`). Start it in `--warn` mode, make it blocking
     once the habit sticks.
6. Track what's still fictional in `TEMPLATE_STATUS.md`; delete it when done.

## Extending

- **New rule** → the one authoritative file it belongs in; add a pointer elsewhere only if discovery
  needs it.
- **New recurring task** → a new `ai/skills/<name>/SKILL.md`. Nothing else to register.
- **New "why do we…"** → `ai/patterns/`, and an ADR if it was a real decision with alternatives.
- **New tool** (Windsurf, Cline, …) → a thin adapter file pointing at `AGENTS.md`, following the
  same no-duplication rule.
