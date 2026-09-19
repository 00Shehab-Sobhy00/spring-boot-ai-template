# Onboarding: First Day on This Codebase

> Target: a new engineer runs the service locally and understands the shape of the system in
> under an hour. If it takes longer, this document is the bug — fix it here, not in Slack.

## 1. Prerequisites

- JDK 21 (check with `java -version`)
- Maven
- Docker (for Testcontainers and the local stack)
- _add: VPN / registry credentials / any internal access needed_

## 2. Run the Local Stack

```bash
docker compose -f docker/docker-compose.yml up -d
```

Brings up Postgres, Redis, and Kafka — see `docs/deployment/environments.md` for what differs
from staging and production.

## 3. Run the Service

```bash
cd <service-directory>          # not the workspace root — there is no reactor POM
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

Verify: `curl localhost:8080/actuator/health` returns UP.

## 4. Run the Tests

```bash
mvn verify                      # unit + integration (Testcontainers needs Docker running)
```

## 5. Read These, In This Order

1. `docs/business/business-overview.md` — what the product does and why
2. `ai/ARCHITECTURE.md` — layering and service boundaries
3. `docs/architecture/components.md` — which service owns what
4. `ai/PROJECT_MEMORY.md` — the gotchas you'd otherwise learn the hard way
5. `ai/BACKEND_RULES.md` — the conventions your first PR will be reviewed against

## 6. Working With the AI Assistant

This repo is wired for **opencode** via `opencode.json` — it loads the rule files (`AGENTS.md` +
`ai/*.md`) as instructions and discovers every skill under `ai/skills` automatically. Just start
opencode in the repo root; no extra flags needed. Before a common task, ask for the relevant
skill — e.g. "add an endpoint" loads the REST recipe automatically.

## 7. Your First Change

Pick something small. Open a PR. The PR template's checklist is the same one reviewers use —
read it before you start, not after.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| Tests fail with container errors | Docker isn't running |
| Feign calls fail locally with connection reset | Local proxy not running — see `ai/PROJECT_MEMORY.md` |
| Port already in use | Another service instance, or the compose stack, is up |
| _add yours here_ | |

**If you hit something not listed here, add it.** That is the single most useful contribution a
new joiner makes.
