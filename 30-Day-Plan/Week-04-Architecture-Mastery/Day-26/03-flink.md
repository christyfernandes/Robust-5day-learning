# Day 26: Flink — Integrations: ClickHouse, Redis, Elasticsearch Sinks

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Sketch three Flink sink integrations, with particular attention to the
exactly-once caveat when sinking to ClickHouse specifically.

## 2. Core Concept (basics → advanced)

- **Flink + ClickHouse sink**: this integration carries a genuine caveat
  worth stating precisely — Week 2, Day 9's two-phase-commit exactly-once
  sink pattern depends on the target system supporting transactional
  commit/abort semantics (as Kafka's transactional producer does). ClickHouse
  is **not transactional in that same sense** — a `Kafka`-engine-table +
  Materialized View ingestion path (Week 2, Day 13) or a batch-insert sink
  gives you at-least-once semantics at best, not the same rigorous
  exactly-once guarantee as a Flink-to-Kafka sink. Achieving effectively-once
  behavior into ClickHouse in practice typically relies on idempotent
  inserts (e.g., using ClickHouse's `ReplacingMergeTree` engine, which
  de-duplicates by a key during merges, Week 1 Day 1) rather than a true
  transactional sink.
- **Flink + Redis**: commonly used for low-latency state *lookups* (enriching
  a stream with reference data from Redis) rather than as a sink for Flink's
  own primary output — a genuinely different integration shape than a sink.
- **Flink + Elasticsearch sink**: a standard CQRS read-model feed (Week 2,
  Day 10; Week 4, Day 22) — Flink processes and enriches events, then indexes
  results into Elasticsearch for search/facet serving.

## 3. How It Really Works (Internals)

The ClickHouse caveat matters directly for your own architecture: if any part
of your target design assumes Flink-to-ClickHouse writes carry the same
exactly-once guarantee as Flink-to-Kafka (Week 2, Day 9), that's a real gap
worth correcting explicitly — either by using `ReplacingMergeTree`'s
deduplication-by-key as a practical mitigation, or by accepting and
documenting the at-least-once behavior with idempotent downstream handling,
rather than silently assuming a guarantee that doesn't actually hold.

## 4. Architecture & Design Pattern Spotlight

**Pattern: sink-specific guarantee verification — never assume a general
"exactly-once" claim transfers automatically to every sink; verify what the
*specific* target system actually supports.** This is a genuinely important,
easy-to-miss correctness gap worth explicitly checking in your own capstone
design (Day 25).

## 5. Hands-On Lab

Check your own Day 25 capstone design's Flink-to-ClickHouse integration
specifically: does it correctly account for ClickHouse's non-transactional
nature, either via `ReplacingMergeTree` deduplication or explicit
at-least-once acceptance with idempotent handling? If this wasn't addressed
in Day 25's design, add it now as a specific correction.

## 6. Real-World Product Comparison

This is a genuine, well-known caveat in the Flink/ClickHouse integration
community — worth verifying your own design doesn't silently assume a
guarantee ClickHouse doesn't provide.

## 7. Common Production Pitfalls

- Assuming Flink's exactly-once sink pattern (Week 2, Day 9) transfers
  automatically to a ClickHouse sink without verifying ClickHouse's actual
  transactional support.
- Not using `ReplacingMergeTree` (or an equivalent idempotency mechanism)
  when at-least-once delivery to ClickHouse could otherwise produce
  duplicate rows after a restart.

## 8. Review Questions
1. Why doesn't Flink's exactly-once sink pattern transfer automatically to
   ClickHouse?
2. What practical mitigation makes ClickHouse writes effectively idempotent?
3. Does your own Day 25 capstone design correctly address this caveat?
4. What's the difference between the Flink+Redis lookup pattern and a
   Flink+Elasticsearch sink pattern?

## 9. Proficiency Checkpoint
If you've identified and corrected this exact caveat in your own real
design, you're at Level 4 — a genuinely important correctness catch.

## Next
Day 27 is your final interview-readiness and mock-review day.
