# Runbook (Template)

## Deploy

1. CI green on the release commit (build + tests + image scan).
2. `helm upgrade --install <service> ./helm -f values-<env>.yaml` (or via the platform's CD
   pipeline).
3. Watch: rollout status, pod restarts, error rate, latency, consumer lag, DLQ depth.

## Rollback

- `helm rollback <service> <revision>` — safe when the deploy contained no irreversible migration.
- If a migration shipped: check `docs/database/migrations.md` — expand/contract migrations are
  rollback-safe; destructive ones need the documented recovery plan instead.

## Incident Quick Checks

| Symptom | First looks |
| --- | --- |
| 5xx spike | error `origin` field (internal vs external — `docs/api/error-catalog.md`), recent deploys, downstream status |
| Latency spike | DB slow queries, N+1 regressions, downstream latency, mesh retries amplifying |
| Consumer lag | consumer errors → retry loop? poison message blocking a partition? (`docs/messaging/dlq.md`) |
| DLQ depth > 0 | failure headers on the DLQ records → `docs/messaging/dlq.md` replay procedure |
| Pods restarting | probe config vs real startup time (`ai/skills/deployment/references/kubernetes.md`), OOM vs JVM memory settings |

After any incident with a durable lesson: `ai/PROJECT_MEMORY.md`.
