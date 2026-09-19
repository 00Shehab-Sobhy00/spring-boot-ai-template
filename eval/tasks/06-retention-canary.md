---
id: retention-canary
shape: long task that must still cite early rules
requires: [ai/ARCHITECTURE.md, ai/BACKEND_RULES.md, ai/TESTING.md, ai/skills/database/SKILL.md, ai/skills/create-rest-api/SKILL.md, ai/skills/create-integration-test/SKILL.md]
expect_files: ['liquibase/', 'Entity\.java$|entity/', 'Controller\.java$', 'IT\.java$|Test\.java$']
expect_status: OK
---
Add a `refunds` feature end to end: a `refund` table (Liquibase), entity + repository, a
`POST /orders/{id}/refunds` endpoint with validation, service logic, integration test with
Testcontainers, and all doc updates. Run it through the deliver-feature skill and keep the
checkpoint updated. This task is deliberately long — if you lose track of a rule you read at the
start, say so.
