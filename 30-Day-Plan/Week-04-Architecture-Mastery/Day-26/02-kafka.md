# Day 26: Kafka — Integrations: Flink, ClickHouse, Redis

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Sketch three concrete Kafka integration points: exactly-once with Flink, the
ClickHouse table engine, and Redis cache-invalidation events.

## 2. Core Concept (basics → advanced)

- **Kafka + Flink**: exactly-once via the checkpoint-tied two-phase-commit
  sink (Week 2, Day 9) — this is the tightest, most rigorously correct
  integration studied this month, worth using as the reference point for
  what "properly integrated, exactly-once" actually looks like.
- **Kafka + ClickHouse**: the native Kafka table engine + Materialized View
  pattern (Week 2, Day 13) — direct streaming ingestion, no separate consumer
  application needed.
- **Kafka + Redis**: using Kafka events to trigger cache invalidation
  (Week 1, Day 6; Week 2, Day 11) — a write to the system of record emits an
  event, a consumer invalidates the corresponding Redis cache entry, keeping
  cache and source-of-truth in sync via the event stream rather than direct
  application-code coupling.

## 3. How It Really Works (Internals)

The Kafka+Redis cache-invalidation pattern is worth connecting explicitly
back to your own MDO portal cache-bypass investigation (Week 1, Day 6; Day 25):
if invalidation currently happens via direct application-code calls (rather
than an event-driven mechanism), that's a real, concrete architectural gap —
any write path that doesn't correctly call the invalidation logic produces
exactly the silent staleness bug this month's caching lessons have covered
repeatedly. An event-driven invalidation pattern (Kafka event → invalidation
consumer) centralizes this logic in one place, structurally reducing the risk
of a missed invalidation call somewhere in application code.

## 4. Architecture & Design Pattern Spotlight

**Pattern: event-driven invalidation as a structural fix for the cache-bypass
class of bug — moving invalidation logic out of scattered application code
and into one centralized event-consumer**, directly relevant to Day 25's
Redis-lesson fix design.

## 5. Hands-On Lab

Sketch the Kafka+Redis cache-invalidation design for your own MDO portal fix
(from Day 25): what event triggers invalidation, what topic carries it, and
what consumer performs the actual Redis invalidation? Compare this against
your current (likely application-code-coupled) invalidation mechanism, and
assess whether the event-driven version would have prevented the original
bypass bug.

## 6. Real-World Product Comparison

This directly extends Day 25's real fix design with a specific, structural
implementation mechanism.

## 7. Common Production Pitfalls

- Relying on scattered, application-code-coupled invalidation calls instead
  of a centralized, event-driven mechanism — the root structural cause of
  many cache-bypass bugs.
- Not testing the Kafka+Flink exactly-once integration's actual behavior
  under a forced restart (Week 2, Day 9's lab) before trusting it in
  production.

## 8. Review Questions
1. What makes the Kafka+Flink integration the "reference" for correct
   exactly-once behavior?
2. How does event-driven invalidation structurally reduce cache-bypass risk?
3. Would this pattern have prevented your own MDO portal's original bypass
   bug?
4. What's required to convert your current invalidation mechanism to this
   pattern?

## 9. Proficiency Checkpoint
If you've designed a real, event-driven invalidation mechanism for your own
cache-bypass fix, you're at Level 4.

## Next
Day 27 is your final interview-readiness and mock-review day.
