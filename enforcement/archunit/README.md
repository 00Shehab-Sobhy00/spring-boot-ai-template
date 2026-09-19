# ArchUnit — `ai/ARCHITECTURE.md` as a Failing Test

`ai/ARCHITECTURE.md` is markdown. An agent that never read it, or read it and lost it, can still
produce a Controller that calls a Repository. This folder is the mechanical version of that file:
`ArchitectureRulesTest.java` fails the build when the layering rules are violated, whichever tool or
model wrote the code.

## Install (per service, once)

1. Add the dependency to the service `pom.xml` (test scope). Use the version the platform already
   pins; do not hardcode one here.

   ```xml
   <dependency>
     <groupId>com.tngtech.archunit</groupId>
     <artifactId>archunit-junit5</artifactId>
     <scope>test</scope>
   </dependency>
   ```

2. Copy `ArchitectureRulesTest.java` to
   `src/test/java/<base-package>/architecture/ArchitectureRulesTest.java`.
3. Set `BASE_PACKAGE` and the `package` declaration. Adjust the package globs (`..controller..`,
   `..service..`, …) to the
   service's real layout — `AGENTS.md` → Workspace Map lists the typical one.
4. `mvn -q test -Dtest=ArchitectureRulesTest` — `layer_globs_all_match_classes` fails if any single
   layer glob matched zero classes. `base_package_is_not_empty` only proves *something* was
   imported; it does not detect one wrong glob, which is why the per-layer check exists.

## Keeping the two in sync

Each rule cites the `ARCHITECTURE.md` line it enforces. `ai/impact-map.yaml` (row `arch`) makes a
change to `ai/ARCHITECTURE.md` require a change under `enforcement/archunit/` in the same PR — so
the prose and the test cannot drift apart without CI noticing.

## What it cannot check

- Business-logic-in-controller (a judgement call; `review-pr` covers it)
- Cross-service DB access (different repos; covered by network policy, not ArchUnit)
- Anything about *runtime* behavior — timeouts, idempotency, correlation ids. Those stay in
  `ai/skills/resilience/`, `ai/skills/concurrency/`, `ai/skills/observability/` and their tests.
