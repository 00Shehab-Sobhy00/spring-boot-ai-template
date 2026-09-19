# Kubernetes / Helm Deployment

Reference chart: `helm/` (in this template). Per-env values: `values-<env>.yaml`. Routing must stay
explicit and debuggable per `ai/ARCHITECTURE.md` (Infrastructure Awareness).

## Steps

1. **Start from the template chart** — `helm/` here mirrors the standard service layout
   (`deployment`, `service`, `ingress`, `virtualservice`, `destination-rule`, `hpa`). Extend the
   service's existing chart rather than restructuring it.
2. **Values, not template edits** — environment differences go in `values-<env>.yaml` overrides.
   Prefer clear per-env values over hidden defaults buried in templates.
3. **Probes** — liveness and readiness on the actuator endpoints, with startup allowances that
   reflect real cold-start time (remember the mesh sidecar adds latency in some envs — see
   `docs/deployment/networking.md` before "fixing" a probe by loosening it blindly).
4. **Resources** — explicit requests and limits. Memory limit must line up with the JVM's
   `MaxRAMPercentage` from the Dockerfile, or the OOMKiller and the JVM will fight.
5. **HPA** — scale on a metric that reflects real load for this service (CPU is the default; don't
   add custom-metric scaling without a reason). Min replicas ≥ 2 for anything production-serving.
6. **Mesh routing** — `virtualservice` / `destination-rule` changes are where staging-vs-prod
   surprises live: timeouts, retries, and mTLS settings at the mesh layer stack on top of the app's
   own client settings. Change one layer at a time and say which layer you changed.
7. **Rollout safety** — rolling update strategy with sane `maxUnavailable`; PodDisruptionBudget if
   the service is production-critical.
8. **Verify** — `helm template` renders cleanly, values overrides resolve per env, and the diff
   against the currently-deployed manifests is reviewed before apply.

## Don't

- Don't hardcode env-specific values in templates — that's what values files are for
- Don't loosen a failing probe without understanding *why* it fails — you may be masking a real
  startup problem
- Don't set mesh-level retries on top of app-level retries without accounting for the multiplication

## Related

`helm/` · `docs/deployment/` · `docs/deployment/networking.md` ·
`ai/skills/deployment/references/docker.md` · `ai/ARCHITECTURE.md`
