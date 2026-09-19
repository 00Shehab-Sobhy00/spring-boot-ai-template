# Create a JPA Entity

Follows `ai/BACKEND_RULES.md` (Persistence section) and `ai/ARCHITECTURE.md` (Entities never leak
past the Repository layer).

## Steps

1. **Entity class** — under the module's existing entity package. Explicit `@Id` strategy consistent
   with sibling entities in this service (don't introduce a second ID strategy). Favor immutability
   where the ORM allows it; avoid exposing setters that would let other layers mutate persisted
   state outside a transaction.
2. **Liquibase migration** — add a **new** changelog file under
   `src/main/resources/liquibase/changelog/` and register it in `master.xml`. Never edit a
   historical changelog, even for a typo. Include the down/rollback if this project's changelogs do
   so consistently.
3. **Indices & constraints** — add indexes for columns you know will be queried/filtered on; add FK
   constraints for real relationships. Note anything non-obvious (a partial index, a
   deliberately-missing FK) in `ai/PROJECT_MEMORY.md`.
4. **Repository** — a Spring Data interface in the persistence package. Custom queries live here,
   not in the service or controller.
5. **Mapper** — entity ↔ domain/DTO, matching the existing mapping approach in the module. The
   entity must never be returned from a controller.
6. **Test data / fixtures** — add Liquibase test data under `src/test/resources/liquibase/` if this
   project seeds test data that way, or a focused fixture next to the test.
7. **Tests** — a repository/persistence test if there's meaningful query behavior; otherwise cover
   the entity through the service test that uses it.

## Don't

- Don't put business logic in the entity or the repository
- Don't touch a historical migration — always a new file
- Don't skip the index just because it "probably won't matter" for a column you already know will be
  filtered on

## Related

`ai/BACKEND_RULES.md` (Persistence) · `docs/database/migrations.md` ·
`docs/database/schema-conventions.md` · `ai/skills/database/references/optimize-query.md` ·
`ai/skills/create-integration-test/`
