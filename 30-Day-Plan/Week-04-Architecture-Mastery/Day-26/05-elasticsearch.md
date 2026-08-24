# Day 26: Elasticsearch — Integrations & Head-to-Head vs. ClickHouse

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Finalize the ES-vs-ClickHouse head-to-head for your actual workload, and
sketch its Kafka/Flink ingestion integration if retained.

## 2. Core Concept (basics → advanced)

Today closes the loop on Day 25's honest ES-vs-ClickHouse assessment: if any
Elasticsearch workload is retained (for genuine search/faceted-navigation
needs), its ingestion integration follows the same CQRS pattern studied all
month (Week 2, Day 10; Week 4, Day 22) — Kafka as the event backbone, Flink
(or a simpler consumer) transforming and indexing into Elasticsearch. If the
honest assessment concluded a workload should migrate to ClickHouse instead,
today is the point to finalize that as a concrete decision, not leave it as
an open question.

## 3. How It Really Works (Internals)

The head-to-head decision, finalized: for each specific Elasticsearch
workload in scope, is it (a) staying on Elasticsearch because of a genuine,
confirmed search/relevance requirement, (b) migrating to ClickHouse because
it's confirmed aggregation-dominant with no genuine search need, or (c) a
split — some access patterns migrate, others stay? This three-way
classification, applied to every actual workload rather than treated as one
global yes/no question, is the mature, precise version of Day 24's
conceptual lesson.

## 4. Architecture & Design Pattern Spotlight

**Pattern: finalized, workload-by-workload classification — resolving Day
25's honest assessment into concrete, actionable decisions for your actual
architecture**, rather than leaving it as an open analytical exercise.

## 5. Hands-On Lab

For each Elasticsearch workload assessed in Day 25, finalize its
classification (stay / migrate / split) and, for anything staying, sketch its
Kafka→[Flink]→Elasticsearch ingestion path explicitly, including expected
staleness tolerance (Week 2, Day 10).

## 6. Real-World Product Comparison

This completes your own real architecture's ES-vs-ClickHouse decision.

## 7. Common Production Pitfalls

- Leaving Day 25's assessment as an open question rather than converting it
  into a concrete decision as part of the final architecture.
- Not designing the retained-ES ingestion path explicitly, assuming it will
  "just work" the same way an existing pipeline does without verification.

## 8. Review Questions
1. What's your final stay/migrate/split classification for each real ES
   workload?
2. For anything staying, what's its ingestion path and staleness tolerance?
3. What evidence from Day 25 supports each classification?
4. Is this decision documented clearly enough for a stakeholder to
   understand the reasoning?

## 9. Proficiency Checkpoint
If you've converted Day 25's assessment into concrete, workload-by-workload
decisions, you're at Level 4.

## Next
Day 27 is your final interview-readiness and mock-review day.
