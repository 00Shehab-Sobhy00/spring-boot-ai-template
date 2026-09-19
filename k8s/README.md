# k8s/

Raw manifests that intentionally bypass the Helm chart — cluster-scoped or one-off resources
(namespaces, network policies, shared secrets wiring via external-secrets, etc.).

Rules:

- Anything service-shaped belongs in the Helm chart (`/helm`), not here — one paved road.
- Everything here must say **why** it can't live in the chart, in a comment at the top of the file.
- Same review bar as code: no secrets committed, changes reviewed against `docs/deployment/`.
