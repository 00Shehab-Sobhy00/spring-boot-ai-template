# Dockerize a Spring Boot Service

Reference Dockerfile: `docker/Dockerfile` (in this template). Compose for local dev:
`docker/docker-compose.yml`.

## Steps

1. **Start from the template** — copy `docker/Dockerfile` into the service and adjust the artifact
   name; don't write one from scratch if the template already encodes the conventions.
2. **Multi-stage build** — build stage with the full JDK + Maven cache-friendly layering (`pom.xml`
   copied and dependencies resolved before sources), runtime stage on a slim JRE base.
3. **Layered jar** — use Spring Boot's layertools extraction so dependency layers cache across
   builds and only the application layer changes on a code-only change.
4. **Non-root user** — the runtime stage runs as a dedicated non-root user. No exceptions for
   convenience.
5. **JVM settings** — respect container memory limits (`-XX:MaxRAMPercentage` rather than a
   hardcoded `-Xmx`); pass through `JAVA_OPTS` for per-env tuning.
6. **Health** — expose the actuator port; readiness/liveness probing is Kubernetes' job (see
   `ai/skills/deployment/references/kubernetes.md`), but the image must not do anything that breaks
   probe endpoints (e.g. lazy init that makes readiness lie).
7. **No secrets in the image** — configuration via env vars / mounted config, per
   `ai/BACKEND_RULES.md` (Configuration). `.dockerignore` excludes `target/` junk, `.git`, and local
   env files.
8. **Verify** — build it, run it with a memory limit, hit the health endpoint, and check the image
   size is in line with sibling services.

## Don't

- Don't run as root in the runtime stage
- Don't bake environment-specific config or secrets into the image
- Don't copy the fat jar as a single layer — you lose all build caching

## Related

`docker/Dockerfile` · `docker/docker-compose.yml` · `ai/skills/deployment/references/kubernetes.md`
· `docs/deployment/`
