# Day 26: Redis — Integrations: Kafka Invalidation Events & Hot-Tier Caching

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Sketch Redis as a hot-tier cache in front of ClickHouse for point lookups,
complementing today's Kafka-lesson invalidation-event design.

## 2. Core Concept (basics → advanced)

Beyond today's Kafka-lesson invalidation pattern, Redis's other major
integration role in your target architecture is as a **hot-tier cache in
front of ClickHouse specifically for point-lookup-shaped queries** — Day 24's
"when NOT to use ClickHouse" lesson identified point lookups as a poor fit for
ClickHouse's architecture; rather than forcing ClickHouse to serve those
queries directly, a Redis layer in front absorbs exactly that access pattern,
letting ClickHouse focus on what it's actually built for (large scans and
aggregations, Day 22).

```
Point-lookup query (e.g., "get this one org's current summary stats")
     │
     ▼
Redis (cache-aside, Week 2 Day 11) — FAST path for point lookups
     │ on miss
     ▼
ClickHouse — computes/refreshes the value (via a query or a
             Refreshable MV, Week 1 Day 6), populates Redis cache
```

## 3. How It Really Works (Internals)

This is a direct, concrete application of the CQRS read-model idea (Week 2,
Day 10; Week 4, Day 22) — Redis serves as a purpose-built read-model layer
specifically for the point-lookup access pattern, while ClickHouse serves the
large-scan/aggregation access pattern, each engine handling the query shape
it's actually built for rather than forcing one engine to serve both shapes
adequately.

## 4. Architecture & Design Pattern Spotlight

**Pattern: hot-tier cache absorbing an access pattern the backing store isn't
optimized for — the same principle as Week 2 Day 10's hot/warm/cold tiering,
applied here to query *shape* (point lookup vs. scan) rather than data
*age*.**

## 5. Hands-On Lab

Identify, in your own Day 25 capstone design, any dashboard or API query that
is fundamentally point-lookup-shaped (fetching one specific, small,
frequently-requested result) rather than scan/aggregation-shaped. Design a
Redis hot-tier cache layer for it specifically, using cache-aside (Week 2,
Day 11) with an explicit TTL and invalidation trigger tied to the Kafka event
pattern from today's Kafka lesson.

## 6. Real-World Product Comparison

This directly extends and completes your Day 25 capstone design's caching
architecture.

## 7. Common Production Pitfalls

- Forcing ClickHouse to serve point-lookup-shaped queries directly when a
  Redis hot-tier cache would serve them far more efficiently.
- Building this cache layer without the event-driven invalidation design
  from today's Kafka lesson, reintroducing cache-bypass risk in the new
  architecture.

## 8. Review Questions
1. What access-pattern mismatch does this Redis hot-tier layer specifically
   address?
2. How does this relate to the CQRS read-model pattern?
3. Which of your own real dashboard queries is point-lookup-shaped enough to
   benefit from this?
4. How does this integrate with today's Kafka-based invalidation design?

## 9. Proficiency Checkpoint
If you've designed a complete, invalidation-integrated hot-tier cache for a
real point-lookup query, you're at Level 4.

## Next
Day 27 is your final interview-readiness and mock-review day.
