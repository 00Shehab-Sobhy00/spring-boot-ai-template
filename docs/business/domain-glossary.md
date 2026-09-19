# Domain Glossary (Ubiquitous Language)

> One definition per term. Code, APIs, events, and docs use **these exact words** — an "Order" in
> the glossary is `Order` in code, never sometimes "Purchase". AI agents: treat this as binding
> vocabulary; when you meet an undefined term, propose adding it here.

<!-- TODO: replace with your real data — the rows below are a fictional example -->
| Term | Definition | Owned by (service) | Notes / easily confused with |
| --- | --- | --- | --- |
| _Order_ | _A customer's confirmed intent to buy, from placement until fulfillment or cancellation_ | orders-service | _Not the same as a Cart (pre-confirmation)_ |
| _Payment_ | _A single charge attempt against an Order_ | payments-service | _An Order can have several Payments (retries)_ |
| | | | |
