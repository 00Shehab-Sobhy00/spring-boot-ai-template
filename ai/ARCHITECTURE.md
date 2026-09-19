> Part of the [AI agent configuration](../AGENTS.md). This file is the **authoritative source** for
> architecture/layering rules — `AGENTS.md` and `opencode.json` link here instead of repeating it.
> Edit it in one place and every tool picks up the change.
<!-- evidence-token: ARCH-KYD0VI — cite in the AI Run Report -->

# Architecture Style

- Layered Architecture

# Layers

```text
Controller  (inbound adapter)
    ↓
Service     (business / application logic)
    ↓
Repository  (persistence adapter)
```

Supporting concerns (not business layers):

- Validator — input / business validation helpers
- Mapper — conversion between DTO, domain, and entity
- Error handling — centralized mapping to HTTP errors
- Config — infrastructure wiring only
- Clients / Adapters — calls to other microservices or external systems

# Dependency Rule

- Dependencies point downward only: Controller → Service → Repository
- Lower layers must not depend on upper layers
- Cross-service or external calls go through dedicated clients/adapters, preferably via Service —
  not from Controllers directly

# Models

- **API DTO** — request / response contract with the outside world
- **Domain / service model** — internal business representation when needed
- **Persistence Entity** — database mapping only

# Mapping Rules

- Controllers talk DTOs only
- Services map between DTO ↔ domain / entity as needed
- Repositories talk Entities only
- DTOs never reach the Repository / persistence layer
- Entities are never returned raw from Controllers

# Layer Rules

- Controllers contain no business logic
- Services contain business logic
- Repository only accesses persistence
- DTOs never leak into persistence

# Allowed / Forbidden

## Allowed

- Controller → Service
- Service → Repository / Client
- Service → Mapper / Validator

## Forbidden

- Controller → Repository
- Controller → Client / Adapter (prefer via Service)
- Repository → Service / Controller
- Entity exposed as API response
- DTO persisted directly

# Microservice Boundaries

- Each service owns its data and API contract
- No direct DB access across services
- Communicate via APIs, events, or clients only
- Prefer changing one service at a time unless a cross-service change is explicitly requested

# Infrastructure Awareness

- Keep Helm / Kubernetes routing explicit and debuggable (`deployment`, `service`, `ingress`,
  `virtualservice`, `destination-rule`, `hpa`). Prefer clear values overrides per environment over
  hidden defaults — see `helm/README.md` and `docs/deployment/`.
- Consider application context crashes, proxy resets, and service-mesh behavior in local and staging
  environments when suggesting timeouts, health checks, or HTTP client settings — see
  `docs/deployment/networking.md`.

# See Also

- **Executable form of this file**: `enforcement/archunit/ArchitectureRulesTest.java` — changing
  a rule here requires changing it there in the same PR (CI enforces)
- Concrete pattern write-ups: `ai/patterns/`
- Recorded decisions and trade-offs: `/adr/`
- System diagrams: `/docs/architecture/`
