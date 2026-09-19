> Reference pattern. Governing rule from `ai/ARCHITECTURE.md` / `AGENTS.md`: use design patterns
> **only when they clarify boundaries — not for ceremony.** This file lists the handful actually
> worth reaching for in a Spring codebase, and the traps.
<!-- evidence-token: PATDESI-JTNPRZ — cite in the AI Run Report -->

# Pattern: Common Design Patterns (the useful subset)

## First, the free ones — Spring already gives you these

Don't hand-implement what the framework provides:

| Pattern | You get it from | Notes |
| --- | --- | --- |
| Singleton | Spring beans (default scope) | Never write a `getInstance()` singleton in a Spring app — and because beans are shared, keep them **stateless** per `ai/REVIEW.md` (Thread Safety) |
| Dependency Injection / IoC | Spring container | Constructor injection only (`ai/BACKEND_RULES.md`) |
| Proxy / Decorator (infra) | `@Transactional`, `@Cacheable`, AOP | Know it's there: self-invocation bypasses the proxy — calling a `@Transactional` method from inside the same class silently skips the transaction |
| Template Method (infra) | `JdbcTemplate`, `KafkaTemplate`, etc. | Use the template; don't wrap it in another abstraction with no added value |
| Observer (infra) | Spring `ApplicationEvent` / Kafka | In-process events for same-service decoupling; Kafka for cross-service (`async-events.md`) |

## The ones worth writing by hand — with the trigger that justifies each

**Strategy** — *trigger: a growing `if/else` or `switch` on a "type" that selects a behavior.* One
interface, one implementation per variant, selected via a `Map<Type, Strategy>` injected by Spring
(inject `List<Strategy>` and index by a `type()` method). Adding a variant = adding a class, not
editing a switch. Don't use it for two stable branches — an `if` is fine.

**Factory (method)** — *trigger: constructing an object requires logic/choices the caller shouldn't
own.* Usually a small `@Component` with a `create(...)` method. You rarely need Abstract Factory in
a Spring service — the DI container *is* the abstract factory.

**Builder** — *trigger: an object with several optional fields, or test-data setup readability.*
Records + a compact builder (or Lombok `@Builder` if the repo already uses Lombok — check first, per
"no second parallel style"). Especially valuable for test fixtures.

**Adapter** — *trigger: an external contract (Feign client, SDK, legacy API) whose shape shouldn't
leak inward.* This is exactly the `clients/adapters` layer in `ai/ARCHITECTURE.md`: wrap the
external DTOs/exceptions at the boundary and expose your own domain-shaped interface. The rest of
the service must not import the vendor's types.

**Chain of Responsibility** — *trigger: an ordered pipeline of independent checks/steps (validation
pipeline, message-processing steps).* An ordered `List<Handler>` injected by Spring (`@Order`).
Prefer it over one 200-line validate method — but only once there are 3+ genuinely independent
steps.

**Template Method (yours)** — *trigger: several workflows share a fixed skeleton with small varying
steps* (e.g. all Kafka consumers do: dedupe → validate → process → ack). An abstract base or, often
better in modern Java, a composed strategy — prefer composition when the variation points are few.

**Specification / Predicate composition** — *trigger: combinable query filters* (Spring Data
`Specification`). Use when filters genuinely combine at runtime; skip for one fixed query.

## The traps (patterns that mostly cost you)

- **Ceremony layering**: interfaces with exactly one implementation "for testability" — Mockito
  mocks classes; add the interface when a second implementation or a real boundary exists.
- **God-object "Manager/Helper/Util"**: not a pattern, a landfill. Split by responsibility.
- **Observer for critical flow**: in-process events that *must* happen (billing!) hidden behind an
  event bus make the flow invisible and failure handling vague — critical steps stay explicit calls;
  events are for genuinely optional reactions.
- **Premature Strategy/Factory**: two variants, both stable → an `if` statement is the superior
  design.
- **Duplicate pattern next to an existing one**: before adding *your* strategy registry, check
  whether the module already has one — `ai/REVIEW.md` (Duplicate Logic).

## How to decide (30-second test)

1. Can I name the concrete trigger from the lists above? If not — no pattern.
2. Does the module already solve this shape somewhere? If yes — mirror it.
3. Will the pattern remove a real change-hotspot (a switch everyone edits), or just add indirection?
   Only the first justifies it.

## Related

`ai/ARCHITECTURE.md` (patterns clarify boundaries, not ceremony) · `ai/REVIEW.md` (Complexity,
Duplicate Logic) · `ai/patterns/` siblings for the architectural patterns (outbox, saga,
cache-aside, retry)
