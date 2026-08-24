# Day 26: ClickHouse — The Full Integration Set

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Consolidate ClickHouse's integrations with Kafka, Spark, and Redis into one
coherent picture, from ClickHouse's own side of each relationship.

## 2. Core Concept (basics → advanced)

Reviewing today's integrations from ClickHouse's specific vantage point:
- **+ Kafka**: the native `Kafka` table engine + Materialized View pattern
  (Week 2, Day 13) — ClickHouse's preferred, most efficient ingestion path
  for streaming data.
- **+ Spark**: JDBC-based batch writes (today's PySpark lesson) — a
  secondary, less-optimized path best reserved for batch workloads that
  don't fit the Kafka table engine's streaming-ingestion shape.
- **+ Redis**: not a direct integration ClickHouse initiates, but rather
  Redis sitting *in front of* ClickHouse as a hot-tier cache (today's Redis
  lesson) — ClickHouse's role here is as the backing store a cache-aside
  pattern refreshes from on a miss.

## 3. How It Really Works (Internals)

The pattern worth naming explicitly: ClickHouse has **one clearly preferred
ingestion path** (native Kafka table engine) and treats everything else
(JDBC batch writes, being fronted by a cache) as secondary, situationally
appropriate integrations — not because they're wrong, but because they serve
different specific needs (batch workloads, point-lookup access patterns) that
the primary streaming-ingestion path doesn't address. Recognizing which
integration is "the preferred path" versus "a situational fit" avoids
defaulting to whichever integration is most familiar rather than the one
best suited to the actual requirement.

## 4. Architecture & Design Pattern Spotlight

**Pattern: preferred-path vs. situational integrations — a general
principle for any system with multiple integration options: know which one
is the primary, most-optimized path, and use the others deliberately for
their specific fit, not out of habit.**

## 5. Hands-On Lab

Review your own Day 25 capstone design's ClickHouse integrations explicitly:
is streaming ingestion using the native Kafka table engine (the preferred
path)? Are any JDBC/batch writes genuinely batch-shaped workloads, or could
they be better served by the native path? Is Redis correctly positioned as a
front-facing cache rather than something ClickHouse depends on directly?

## 6. Real-World Product Comparison

This finalizes your own real architecture's ClickHouse integration design.

## 7. Common Production Pitfalls

- Defaulting to JDBC batch writes for genuinely streaming workloads that
  would be better served by the native Kafka table engine.
- Not explicitly verifying which integration pattern is actually in use for
  each real data flow in your target architecture.

## 8. Review Questions
1. What's ClickHouse's preferred ingestion path, and why?
2. When is a JDBC/batch write genuinely the right choice instead?
3. What's Redis's role in this integration set, precisely?
4. Does your own Day 25 design use the preferred path where appropriate?

## 9. Proficiency Checkpoint
If you've verified your own design uses the right integration pattern for
each data flow, you're at Level 4.

## Next
Day 27 is your final interview-readiness and mock-review day.
