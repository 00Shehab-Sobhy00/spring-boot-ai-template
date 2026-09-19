# Graceful Shutdown

Every deploy, scale-down, and pod eviction terminates instances. Done badly, each one drops
in-flight requests and half-processed messages. Users experience deploys as errors.

## The Sequence That Must Happen

1. Orchestrator sends SIGTERM
2. **Readiness probe starts failing immediately** — the load balancer stops sending new traffic
3. In-flight HTTP requests are allowed to finish (within a grace period)
4. Kafka consumers stop polling, finish and commit what's in hand
5. Scheduled tasks and timers stop accepting new work
6. Connection pools and executors close
7. Process exits — before the orchestrator's termination grace period runs out

## Steps

1. **Enable the framework's graceful shutdown** and set an explicit grace period. Spring Boot
   supports this directly; the default is "immediate", which is the wrong default for production.
2. **The Kubernetes `terminationGracePeriodSeconds` must exceed the app's shutdown timeout.**
   If the app needs 30s and the orchestrator kills at 20s, graceful shutdown never completes and
   you've configured a lie. Check both numbers together — see
   `ai/skills/deployment/references/kubernetes.md`.
3. **Add a preStop delay** if the load balancer takes time to notice readiness dropped. Without
   it, traffic keeps arriving at a pod that is already shutting down — a classic source of
   deploy-time 502s.
4. **Kafka consumers**: ensure the container stops polling and commits offsets on shutdown.
   Uncommitted offsets mean redelivery — safe if consumers are idempotent (they must be —
   `ai/skills/kafka/`), but it inflates duplicate processing on every deploy.
5. **Custom executors and schedulers** must be registered with the application lifecycle so they
   are shut down with the context — otherwise timers fire against a half-torn-down context and
   throw confusing exceptions during every deploy.
6. **Test it**: send SIGTERM under load and assert zero failed requests.

## Don't

- Don't leave the shutdown grace period at the default and assume it's handled
- Don't set the app's timeout longer than the orchestrator's grace period
- Don't leave custom thread pools unmanaged by the Spring lifecycle
- Don't treat deploy-time errors as normal — they are a configuration bug, not a cost of doing
  business
