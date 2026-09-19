# Metrics

Micrometer is the instrumentation API; the backend (Prometheus, OTLP, whatever the platform runs)
is a config concern, not a code concern. Instrument once against Micrometer.

## Steps

1. **Decide the question first.** Write down the question this metric answers ("how many orders
   fail payment per minute?"). If you can't state it, don't add the metric.
2. **Pick the right instrument:**
   - `Counter` — monotonically increasing count (orders created, errors, retries)
   - `Timer` — duration + count together (endpoint latency, downstream call time)
   - `Gauge` — current value that goes up and down (queue depth, active sessions, cache size)
   - `DistributionSummary` — distribution of a non-time value (payload size, batch size)
3. **Name it consistently:** `<domain>.<entity>.<action>` in lowercase dot notation
   (`orders.order.created`, `payments.charge.duration`). Match the naming already in the service.
4. **Tag deliberately.** Small, fixed sets only: `status`, `error_type`, `region`, `tier`.
   **Never** `userId`, `orderId`, or a raw path. Every distinct tag combination is a separate
   time series — cardinality multiplies.
5. **Instrument the boundaries you care about:** inbound endpoints, outbound client calls, Kafka
   consume/produce, cache hit/miss, and the business events from
   `docs/business/business-overview.md`.
6. **Free ones already exist.** HTTP server/client metrics, JVM, connection pools, and Kafka
   client metrics come from auto-configuration. Don't hand-roll what Actuator already exposes —
   check first.
7. **Register the metric in `docs/observability/metrics-catalog.md`** with its question, tags,
   and which dashboard uses it. An unregistered metric becomes an orphan nobody dares delete.

## The Cardinality Trap

```java
// WRONG — one time series per order, forever
Counter.builder("orders.processed").tag("orderId", order.getId()).register(registry);

// RIGHT — bounded dimensions
Counter.builder("orders.processed")
       .tag("status", order.getStatus().name())     // handful of values
       .tag("channel", order.getChannel())          // handful of values
       .register(registry);
```

If you need to find *one specific* order's path, that's a trace, not a metric.

## Don't

- Don't add metrics "for completeness" — each one costs storage forever
- Don't use a Gauge for something that only increases (that's a Counter)
- Don't compute a rate in code — the metrics backend does that; record the raw counter
- Don't tag by exception message (unbounded); tag by exception class or an error code
