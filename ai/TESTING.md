> Part of the [AI agent configuration](../AGENTS.md). Authoritative source for testing policy.
<!-- evidence-token: TEST-6XZY5P — cite in the AI Run Report -->

# When Implementing New Code

Always:

- Write unit tests for new business logic
- Cover the happy path and at least the important failure / edge paths

# When Changing Business Logic

- Run related tests first
- Update or add tests for the new behavior before considering the change done
- Never remove tests without explanation

# What to Test

Prioritize:

- Service-layer business rules
- Validation and error mapping
- Transaction boundaries
- Inter-service / client failure paths (timeouts, 4xx/5xx from downstream)
- Persistence behavior that encodes real rules (queries, purge/cleanup, constraints)

Do not over-test:

- Framework wiring with no business value
- Trivial getters/setters
- Pure pass-through code with no logic

# Test Types

- **Unit tests** — default for services, validators, mappers, pure logic (mock collaborators)
- **Repository / persistence tests** — when query or data behavior matters
- **API / controller tests** — when request validation, status codes, or error responses matter
- **Integration tests** — when a real Spring context, database, or broker matters; see
  `ai/skills/create-integration-test/`
- Prefer the smallest test that proves the behavior

# Style

- One behavior per test; name tests by behavior, not by method only
- Arrange → Act → Assert
- Keep tests deterministic (no time/order flakiness; control clocks and randomness)
- Prefer focused assertions on the outcome that matters
- Do not share mutable state between tests

# Doubles & Boundaries

- Mock external systems and other microservices
- Do not mock the class under test
- Prefer fakes/stubs for stable simple collaborators when mocks become noisy
- Keep test data anonymized / synthetic — no real PII or secrets

# Data & Fixtures

- Prefer explicit fixtures close to the test
- For DB-backed tests, use controlled seed data and clean state between tests
- Cleanup / purge tests must assert both what was deleted and what must remain

# When a Test Fails

- Fix the code or update the test to match intentional new behavior
- Do not disable, skip, or delete failing tests to "make CI green" without a clear reason documented
  in the change

# Concurrency Tests

Required whenever multiple requests, replicas, or a scheduled job can touch the same state.
A sequential test proves nothing about thread safety.

- Use a `CountDownLatch` to release N threads simultaneously, then assert exactly one winner
- Test the scheduled-job case: would this be correct if it ran on every replica at once?
- See `ai/skills/concurrency/`

# Quality Gates

These should run in your CI pipeline and are part of "done":

- **Coverage** — new business logic is covered; the build fails below the configured threshold.
  Coverage is a floor, not a goal: 100% coverage of trivial code proves nothing.
- **Architecture** — `enforcement/archunit/ArchitectureRulesTest.java` passes in every service
- **Static analysis** — no new blocker or critical findings
- **Dependency scanning** — no new high/critical CVEs introduced by added dependencies

# Scope

- Run the smallest relevant test set while iterating
- Run the full module test suite before finishing a business-logic change

# See Also

- Recipe for writing a new integration test: `ai/skills/create-integration-test/`
- Review checklist that includes test coverage: `ai/REVIEW.md`
