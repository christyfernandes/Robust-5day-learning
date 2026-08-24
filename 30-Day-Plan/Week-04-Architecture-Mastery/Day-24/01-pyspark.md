# Day 24: PySpark — When NOT to Use It

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Write the one sentence you'd say in a design review when someone proposes Spark
for the wrong job.

## 2. Core Concept (basics → advanced)

Spark's architecture (Week 1, Day 1) — JVM-based, DAG-scheduled, optimized for
distributed processing of large datasets — has a genuine **latency floor**: job
startup, DAG scheduling, and JVM overhead mean even a trivially small query pays
real fixed cost (typically seconds, not milliseconds) before any actual work
begins. This makes Spark a poor fit for:
- **Small-data workloads**: if your data comfortably fits in a single machine's
  memory, Spark's distributed-coordination overhead (Week 1, Day 3's
  DAGScheduler/TaskScheduler machinery) is pure cost with no corresponding
  benefit — a single-node tool (DuckDB, Polars, or even Pandas) does the same
  job faster with none of the distributed-systems complexity.
- **Interactive/low-latency query serving**: Spark's execution model (even with
  AQE, Week 2 Day 11) isn't built for sub-second, high-concurrency interactive
  queries — that's precisely ClickHouse's or Trino's home turf, not Spark's.

## 3. How It Really Works (Internals)

The correct mental test: **does this job's problem size and latency requirement
actually need distributed execution?** If a job processes gigabytes on a
schedule with minutes of acceptable latency, Spark is likely appropriate. If a
job processes megabytes and needs sub-second response for an interactive user,
Spark's entire architecture (built around Week 1's DAG/shuffle/stage model) is
solving a problem you don't have, at a real, unnecessary cost.

## 4. Architecture & Design Pattern Spotlight

**Pattern: matching tool architecture to actual problem shape — the Level 4 skill
of recognizing when a familiar, well-understood tool is nonetheless the wrong
choice for a specific job**, rather than defaulting to whatever tool a team
already knows well.

## 5. Hands-On Lab

Write the one sentence you'd say in a design review when someone proposes
Spark for a genuinely small-data or interactive-latency use case — something
concrete and specific enough to actually redirect the conversation productively,
not just "Spark is for big data."

## 6. Real-World Product Comparison

- **Trino/Presto**: better fit for interactive, federated SQL queries across
  multiple sources (Week 1, Day 1's comparison).
- **DuckDB/Polars**: purpose-built for single-node, in-process analytical
  workloads — genuinely faster than Spark for data that fits comfortably in one
  machine's memory, with none of the distributed-coordination overhead.
- **ClickHouse**: the right choice specifically for high-concurrency,
  low-latency interactive analytical queries at scale — this month's central
  case study.

## 7. Common Production Pitfalls

- Defaulting to Spark because a team already knows it well, for a workload
  that would be faster and simpler on a single-node tool.
- Not periodically re-evaluating whether a job's actual data volume still
  justifies Spark's overhead as volume changes over a system's lifetime.

## 8. Review Questions
1. What specifically causes Spark's latency floor?
2. When does distributed-processing overhead outweigh its benefit?
3. What's your one-sentence design-review pushback?
4. What tool would you propose instead, for a small-data or interactive use case?

## 9. Proficiency Checkpoint
If you have a real, specific one-sentence pushback ready, you're at Level 4.

## Next
Day 25 turns this judgment directly onto your own real work — the MDO portal
migration design.
