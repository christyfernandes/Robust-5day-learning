# Day 25: Elasticsearch — Could ClickHouse Replace This ES Workload?

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Honestly assess whether ClickHouse could replace any current Elasticsearch
workload in your environment — writing the full comparison, not just the
conclusion.

## 2. Core Concept (basics → advanced)

Day 24's "when NOT to use it" lesson named the ES-vs-ClickHouse-for-dashboards
mismatch directly. Today: apply it as a genuine, honest assessment against
whatever Elasticsearch usage actually exists in your environment (if any),
rather than a hypothetical exercise. The discipline that matters here: **write
the comparison, not just the conclusion** — a one-line "yes, migrate" or "no,
keep it" is far less useful to stakeholders than the reasoning that produced
it, since the reasoning is what lets others evaluate whether it still holds as
circumstances change.

## 3. How It Really Works (Internals)

The comparison should explicitly separate: **genuine search/relevance
requirements** (Week 1, Day 3's BM25 and query-DSL material — does this
workload actually need full-text relevance ranking, fuzzy matching, or
faceted navigation?) from **aggregation/analytics requirements** (Week 1, Day
4 — does it primarily compute rollups, sums, and group-bys over large
volumes?). If the honest answer is "overwhelmingly the latter, with
negligible genuine search need," that's Day 24's mismatch, concretely
confirmed rather than assumed. If there's a genuine mixed requirement, the
comparison should state explicitly which parts could migrate and which
should stay.

## 4. Architecture & Design Pattern Spotlight

**Pattern: honest capability audit — separating what a system was *chosen for*
from what it's *actually being used for* today**, which can drift apart over
time (Day 24's lesson noted this explicitly) without anyone deliberately
deciding to make that drift happen.

## 5. Hands-On Lab

For whatever Elasticsearch usage exists in your environment (or the closest
proxy, if none does directly), write the full comparison: what fraction of
actual query volume is genuine search/relevance vs. aggregation-only? What
would a ClickHouse-based replacement look like for the aggregation-heavy
portion specifically (schema design informed by Day 22's OBT/star-schema
lesson)? What, if anything, would need to remain on Elasticsearch (or move to
a purpose-built search tool, Week 3 Day 20) for genuine search needs?

## 6. Real-World Product Comparison

This is your own honest environment audit, informed by Day 24's architectural
lesson.

## 7. Common Production Pitfalls

- Writing only the conclusion ("migrate" or "don't") without the supporting
  reasoning, producing a less durable, less defensible recommendation.
- Assuming an all-or-nothing answer when the honest assessment might show a
  genuine mixed requirement warranting a split architecture.

## 8. Review Questions
1. What fraction of your actual (or hypothetical) ES workload is genuine
   search vs. aggregation-only?
2. What would a ClickHouse-based replacement look like for the
   aggregation-heavy portion?
3. Why is writing the full comparison more valuable than stating only the
   conclusion?
4. Is an all-or-nothing migration the right answer, or a split architecture?

## 9. Proficiency Checkpoint
If you've produced a full, honest, reasoned comparison (not just a
conclusion), you're at Level 4.

## Next
This feeds directly into today's ClickHouse and Architecture lessons — the
full MDO portal migration capstone design.
