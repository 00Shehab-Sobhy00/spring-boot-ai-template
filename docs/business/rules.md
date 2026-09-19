# Business Rules Register

<!-- TODO: replace the example rows with your real rules -->

The rules that make the code *correct for this business*, not just correct. Each rule has an id,
and the id is the link between this file and the code: the condition that implements a rule and
the test that proves it both carry a `// BR-nnn` comment. `scripts/check-business-rules.sh`
reports ids referenced in code but missing here, and ids here with no code reference.

Why ids and not prose: business docs can't be generated from code, but the *link* between them
can be checked. That is what keeps this file honest.

| Id | Rule | Source | Owner | Since | Enforced in |
| --- | --- | --- | --- | --- | --- |
| BR-001 | *Orders may be cancelled free within 15 minutes of placement; after that the cancellation fee in `fees.cancellation` applies* | *Product decision 2024-02* | *Orders PO* | *2024-02-10* | `orders-service` `CancellationPolicy` |
| BR-002 | *Refunds above 500 (any currency, at booking-time rate) require manual approval* | *Finance policy* | *Finance* | *2024-03-01* | `payments-service` `RefundService` |
| BR-003 | *Partner X responses must be acknowledged within 2 s (contractual SLA)* | *Contract §4.2* | *Partnerships* | *2024-01-20* | `partner-gateway` timeout config + alert |

## Conventions

- Ids are sequential and never reused. A retired rule keeps its row with
  `Status: retired (YYYY-MM-DD)` appended to the Rule column — the id may still appear in old
  commits.
- One rule per row. If a "rule" needs a paragraph, it's a section in `business-overview.md` or a
  per-domain doc, and the row here links to it.
- `Source` is the thing a lawyer or PO would point at: contract, regulation, product decision +
  date. "It's always been that way" is not a source — record it as such and flag it.
- In code, put the comment on the **condition**, not the class:

  ```java
  // BR-001: free cancellation window
  if (Duration.between(order.placedAt(), now).compareTo(policy.freeWindow()) <= 0) { ... }
  ```

  and on the test that proves it. A rule with no test is a rule the next refactor will delete.
- The agent must **not** invent rows. When it finds a domain condition with no `BR` id, it asks (see
  `ai/skills/sync-docs/SKILL.md` step 4).
