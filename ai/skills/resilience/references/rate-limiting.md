# Rate Limiting

Two directions, often confused:

- **Inbound** — protect *this* service from callers (abuse, runaway clients, thundering herds)
- **Outbound** — respect a downstream's quota so you don't get throttled or banned

## Steps

1. **Decide the scope.** Per caller (API key, tenant, user)? Per endpoint? Global? Per-caller is
   usually right — a global limit means one heavy client degrades everyone.
2. **Pick where it lives.** Gateway/mesh handles coarse protection cheaply. In-app limiting is
   for business rules ("free tier gets N calls per day") that the gateway can't know about.
3. **Distributed means shared state.** With multiple replicas, an in-memory limiter gives each pod
   its own quota — the effective limit becomes N × the intended one. Use a shared counter
   (Redis/Redisson is already in this stack — see `ai/skills/redis-cache/`) when the limit must
   be cluster-wide.
4. **Respond correctly.** HTTP `429` with a `Retry-After` header. Register the error code in
   `docs/api/error-catalog.md`. A 429 without `Retry-After` invites an immediate retry storm.
5. **For outbound limits**, throttle proactively at the client rather than reacting to the
   downstream's 429s — being rate-limited is already a failure.
6. **Instrument rejections.** A rising rejection rate is either an attack, a misconfigured client,
   or a limit that's now too low for legitimate growth. You can't tell which without the metric.

## Don't

- Don't apply an in-memory limiter across replicas and assume it's cluster-wide
- Don't return 429 without `Retry-After`
- Don't rate-limit health/probe endpoints
- Don't set limits from a guess — measure real traffic first, then set a headroom multiple
