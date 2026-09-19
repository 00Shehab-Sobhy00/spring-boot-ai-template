# Metrics Catalog

> Register every **custom** metric here. Auto-configured metrics (JVM, HTTP, pools, Kafka client)
> don't need a row. An unregistered metric becomes an orphan nobody dares delete.

<!-- TODO: replace with your real data — the rows below are a fictional example -->
| Metric | Type | Question it answers | Tags (bounded!) | Dashboard | Alert? |
| --- | --- | --- | --- | --- | --- |
| `orders.order.created` | Counter | Are orders still being created? | `channel`, `status` | Business | Yes — drop to zero |
| `payments.charge.duration` | Timer | Is the payment provider slow? | `provider`, `outcome` | Payments | Yes — p95 |
| `outbox.lag.seconds` | Gauge | Is the outbox relay stuck? | — | Platform | Yes — see ADR-003 |

## Before Adding a Row

- State the question in plain words. No question, no metric.
- Check every tag has a small fixed set of values. No ids, no paths, no exception messages.
- Confirm it isn't already exposed by auto-configuration.
