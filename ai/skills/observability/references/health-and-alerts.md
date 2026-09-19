# Health Probes, Alerts & SLOs

## Health Probes

Liveness and readiness answer different questions. Wiring both to the same check causes
restart storms.

| Probe | Question | Should depend on downstream services? |
| --- | --- | --- |
| **Liveness** | Is this process broken beyond recovery? Restart it. | **No.** A downstream outage must not restart your pods. |
| **Readiness** | Can this instance serve traffic right now? | Yes, for dependencies it genuinely cannot serve without. |
| **Startup** | Has it finished booting? | N/A — it exists to stop liveness killing a slow start. |

Steps:

1. Expose health groups so liveness and readiness resolve different indicator sets.
2. Add a custom indicator only for dependencies the service genuinely cannot serve without.
3. Set the startup probe's budget from a **cold** start, including mesh sidecar warm-up —
   see `docs/deployment/networking.md`.
4. Expose actuator on a separate management port, and never route it through the public ingress.

## Alerts

**Alert on symptoms the user feels.** Error rate, latency, and business-flow stalls. Not CPU, not
memory, not thread count — those are dashboard material, not pager material.

For each alert define: the condition, the window, the severity, and **the runbook entry**
(`docs/deployment/runbook.md`). An alert with no runbook is noise, and noise trains people to
ignore the pager.

Baseline alert set for a service here:

- Error rate above threshold (sustained, not a single spike)
- p95/p99 latency above threshold
- Consumer lag growing (see `docs/messaging/consumers.md`)
- DLQ depth above zero (see `docs/messaging/dlq.md`)
- Outbox lag — the oldest undispatched row's age (see `ai/patterns/outbox-pattern.md`)
- Pod restart rate

## SLOs

An SLO is a promise with a number. Define at minimum: availability and latency, measured from the
**user's** perspective, over a stated window. Write them in `docs/observability/slos.md` and
review them after incidents — an SLO nobody revisits is decoration.

## Don't

- Don't make liveness depend on the database or a downstream service
- Don't alert on a cause when you can alert on the symptom
- Don't set an SLO you have no measurement for
- Don't expose actuator publicly
