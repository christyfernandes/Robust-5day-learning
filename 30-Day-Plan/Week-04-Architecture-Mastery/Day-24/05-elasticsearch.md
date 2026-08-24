# Day 24: Elasticsearch — When NOT to Use It (ES vs. ClickHouse for Dashboards)

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Write the one sentence you'd say in a design review when someone proposes
Elasticsearch for an aggregation-heavy analytical dashboard — and know exactly
why, directly relevant to your own work.

## 2. Core Concept (basics → advanced)

Elasticsearch's aggregation framework (Week 1, Day 4) is genuinely capable, but
its underlying architecture — an inverted index (Week 1, Day 1) optimized for
**text search and document retrieval**, with aggregation as a secondary,
scatter-gather capability built on top — is not the same architecture as a
purpose-built columnar OLAP engine (ClickHouse, Week 1 Day 1) built from the
ground up for exactly the "scan and aggregate over millions of rows" access
pattern a dashboard needs.

The specific, concrete signal: if your actual workload is **primarily
aggregation-heavy analytical queries** (group-by, sum, count-distinct over large
volumes, Week 1 Day 4) with **little or no genuine full-text search
requirement**, you're very likely using Elasticsearch's secondary capability
(aggregations) while paying for infrastructure and licensing overhead built
around its *primary* capability (text search) that you don't actually need.

## 3. How It Really Works (Internals)

The underlying architectural reason ClickHouse tends to win this specific
comparison: its columnar storage and vectorized execution (Week 1, Day 1; Week
2, Day 8) are purpose-built for exactly the access pattern of scanning large
volumes of a few relevant columns and aggregating — Elasticsearch's document-
oriented, inverted-index storage (Week 1, Day 1) is optimized for a different
access pattern (find documents matching a query, score and rank them), and its
aggregation performance, while genuinely useful, generally doesn't match a
purpose-built columnar engine's raw throughput for pure analytical workloads at
comparable scale — this is precisely the architectural mismatch worth
articulating clearly in a design review, not just asserting as received wisdom.

This is directly, concretely relevant to **your own MDO portal work**: if any
part of that portal's current or historical architecture uses (or considered
using) Elasticsearch for what's fundamentally dashboard-style aggregation
rather than genuine search, that's exactly the mismatch this lesson names —
worth an honest, explicit assessment as part of Day 25's real design work,
not just a hypothetical exercise.

## 4. Architecture & Design Pattern Spotlight

**Pattern: matching tool architecture to actual access pattern — the single
most directly work-relevant "when NOT to use it" case in this entire
curriculum.** Recognizing "is this fundamentally a search problem or an
aggregation problem" as the deciding question, rather than "which tool do we
already have," is precisely the Level 4 judgment this whole day is building.

## 5. Hands-On Lab

Write the one sentence you'd say in a design review when someone proposes
Elasticsearch for a fundamentally aggregation-heavy dashboard with no genuine
full-text search requirement. Then, honestly and specifically: does any part of
your own current or planned MDO portal architecture fall into this exact
mismatch? If so, write down what a ClickHouse-based alternative would look
like for that specific piece.

## 6. Real-World Product Comparison

- Many organizations that adopted Elasticsearch primarily for its aggregation
  capability (rather than genuine search needs) have migrated analytics-heavy
  workloads to purpose-built OLAP engines (ClickHouse, Druid, Pinot) once query
  volume and cost made the architectural mismatch expensive enough to address
  directly — exactly the trajectory your own BigQuery→ClickHouse work is
  already on, worth applying the same lens to any Elasticsearch usage too.
- Conversely, genuine full-text/faceted search use cases (Week 4, Day 22's
  CQRS read-model lesson) remain a strong, appropriate fit for Elasticsearch —
  this isn't "Elasticsearch is wrong," it's "Elasticsearch is wrong **for this
  specific access pattern**."

## 7. Common Production Pitfalls

- Defaulting to Elasticsearch for a new analytical dashboard because it's
  already deployed for search elsewhere in the organization, without assessing
  whether the actual access pattern fits its strengths.
- Conflating "Elasticsearch can technically do aggregations" with
  "Elasticsearch is the right tool for aggregation-heavy workloads" — capability
  and fitness are different questions.
- Not periodically re-assessing existing Elasticsearch usage as query patterns
  evolve — a use case that started as genuine search can drift toward
  primarily-aggregation over time without anyone noticing the architectural
  mismatch has emerged.

## 8. Review Questions
1. What's the precise architectural reason ClickHouse tends to outperform
   Elasticsearch for pure aggregation workloads?
2. What's the deciding question for whether a use case is "search" or
   "aggregation"?
3. What's your one-sentence design-review pushback?
4. Does any part of your own real architecture exhibit this exact mismatch?

## 9. Proficiency Checkpoint
If you can articulate this trade-off precisely and have honestly assessed your
own architecture against it, you're at Level 4 — this is one of the most
directly applicable judgments from the entire curriculum.

## Next
Day 25 asks you to honestly assess this exact question for your own real ES
workload, writing the comparison, not just the conclusion.
