# Day 11: Architecture — Lambda vs. Kappa vs. Kappa+

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Classify your own current (BigQuery-based) pipeline and target (ClickHouse-based)
pipeline using the Lambda/Kappa/Kappa+ framework — a direct application to your real
S6 benchmark work.

## 2. Core Concept (basics → advanced)

Three architectural philosophies for combining batch and real-time data processing:

- **Lambda architecture**: run **two separate pipelines** in parallel — a batch layer
  (accurate, but high-latency, reprocessing all historical data periodically) and a
  speed layer (low-latency, but potentially less accurate/complete), with a serving
  layer merging both views for queries. The batch layer is the eventual source of truth;
  the speed layer covers the gap until batch catches up.
- **Kappa architecture**: **one single stream-processing pipeline** handles
  everything — no separate batch layer at all. Historical reprocessing (when logic
  changes) is done by replaying the event log through the *same* streaming pipeline,
  not a separate batch codepath.
- **Kappa+**: a pragmatic hybrid some teams adopt — primarily stream-only (Kappa), but
  retaining a batch capability for specific cases where true streaming would be
  prohibitively expensive or complex (e.g., certain very large historical
  reprocessing or backfill operations) rather than dogmatically avoiding batch
  entirely.

```
Lambda:   raw events ──▶ BATCH layer (accurate, slow)  ──▶ serving layer ──▶ query
              │      ──▶ SPEED layer (fast, less exact) ──▶      ▲
              └── (TWO separate codepaths implementing similar logic — real maintenance cost)

Kappa:    raw events ──▶ ONE stream pipeline ──▶ serving layer ──▶ query
              (reprocessing = replay the log through the SAME pipeline, not a second one)
```

## 3. How It Really Works (Internals)

Lambda's core cost is **maintaining two implementations of the same business logic**
(once in a batch framework, once in a streaming framework) — these can drift apart
subtly over time (a bug fixed in one path but not the other), and it's a genuine,
recurring engineering tax, not a one-time setup cost. Kappa's promise is eliminating
this duplication entirely by treating "batch reprocessing" as just "replay the stream
from an earlier offset" — made practical specifically by log-structured systems like
Kafka retaining enough history (or all history, with compaction/tiered storage from
Day 10) to actually support full reprocessing this way.

The honest trade-off: Kappa requires your stream-processing engine (Flink, in this
curriculum) to be capable of the *full range* of what your batch layer used to do —
including expensive, complex historical aggregations — which isn't always
straightforward or cost-effective in a pure streaming engine, which is exactly the gap
**Kappa+** acknowledges pragmatically rather than dogmatically insisting on pure
streaming everywhere.

## 4. Architecture & Design Pattern Spotlight

**Pattern: batch+speed layer duplication (Lambda) vs. stream-only unification
(Kappa) — a direct, practical instance of the micro-batch (Spark Structured Streaming,
Week 1 Day 6) vs. true streaming (Flink) distinction, at the whole-architecture
level.** Your own **S6 benchmark** (the greenfield architecture using ClickHouse,
Iceberg, DragonflyDB, and Flink) is a concrete, real exploration of exactly this
framework — worth explicitly revisiting that benchmark through this Lambda/Kappa lens
as part of today's lab.

## 5. Hands-On Lab

Classify two pipelines explicitly:
1. **Your current production pipeline** (BigQuery-centric): does it have separate
   batch and "real-time-ish" scheduled-query paths (Lambda-shaped), or does
   everything flow through one unified path? Where does duplication of logic
   currently exist, if any?
2. **Your target pipeline** (ClickHouse-based, informed by the S6 benchmark): with
   Flink handling ingestion and Refreshable Materialized Views (Week 1, Day 6) handling
   periodic recompute, is this Lambda-shaped (two distinct codepaths), Kappa-shaped
   (one unified stream path), or Kappa+ (primarily unified, with an accepted batch
   exception for specific expensive recomputations)?

Write one paragraph justifying your classification for the target pipeline, and note
any specific place where a genuine Lambda-style duplication risk still exists in the
target design.

## 6. Real-World Product Comparison

- **LinkedIn** (Kafka's origin) has publicly discussed moving many internal pipelines
  toward Kappa-style architectures specifically to eliminate batch/speed logic
  duplication — a direct real-world validation of the trade-off analysis above.
- Companies with very large, complex historical reprocessing needs (certain financial
  reporting or compliance pipelines) often land on **Kappa+** rather than pure Kappa,
  for the same pragmatic reason your own target architecture might reasonably keep a
  batch/Refreshable-MV escape hatch rather than forcing every computation through Flink.

## 7. Common Production Pitfalls

- Building a Lambda architecture without a disciplined process for keeping batch and
  speed-layer logic in sync — this drift is the single most common real-world Lambda
  pain point cited in practice.
- Adopting "pure Kappa" dogmatically for a workload where a specific expensive
  historical computation genuinely doesn't fit well in a streaming engine, instead of
  pragmatically accepting a Kappa+ exception.
- Not explicitly documenting which architecture style a given pipeline follows —
  without a shared framework/vocabulary, discussions about "should this be batch or
  streaming" tend to relitigate the same trade-offs from scratch every time.

## 8. Review Questions
1. What specific engineering cost does Lambda architecture pay that Kappa avoids?
2. What capability must a streaming engine have for Kappa to be practical at all?
3. Why might a real system pragmatically choose Kappa+ over pure Kappa?
4. How does your own S6 benchmark relate to this framework?

## 9. Proficiency Checkpoint
If you can classify a real, complex pipeline using this framework and identify
specific duplication risk or streaming-capability gaps, you're at Level 3 — directly
applicable to your target-state architecture work.

## Next
Day 12 covers the lakehouse concept (Delta/Iceberg/Hudi) and data mesh vs. lake vs.
lakehouse vs. warehouse — broadening today's architecture-framework thinking further.
