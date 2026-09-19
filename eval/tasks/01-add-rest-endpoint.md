---
id: add-rest-endpoint
shape: adding a REST endpoint
requires: [ai/ARCHITECTURE.md, ai/skills/create-rest-api/SKILL.md]
expect_files: ['Controller\.java$', 'Request\.java$|Response\.java$', 'ControllerTest\.java$|IT\.java$', 'docs/api/']
expect_status: OK
forbid: ['^\+.*class \w+Controller[\s\S]*Repository\b']
---
Add a `GET /orders/{id}/summary` endpoint that returns the order id, status, total amount and
item count. Follow the repo's conventions. Include tests and update whatever docs the change
touches.
