---
id: add-consumer
shape: adding a Kafka consumer
requires: [ai/skills/kafka/SKILL.md]
expect_files: ['Consumer\.java$|Listener\.java$', 'docs/messaging/consumers\.md', 'Test\.java$']
expect_status: OK
forbid: ['catch \(Exception \w+\) \{\s*\}']
---
Consume `payments.payment.captured` events and mark the matching order as PAID. Handle poison
messages the way this repo does it. Tests and docs included.
