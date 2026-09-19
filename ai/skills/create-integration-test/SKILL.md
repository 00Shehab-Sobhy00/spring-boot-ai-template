---
name: create-integration-test
description: >
  Write an integration test using Testcontainers (and, where relevant, embedded Kafka/Redis) with
  correct fixture and cleanup handling. Trigger when the user asks for an integration test, an
  end-to-end test for a slice of the app, or "test this against a real database".
metadata:
  when_to_use: ["integration test", "test with a real database", "Testcontainers", "test the Kafka consumer"]
---
<!-- evidence-token: SKCREA-GD2T18 — cite in the AI Run Report -->

# Create an Integration Test

Follows `ai/TESTING.md` (Test Types, Data & Fixtures).

## Steps

1. **Decide it's actually warranted.** Per `ai/TESTING.md`, an integration test is for behavior a
   mocked unit test can't credibly prove: real query behavior, transaction boundaries under a real
   DB, Kafka produce/consume, or a Liquibase migration's actual effect. If a unit test with mocks
   would prove the same thing, prefer that instead — it's faster and more focused.
2. **Spin up the dependency with Testcontainers** — Postgres/Kafka/Redis containers matching what's
   already used elsewhere in this repo's integration tests (don't introduce a different container
   image or version than sibling tests use).
3. **Seed state explicitly** — Liquibase test data under `src/test/resources/liquibase/` for
   DB-backed tests, or an explicit fixture next to the test. Avoid relying on implicit ordering
   between tests.
4. **Clean state between tests** — each test should be independent; don't let one test's data leak
   into the next.
5. **Test the real boundary** — e.g. for a Kafka consumer test, actually publish to the (test) topic
   and assert on the observable side effect, rather than calling the listener method directly (which
   would just be a unit test in disguise).
6. **Assert both directions for cleanup/purge logic** — what was deleted, and what was correctly
   preserved.
7. **Keep it deterministic** — control clocks and randomness; don't depend on wall-clock timing or
   container startup race conditions.

## Don't

- Don't reach for a full integration test when a unit test with mocked collaborators proves the same
  thing faster
- Don't share mutable state or ordering assumptions between tests
- Don't leave a slow, flaky integration test as the *only* coverage for a piece of business logic —
  pair it with a focused unit test where possible

## Related

`ai/TESTING.md` · `ai/skills/database/references/create-entity.md` ·
`ai/skills/kafka/references/consumer.md`
