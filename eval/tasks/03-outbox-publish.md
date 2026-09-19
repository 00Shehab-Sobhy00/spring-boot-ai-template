---
id: outbox-publish
shape: publishing an event after a DB write
requires: [ai/skills/kafka/SKILL.md, ai/patterns/outbox-pattern.md]
expect_files: ['Publisher\.java$|Producer\.java$|Outbox', 'docs/messaging/kafka-topics\.md|docs/messaging/producers\.md']
expect_status: OK
forbid: ['kafkaTemplate\.send\([^)]*\);[\s\S]{0,400}@Transactional', '@Transactional[\s\S]{0,600}kafkaTemplate\.send']
---
When an order is cancelled, persist the cancellation and publish `orders.order.cancelled`. Make it
safe if the pod dies between the write and the publish.
