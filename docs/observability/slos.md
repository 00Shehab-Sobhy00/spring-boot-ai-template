# Service Level Objectives

> Measured from the **user's** perspective, over a stated window. Review after every incident.

<!-- TODO: replace with your real data — the rows below are a fictional example -->
| Service | SLI | Objective | Window | Measured by |
| --- | --- | --- | --- | --- |
| _example: orders-api_ | Availability (non-5xx) | 99.9% | 30 days rolling | Gateway metrics |
| _example: orders-api_ | Latency p95 | < 300ms | 30 days rolling | Server-side timer |

## Rules

- Only define an SLO you actually measure today. An unmeasured SLO is a wish.
- Alert on burn rate, not on single breaches — one slow minute isn't an incident.
- When an SLO is repeatedly missed, either fix the service or change the promise. Leaving it
  permanently red teaches everyone to ignore it.
