# Circuit Breaker

## What It Does

Stops calling a dependency that is clearly failing, so you fail fast instead of piling threads
onto a service that can't answer — and so that service gets room to recover.

Three states: **CLOSED** (normal) → **OPEN** (failing fast, not calling) → **HALF_OPEN** (letting
a few probe calls through to test recovery) → back to CLOSED or OPEN.

## Steps

1. **Set timeouts first.** Without a timeout, calls hang instead of failing, so the failure rate
   never rises, so the breaker never opens. This is the number one reason breakers "don't work".
2. **One breaker per dependency**, named after it. A shared breaker means a flaky reporting API
   opens the circuit on payments.
3. **Tune the window to real traffic.** A threshold of "50% of the last 100 calls" behaves very
   differently on an endpoint with 10 rps versus 1000 rps. Configure a minimum number of calls
   before the breaker can trip, so a slow endpoint doesn't open on 2 failures.
4. **Decide what counts as a failure.** A downstream 4xx caused by a bad request is *your* bug,
   not the downstream being down — it usually should **not** count toward opening the circuit.
   Timeouts and 5xx should.
5. **Define the fallback explicitly.** Cached value? Empty result? Typed error to the caller? This
   is a product decision (see `docs/business/business-overview.md`), and it must map to a clear
   response per `docs/api/error-catalog.md` — an EXTERNAL-origin error, not a generic 500.
6. **Emit metrics on state transitions** and alert when a breaker stays open. An open breaker
   nobody knows about is a silent outage.
7. **Test it.** Force failures in a test and assert: the breaker opens, the fallback returns, and
   it closes again after recovery.

## Don't

- Don't count client-caused 4xx as circuit failures
- Don't set the failure threshold so low that normal error noise trips it
- Don't fall back to a value that is silently wrong — a stale price is worse than an error
- Don't put a breaker on a call that has no fallback and no meaningful failure response
