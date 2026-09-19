---
name: observability
description: >
  Instrument a service so an on-call engineer who didn't write it can tell what it's doing —
  metrics, distributed tracing, structured logs, health probes, and alerts. Use when adding
  monitoring, debugging a production issue with no visibility, or preparing a service to ship.
metadata:
  when_to_use: ["add metrics", "instrument this", "distributed tracing", "correlation id", "we can't see what's happening in prod", "add an alert", "actuator", "SLO"]
---
<!-- evidence-token: SKOBSE-60HEGU — cite in the AI Run Report -->

# Observability

The question this skill exists to answer: **can someone who did not write this service tell what
it is doing, at 3am, without attaching a debugger?**

| You want to... | Read |
| --- | --- |
| Add metrics (counters, timers, gauges) | `references/metrics.md` |
| Propagate trace/correlation ids across services and Kafka | `references/tracing.md` |
| Make logs searchable and correlated | `references/logging.md` |
| Configure health probes, or define an alert/SLO | `references/health-and-alerts.md` |

## The Three Pillars, and What Each Is For

Instrument for **questions you will actually ask during an incident** — not for coverage.

| Pillar | Answers | Cost of overdoing it |
| --- | --- | --- |
| **Metrics** | "How many? How fast? How often failing?" — aggregate, cheap, always on | High-cardinality tags explode storage and cost |
| **Traces** | "Where did *this one* request spend its time, across services?" | Tracing every method is noise; sample and trace meaningful operations |
| **Logs** | "What exactly happened in this specific case?" | Volume cost, and PII risk |

A useful rule: **metrics tell you something is wrong, traces tell you where, logs tell you why.**
If you can't answer all three for a new feature, it isn't finished.

## Non-Negotiables

**1. Every log line carries the correlation/trace id.**
A log you can't tie to a request is a log you can't use. Propagate the id through HTTP calls,
Kafka headers, and async boundaries — see `references/tracing.md`, and note that `@Async` and
thread pools **lose MDC context** unless you configure propagation explicitly. This is the single
most common way correlation silently breaks.

**2. Never put unbounded values in metric tags.**
Tag by things with a small fixed set of values — status, region, tier, error type. Never by
userId, orderId, request path with ids in it, or anything else unbounded. A high-cardinality tag
is how a metrics bill becomes a budget incident.

**3. Never log secrets, tokens, full auth headers, or PII.**
Same rule as `ai/BACKEND_RULES.md` (Logging). Applies to trace attributes and metric tags too.

**4. Alert on user-facing symptoms, not internal causes.**
"Error rate above X" and "p95 latency above Y" wake someone for a real reason. "CPU above 80%"
usually doesn't. Every alert needs a runbook entry — see `docs/deployment/runbook.md`.

**5. Business metrics matter as much as technical ones.**
Requests-per-second doesn't tell you orders stopped being created. Instrument the events the
business would notice — see `docs/business/business-overview.md` for which those are.

**6. Readiness and liveness are different questions.**
Liveness: should this pod be restarted? Readiness: should it receive traffic *right now*? Wiring
both to the same endpoint means a slow dependency triggers restart loops.

## Don't

- Don't add a metric without knowing which question it answers or which dashboard shows it
- Don't tag metrics with ids — that's what traces are for
- Don't trace every method; trace meaningful business operations
- Don't wire liveness to a check that depends on a downstream service
- Don't ship an alert with no runbook — an alert nobody knows how to action is noise

## Related

`ai/BACKEND_RULES.md` (Logging) · `docs/observability/` · `docs/deployment/runbook.md` ·
`ai/skills/deployment/references/kubernetes.md` (probe configuration) ·
`ai/prompts/performance-review.md`
