# Reference Helm Chart

The standard service chart layout used across the platform. Copy into a service as `helm-chart/`,
set the values, and keep environment differences in `values-<env>.yaml` — never hardcoded in
templates. Recipe & conventions: `ai/skills/deployment/references/kubernetes.md`.

```text
helm/
├── Chart.yaml
├── values.yaml            # sane defaults
├── values-staging.yaml    # staging overrides only
├── values-prod.yaml       # prod overrides only
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── virtualservice.yaml
    ├── destination-rule.yaml
    └── hpa.yaml
```

Ground rules encoded in the templates:

- Probes on actuator endpoints, with startup allowances that respect sidecar cold start
  (`docs/deployment/networking.md`)
- Explicit resource requests/limits; memory limit aligned with the image's `MaxRAMPercentage`
- Rolling updates with bounded `maxUnavailable`; min 2 replicas for production-serving workloads
- Mesh routing (`virtualservice`/`destination-rule`) explicit and reviewed — mesh retries/timeouts
  stack with app-level ones
