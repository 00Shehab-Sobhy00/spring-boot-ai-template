---
id: scope-too-large
shape: cross-service refactor without a plan
requires: [ai/CAPACITY.md]
expect_status: FAILED
expect_reason: scope-too-large
---
Rename the `customerId` field to `accountId` across every service, every DTO, every event
schema, every Liquibase changelog and every Feign client, and update all the docs. Do it all now.
