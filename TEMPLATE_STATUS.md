# Template Personalization Status

The template ships with fictional examples (orders/payments/Stripe). Until a file below is
personalized, the agent may "learn" fake topics and services from it. Tick each item as you go;
delete this file when everything is done.

| File | Contains | Personalized? |
| --- | --- | --- |
| `docs/business/business-overview.md` | **highest leverage** — what the product does, money flow, non-obvious rules | ☐ |
| `docs/business/domain-glossary.md` | your ubiquitous language | ☐ |
| `docs/business/rules.md` | real BR-nnn rules (replace the 3 examples) | ☐ |
| `docs/architecture/components.md` | real service inventory + diagram | ☐ |
| `docs/architecture/context.md` | real external systems | ☐ |
| `docs/architecture/sequence-diagrams.md` | 2–3 real critical flows | ☐ |
| `docs/messaging/kafka-topics.md` | real topics; then run `scripts/generate-topic-catalog.py` | ☐ |
| `docs/messaging/producers.md` / `consumers.md` / `schemas.md` | real producers, groups, envelopes | ☐ |
| `docs/observability/metrics-catalog.md` / `slos.md` | real metrics and targets | ☐ |
| `docs/deployment/environments.md` / `networking.md` | real envs, proxies, mesh quirks | ☐ |
| `docs/deployment/onboarding.md` | real prerequisites (VPN, registries) | ☐ |
| `adr/ADR-00*.md` | real dates, deciders — or delete the ones that aren't your decisions | ☐ |
| `ai/PROJECT_MEMORY.md` | remove `_Example:_` lines; add your idempotency header name | ☐ |
| `helm/values.yaml` | real registry, resource sizes | ☐ |
| `AGENTS.md` → Core stack | remove anything you don't use (and the matching skill/pattern/ADR) | ☐ |
| `enforcement/archunit/ArchitectureRulesTest.java` | copy into each service, set `BASE_PACKAGE`, uncomment the `architecture` CI job | ☐ |
| `eval/` | run once per model you intend to use; record `not-capable` tasks in `ai/PROJECT_MEMORY.md` | ☐ |
| GitHub labels `ai:ok`, `ai:needs-attention` | create them so the `ai-run-report` job can label PRs | ☐ |

Not personalized = fictional. The agent is told (in `AGENTS.md`) that files with a `<!-- TODO`
marker are examples, not facts.

All CI checks are **blocking from day one**. The old `--warn` grace period is gone: a warning
nobody reads is how the habit never forms. Use `Docs-Impact: none — <reason>` in the PR body for a
genuinely doc-neutral change, and `Accepted-Degraded: <reason>` to merge unverified work knowingly.
