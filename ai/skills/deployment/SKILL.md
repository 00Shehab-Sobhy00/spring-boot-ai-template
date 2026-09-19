---
name: deployment
description: >
  Containerize and deploy a service — Dockerfile, image build, Helm chart, Kubernetes manifests,
  probes, resources, autoscaling, and mesh routing. Use when containerizing, editing charts,
  fixing probes or scaling, or when pods misbehave.
metadata:
  when_to_use: ["dockerize", "write a Dockerfile", "deploy to Kubernetes", "edit the Helm chart", "pods keep restarting", "add an HPA", "fix the readiness probe"]
---
<!-- evidence-token: SKDEPL-VDP1PA — cite in the AI Run Report -->

# Deployment

Two stages, one pipeline. Read the reference for the stage you're on.

| You want to... | Read |
| --- | --- |
| Build or fix a container image | `references/docker.md` |
| Deploy, scale, or route the service in the cluster | `references/kubernetes.md` |

They are coupled in one place that catches people out: **the container's memory settings and the
pod's memory limit must agree.** If `MaxRAMPercentage` in the image and the limit in the chart
disagree, the JVM and the OOMKiller will fight and the pod restarts under load. Changing one
means checking the other.

## Rules That Apply to Both

**1. Non-root, always.** The runtime stage runs as a dedicated non-root user, and the pod's
securityContext enforces it. No exceptions for convenience.

**2. No secrets in images or committed values files.** Configuration comes from env vars and the
secret manager — see `ai/BACKEND_RULES.md` (Configuration).

**3. Environment differences live in `values-<env>.yaml`.** Never hardcoded in templates, never
baked into the image. One image, many environments.

**4. Local and staging are not production.** Proxies, mTLS, and mesh sidecars change latency and
failure behavior. Read `docs/deployment/networking.md` before tuning any timeout, probe, or
retry — and say which layer you changed.

**5. Retries stack across layers.** App-level retries multiply with mesh-level retries. Decide
which layer owns retries per route and don't set both blindly.

## Don't

- Don't loosen a failing probe without understanding why it fails — you may be masking a real
  startup problem
- Don't run as root in the runtime stage
- Don't copy the fat jar as a single layer; you lose all build caching
- Don't hardcode env-specific values in Helm templates

## Related

`docker/Dockerfile` · `helm/` · `docs/deployment/` · `docs/deployment/networking.md` ·
`ai/ARCHITECTURE.md` (Infrastructure Awareness)
