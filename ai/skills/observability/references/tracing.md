# Distributed Tracing & Correlation

The point: follow **one request** across services, queues, and threads.

## Steps

1. **Use the platform's tracing abstraction, not a vendor SDK directly.** Micrometer Tracing with
   an OpenTelemetry backend is the current default in the Spring ecosystem — instrument against
   the abstraction so the backend stays swappable.
2. **Confirm propagation over HTTP.** Auto-configuration handles trace headers on
   `RestClient`/`WebClient`/Feign when the tracing starter is present. Verify it actually works
   end to end before trusting it — a missing starter on one service silently breaks the chain.
3. **Propagate over Kafka explicitly.** The trace context travels in message *headers*. Producers
   must inject it, consumers must extract it. This is the most commonly broken hop, because it
   fails silently: each service traces fine on its own, and the chain just... stops.
4. **Handle async boundaries.** `@Async`, `CompletableFuture`, `ExecutorService`, and scheduled
   tasks run on a different thread — **MDC and trace context do not follow automatically.**
   Configure context propagation on the executor, or wrap the task. If your correlation ids
   mysteriously vanish for background work, this is why.
5. **Sample deliberately.** 100% sampling in production is usually too expensive; sample a
   percentage but always trace errors. Record the sampling decision in
   `ai/PROJECT_MEMORY.md` so nobody debugs a "missing" trace that was simply not sampled.
6. **Add spans for meaningful business operations only** — a whole use case, an external call, a
   slow computation. Not every method.
7. **Put the trace/correlation id in every log line and every error response.** That id is what
   lets support connect "customer complained" to "here is the exact request".

## Rolling It Out on an Existing Service

Adding correlation to a live system is a phased change, not a big-bang one:

1. Generate/accept the id at the edge, log it, but don't yet require it downstream
2. Propagate it outward (HTTP, then Kafka), still tolerating its absence
3. Only once coverage is confirmed, treat a missing id as an anomaly worth alerting on

Guard the rollout behind a flag — see `ai/patterns/feature-flags.md`.

## Don't

- Don't trust propagation because it "should" work — verify with a real cross-service request
- Don't put PII in span attributes; they're stored and queryable like logs
- Don't generate a new correlation id when one already arrived on the request — join the trace
- Don't rely on trace context surviving a thread hop without configuring it
