> Reference pattern. Applies to any change too risky to ship all at once.
<!-- evidence-token: PATFEAT-RXLY6T — cite in the AI Run Report -->

# Pattern: Feature Flags & Phased Rollout

## Intent

Separate **deploying** code from **enabling** behavior, so a risky change can be turned on for a
slice of traffic and turned off in seconds without a redeploy.

## When to Use

- Changing a hot path where the blast radius of being wrong is large
- Cross-service changes that must be coordinated (enable producer, verify, then enable consumer)
- Anything where "roll back the deploy" would take longer than the incident can tolerate
- Migrations that need old and new paths to run side by side

## When Not to Use

- Small, easily reverted changes — a flag has real cost (branches, tests, cleanup debt)
- As a substitute for a proper migration plan
- Long-lived configuration (that's config, not a flag)

## The Phased Rollout

1. **Deploy dark** — code ships with the flag off. Zero behavior change. Confirms the deploy
   itself is safe, separately from the feature.
2. **Enable for a sliver** — internal users, one tenant, or a small percentage. Watch the metrics
   that would show harm (`ai/skills/observability/`).
3. **Ramp** — widen in steps, with a defined bake time at each. Resist the urge to jump to 100%
   because the first step looked fine.
4. **Full on** — flag still present, still flippable.
5. **Remove the flag.** This step is the one teams skip. A flag left in place forever becomes
   permanent branching complexity that nobody dares delete.

## Rules

- **Default off.** A flag that defaults on isn't protecting anything.
- **Both branches must work at all times.** If the old path has silently rotted, the flag is
  decoration — you can't actually roll back.
- **Flag state is observable.** Log and tag metrics with which branch ran, or you can't attribute
  a metric change to the rollout.
- **Every flag has an owner and a removal date.** Record both in `ai/PROJECT_MEMORY.md` under
  Active Migrations.
- **Test both branches.** Two test paths, not one. The off-path test is the one that saves you.
- **Kill switch beats rollback.** For anything on a hot path, being able to disable in seconds is
  worth more than a fast pipeline.

## Pitfalls

- Flags that outlive their purpose and accumulate into unreadable branching
- Flag checks scattered through the codebase instead of evaluated once at a clear boundary
- Enabling for 100% immediately "because staging was fine" — staging traffic is not production
  traffic
- Coordinated cross-service flags flipped in the wrong order (enable the consumer before the
  producer, not after)

## Related

- `ai/skills/observability/` — you cannot run a phased rollout you can't measure
- `ai/PROJECT_MEMORY.md` — Active Migrations
- `/adr/` — if the flag guards a significant, hard-to-reverse decision
