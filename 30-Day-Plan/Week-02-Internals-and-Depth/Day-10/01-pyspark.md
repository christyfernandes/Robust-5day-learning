# Day 10: PySpark — Shuffle Internals: Sort-Based Shuffle & Spill

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Force a large shuffle with a deliberately low `spark.sql.shuffle.partitions`, watch
spill metrics in the Spark UI, and connect this directly to your disk-space-at-87%
production concern.

## 2. Core Concept (basics → advanced)

Day 3 established that a shuffle writes data to local disk, partitioned by key, for
the next stage to read. Modern Spark uses **sort-based shuffle** exclusively (the
older hash-based shuffle was removed) — each task sorts its output records by
destination partition ID before writing, producing one sorted, indexed output file
per task (rather than one file per destination partition per task, which the older
hash-based approach did, and which produced far more small files at scale).

**Spill** happens when a task's in-memory buffer for sorting/aggregating shuffle data
exceeds its allotted execution memory (Day 5) — Spark writes the excess to a temporary
disk file (a "spill file"), continues accumulating in memory, and eventually
merges all spill files with the remaining in-memory data via an **external merge
sort** — the same fundamental algorithm a database uses for a sort that doesn't fit in
RAM.

```
Task's shuffle buffer fills execution memory
       │
       ▼
SPILL: write current buffer contents to a temp file on LOCAL DISK
       │ (repeat as needed — multiple spill files can accumulate per task)
       ▼
Once all input is processed: MERGE all spill files + remaining in-memory data
       via external merge sort → final sorted shuffle output
```

## 3. How It Really Works (Internals)

Spill files, shuffle output files, and any cached-to-disk (`MEMORY_AND_DISK`)
DataFrame partitions all land in the executor's configured **local directories**
(`spark.local.dir`) — on a node running multiple concurrent jobs or a data-heavy
pipeline, this is precisely the mechanism that can silently consume disk space: spill
files accumulate during a job's execution and are normally cleaned up afterward, but a
job that spills heavily, runs long, or crashes before cleanup can leave substantial
temporary data behind — directly relevant to a production node sitting at 87% disk
capacity, since PySpark's own shuffle/spill activity is a very plausible contributor
worth checking, not just externally-accumulated data.

A low `spark.sql.shuffle.partitions` setting (the number of partitions a shuffle
produces, default 200) relative to actual data volume means each partition carries
more data — larger per-task shuffle buffers, more spill, and a real, direct link
between this one config value and disk pressure.

## 4. Architecture & Design Pattern Spotlight

**Pattern: external merge sort — spilling to disk when memory is insufficient, then
merging.** This is a foundational algorithm across nearly every system that processes
more data than fits in memory: database query engines doing a large `ORDER BY`,
ClickHouse's own merge process for MergeTree parts (Day 1), and Spark's shuffle here —
recognize "sort what fits, spill the rest, merge everything" as one of the most reused
ideas in all of data systems.

## 5. Hands-On Lab

```python
spark.conf.set("spark.sql.shuffle.partitions", "4")  # deliberately too low

df = spark.range(0, 50_000_000).withColumn("key", (F.col("id") % 1000))
result = df.groupBy("key").agg(F.sum("id"), F.count("*"))
result.write.mode("overwrite").parquet("/tmp/day10_output")
```
While it's running, check the Spark UI's **Stages** tab for this job's shuffle stage —
look at **Shuffle Spill (Memory)** and **Shuffle Spill (Disk)** columns. Also check
`spark.local.dir`'s actual disk usage (`du -sh`) during the run. Now re-run with
`spark.sql.shuffle.partitions` set to a more reasonable value (e.g., `200`) and compare
spill metrics — this is the exact knob to check first for your real disk-space
investigation.

## 6. Real-World Product Comparison

- Spill-to-local-disk during a shuffle is a standard, expected part of Spark's
  execution model at scale — the operational question is never "should spill happen"
  but "is spill volume proportionate, and is disk being reclaimed properly afterward."
- Compare to **Flink's** RocksDB state backend (Week 1, Day 5) — a related but distinct
  concept: RocksDB spills *state* to disk by design as a normal operating mode, whereas
  Spark's shuffle spill is closer to an overflow valve for a specific operation, not a
  persistent storage strategy.

## 7. Common Production Pitfalls

- Leaving `spark.sql.shuffle.partitions` at its default (200) regardless of actual
  data volume — either too many partitions for small jobs (overhead) or too few for
  large jobs (excessive spill), when it should scale with real data size.
- Not monitoring `spark.local.dir` disk usage as a distinct metric from overall node
  disk usage — spill/shuffle temp files can be a large, variable contributor that's
  easy to overlook when just watching aggregate disk percentage.
- Assuming a crashed job automatically cleans up its spill files — verify this is
  actually happening in your environment, especially after abnormal job termination.

## 8. Review Questions
1. What specifically triggers a spill, and what happens to the data once it's spilled?
2. Why does sort-based shuffle produce fewer files per task than the old hash-based
   approach?
3. How does `spark.sql.shuffle.partitions` directly affect spill volume?
4. Why is checking `spark.local.dir` disk usage specifically (not just overall node
   disk usage) the right first diagnostic step for your production concern?

## 9. Proficiency Checkpoint
If you can look at real Spark UI spill metrics and connect them to a concrete disk-
space investigation, you're at Level 3 — directly applicable to your current
production concern.

## Next
Day 11 covers Adaptive Query Execution — Spark's mechanism for adjusting shuffle
partition counts and join strategies automatically, partly in response to exactly this
kind of spill/skew problem.
