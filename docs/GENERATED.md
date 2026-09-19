# Generated vs Hand-Written Documentation

Docs that can be derived from code **are** derived from code — hand-maintaining them guarantees
drift. This file is the registry: the agent (`ai/skills/sync-docs/`) and reviewers check it
before editing anything under `docs/`.

| Doc | Source of truth | Generator | Hand-written parts |
| --- | --- | --- | --- |
| `docs/api/<service>.yaml` (OpenAPI) | Controller + DTO annotations (springdoc) | `mvn springdoc-openapi:generate` in each service's CI, output committed | none — fix the annotations, not the YAML |
| `docs/messaging/kafka-topics.generated.md` | `@KafkaListener(topics=…)` and producer topic constants across services | `scripts/generate-topic-catalog.py` | `kafka-topics.md` keeps owner, retention, and the *why* per topic; the generated file is a cross-check list, CI fails if a topic is in one and not the other |
| `docs/business/rules.generated.md` | `// BR-nnn` comments in code and tests | `scripts/check-business-rules.sh --report` | `rules.md` holds the rule text, owner, and source (contract, regulator, product decision) |
| `docs/architecture/components.generated.md` | `@RestController`, `@KafkaListener`, `@FeignClient`, `@Entity`, producer topic literals across services | `scripts/generate-components-inventory.py <workspace>` | `components.md` keeps responsibility and notable decisions; the generated file is the inventory cross-check |
| Impact table in `ai/skills/sync-docs/SKILL.md` | `ai/impact-map.yaml` | `scripts/render-impact-table.py` (CI: `--check`) | none — edit the YAML |

Rules:

- Never edit a generated file by hand. If it's wrong, the source is wrong.
- A generator that goes red in CI is a *docs bug*, treat it with the same priority as a failing
  test.
- When you add a generator, add a row here and wire it in `.github/workflows/template-checks.yml`
  (the commented `generated-docs` job is the slot).
