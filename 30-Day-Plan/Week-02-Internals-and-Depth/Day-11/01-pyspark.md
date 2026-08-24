# Day 11: PySpark — Adaptive Query Execution (AQE)

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Run the same skewed join with AQE on vs. off, compare plans and runtime, and explain
what AQE adjusts and when.

## 2. Core Concept (basics → advanced)

Every optimization decision studied so far (join strategy, Day 4; shuffle partition
count, Day 10) has been made **before** the query runs, based on estimates. **Adaptive
Query Execution** instead re-optimizes **during** execution, using *actual* runtime
statistics from completed stages rather than upfront estimates — because estimates
(especially after filters, joins, or UDFs) are often wrong, sometimes by orders of
magnitude, and a plan that looked reasonable on paper can be badly wrong once real
data shapes are known.

AQE performs three main runtime adjustments:
- **Dynamically coalescing shuffle partitions**: if post-shuffle partitions turn out
  much smaller than expected, AQE merges adjacent small partitions into fewer, larger
  ones — directly mitigating the "too many shuffle partitions for small data" half of
  Day 10's spill discussion.
- **Dynamically switching join strategies**: if a table estimated as "large" turns out
  small after actual filtering, AQE can switch a planned sort-merge join to a broadcast
  join mid-query — the exact strategy decision from Day 4, now made with real numbers.
- **Dynamically optimizing skewed joins**: AQE detects partitions that are
  disproportionately large post-shuffle and automatically splits them into smaller
  sub-partitions processed independently — an automated version of the manual salting
  technique from Day 4.

## 3. How It Really Works (Internals)

AQE works by inserting re-optimization checkpoints at shuffle boundaries — since a
shuffle already requires materializing data (Day 3), Spark can cheaply gather exact
statistics (row counts, partition sizes) at that point and feed them back into the
query planner *before* the next stage begins, without needing separate profiling
passes. This is why AQE's benefits concentrate specifically around
shuffle-adjacent decisions (join strategy, partition count) rather than, say,
predicate pushdown or column pruning — those decisions don't benefit from
mid-execution statistics the same way, since they don't depend on data that's only
known after a shuffle completes.

Skew handling specifically works by identifying partitions whose size significantly
exceeds the median partition size (a configurable threshold), and splitting the
processing of that oversized partition into multiple smaller reads processed by
separate tasks, then correctly combining the results — solving the exact "one hot key,
one straggler task" problem from Day 4, without requiring you to manually engineer a
salting scheme.

## 4. Architecture & Design Pattern Spotlight

**Pattern: self-tuning/adaptive execution — re-optimizing based on runtime
observation rather than only upfront estimation.** This is the same philosophical
shift as **BigQuery's automatic slot allocation** and **Snowflake's automatic
clustering/warehouse sizing** — modern data platforms increasingly push optimization
decisions from "human/estimate-driven, decided once" toward "system-driven, decided
continuously from observed behavior." Recognizing this trend explains a lot of where
platform investment is currently going across the whole industry, not just in Spark.

## 5. Hands-On Lab

```python
spark.conf.set("spark.sql.adaptive.enabled", "false")
# ... run your Day 4 skewed join lab, note stage duration in Spark UI ...

spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
# ... re-run the SAME skewed join ...
```
Compare: does the AQE-enabled run show a different physical plan (check `.explain()`
— look for `AQEShuffleRead` or skew-join markers)? Compare stage duration and the
task-duration distribution in the Spark UI between the two runs — AQE should visibly
reduce or eliminate the single-straggler-task pattern from Day 4's manual
investigation.

## 6. Real-World Product Comparison

- **BigQuery**'s automatic slot allocation adjusts compute resources per query
  dynamically based on observed query shape — conceptually the same "adapt based on
  what's actually happening" philosophy as AQE, at the resource-allocation layer
  instead of the join-strategy layer.
- **Snowflake**'s automatic clustering continuously reorganizes data based on observed
  query patterns over time — a longer-timescale version of the same underlying idea:
  let the system observe and adapt, rather than requiring a human to get every
  decision right upfront.

## 7. Common Production Pitfalls

- Leaving AQE disabled on Spark versions where it's not the default, missing out on
  automatic skew handling that would otherwise require manual salting (Day 4)."
- Assuming AQE eliminates the *need* to understand join strategies and skew — AQE
  handles many cases well, but understanding the underlying mechanism (this whole
  week) is what lets you diagnose the cases AQE *doesn't* fully resolve.
- Not tuning AQE's skew-detection thresholds for genuinely unusual data
  distributions — the defaults are reasonable general-purpose values, not universally
  optimal for every workload's specific skew characteristics.

## 8. Review Questions
1. Why do AQE's adjustments concentrate specifically around shuffle boundaries?
2. How does AQE's skew handling relate to the manual salting technique from Day 4?
3. What's the conceptual similarity between AQE and BigQuery's automatic slot
   allocation?
4. Why doesn't AQE reduce the value of understanding join strategies and skew manually?

## 9. Proficiency Checkpoint
If you can explain specifically what AQE changed in a real before/after plan
comparison, you're at Level 3.

## Next
Day 12 covers Parquet internals — row groups and predicate/column pushdown — the file
format underneath most of the lakehouse architectures Week 2 and Week 3 build toward.
