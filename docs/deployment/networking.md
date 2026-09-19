# Networking, Proxies & the Mesh

> The page behind every "works locally, fails in staging" mystery. Referenced by
> `ai/BACKEND_RULES.md` (Integrations), `ai/patterns/retry-pattern.md`, and the deployment skills.

## Layers a Request Crosses

```text
client → ingress → mesh sidecar (in) → app → mesh sidecar (out) → [proxy] → downstream sidecar (in) → downstream app
```

Each layer can independently apply timeouts, retries, connection pooling, and TLS. Symptoms rarely
point at the layer that caused them.

## Known Behaviors to Account For (fill in your platform's specifics)

- **Sidecar cold start** — the first request after a pod (re)start pays sidecar warm-up latency;
  don't tune client timeouts from a cold-start measurement.
- **Retry multiplication** — app-level retries × mesh-level retries = a retry storm during a
  downstream incident. Change one layer at a time; document which layer owns retries for each route.
- **Proxy resets** — long-idle connections may be reset by intermediate proxies; configure client
  keep-alive/pool eviction below the proxy's idle timeout.
- **mTLS in staging/prod but not local** — cert/SNI issues will only ever reproduce in-cluster.
- **Feign defaults** — never rely on default timeouts; set connect/read explicitly per client
  (`ai/BACKEND_RULES.md`).

## When Changing Timeouts / Probes / Retries

1. Identify which layer you're changing (app config? mesh VirtualService? ingress?) and say so in
   the PR.
2. Check the interaction with the layers above/below.
3. Validate on staging, not just locally.
4. If you discover a new platform quirk, record it in `ai/PROJECT_MEMORY.md` → Environment Quirks.
