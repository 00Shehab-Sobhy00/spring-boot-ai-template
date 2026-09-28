---
id: add-consumer
shape: adding a Kafka consumer
requires: [ai/skills/kafka/SKILL.md, ai/skills/kafka/references/dead-letter-queue.md]
expect_files: ['Consumer\.java$|Listener\.java$', 'docs/messaging/consumers\.md', 'Test\.java$', '(?i)(dlq|deadletter|error-?handler)']
# expect_files can only prove a path changed, and a docs-only `.dlq` row satisfies that — which is
# precisely how every measured run "handled" poison messages. This asserts the handler in code.
expect_content: ['DeadLetterPublishingRecoverer|DefaultErrorHandler|CommonErrorHandler|ErrorHandlingDeserializer']
expect_status: OK
forbid: ['catch \(Exception \w+\) \{\s*\}']
---
Consume `payments.payment.captured` events and mark the matching order as PAID. Handle poison
messages the way this repo does it. Tests and docs included.
