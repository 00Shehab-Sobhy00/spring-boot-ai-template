# Environments

| | local | staging | production |
| --- | --- | --- | --- |
| Cluster | docker-compose (`docker/docker-compose.yml`) | shared k8s + mesh | k8s + mesh |
| DB | containerized Postgres | managed, staging-sized | managed, HA |
| Kafka | single-broker container | shared cluster | production cluster |
| Config source | `application-local.yaml` + env | `values-staging.yaml` | `values-prod.yaml` |
| mTLS / mesh | off | on (this is where the surprises live — see `networking.md`) | on |
| Secrets | local env file (gitignored) | secret manager | secret manager |

Rule of thumb: a timeout/probe/retry setting tuned only against local behavior is not tuned.
Validate on staging, and read `networking.md` first.
