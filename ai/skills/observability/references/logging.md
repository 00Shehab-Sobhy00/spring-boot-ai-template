# Structured Logging

Logs are only useful if you can query them. Free text can't be queried at scale.

## Steps

1. **Log as JSON in every deployed environment.** Human-readable format is fine locally; anything
   that ships to a log aggregator should be structured, so fields are queryable rather than
   regex-scraped.
2. **Put context in MDC, not in the message string.** `MDC.put("orderId", id)` then a plain
   message — every line in that scope carries the field automatically, and it's filterable.
   String-concatenated context is invisible to the aggregator.
3. **Always include:** trace/correlation id, service name, environment, and the domain id
   relevant to the operation.
4. **Clear MDC when the scope ends.** Thread pools reuse threads — a leftover MDC value attaches
   itself to an unrelated later request and sends you chasing a ghost.
5. **Use levels with intent:**
   - `ERROR` — someone may need to act; always with enough context to act on
   - `WARN` — recovered, but a human should know it happened
   - `INFO` — meaningful state transitions and business events
   - `DEBUG` — off in production; developer detail
6. **Log state transitions**, not every method entry. "order 123 PENDING → PAID" is worth a line;
   "entering method X" is not.
7. **Never log:** passwords, tokens, full `Authorization` headers, card data, or PII. Log an id
   that lets an authorized person look the record up instead. This applies to exception messages
   from downstream systems too — they often echo the request back.

## Don't

- Don't log a full request/response payload by default — sample it, or log size and key fields
- Don't log an exception and then rethrow it (the caller logs it again — duplicate noise)
- Don't use `System.out` anywhere
- Don't log inside a tight loop or a hot path without a rate limit
