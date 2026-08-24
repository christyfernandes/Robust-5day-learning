# Day 15: PySpark — Tuning Playbook

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Tune `spark.sql.shuffle.partitions` and the broadcast join threshold for a real join,
and measure the before/after difference directly.

## 2. Core Concept (basics → advanced)

This month has covered the individual mechanisms (shuffle, Day 3; join strategies,
Day 4; AQE, Week 2 Day 11) — today consolidates them into a practical **tuning
playbook**: a small set of rules of thumb, each directly traceable back to Catalyst's
underlying cost model, rather than "magic numbers" to memorize.

- **Partition sizing**: target roughly 100-200MB of data per shuffle partition as a
  starting heuristic — too few partitions means large per-task shuffle buffers
  (spill risk, Week 2 Day 10); too many means excessive task-scheduling overhead
  relative to the actual work per task.
- **Shuffle minimization**: prefer operations that don't require a shuffle at all
  (filter before join, project only needed columns before a wide operation) over
  optimizing a shuffle you didn't need to have in the first place.
- **Broadcast threshold**: `spark.sql.autoBroadcastJoinThreshold` (default 10MB) —
  raising it lets more real-world "small" dimension tables qualify for the much
  cheaper broadcast join (Day 4) automatically, without needing an explicit hint every
  time.

## 3. How It Really Works (Internals)

Each of these rules of thumb exists because of a specific mechanism you've already
studied in depth: partition sizing balances against the shuffle-spill mechanics
(Week 2, Day 10) — the "right" partition size is the one that keeps a task's
in-memory sort/aggregate buffer from spilling excessively while not fragmenting work
into too many tiny tasks. The broadcast threshold interacts directly with executor
memory sizing (Week 2, Day 9) — raising it without considering actual available
executor memory can itself cause OOM if a "small" table turns out to be too large to
comfortably broadcast to every executor simultaneously.

This is why a genuine tuning playbook isn't a list of universal constants — it's a
set of starting heuristics that must be validated against your *actual* cluster's
memory budget and your *actual* data's size distribution, using exactly the
diagnostic tools (Spark UI, `.explain()`, AQE's runtime adjustments) studied earlier
this month.

## 4. Architecture & Design Pattern Spotlight

**Pattern: rules of thumb codified from an underlying cost model, not arbitrary
defaults.** Every "just set X to Y" recommendation in Spark tuning traces back to a
specific mechanism (shuffle spill, broadcast memory cost, task scheduling overhead) —
the actual skill is being able to derive the right starting value for *your*
workload from first principles, then validate and adjust using real measurements,
rather than copying a number from a blog post written for a different workload shape.

## 5. Hands-On Lab

```python
# baseline: defaults
df_fact = spark.range(0, 20_000_000).withColumn("dim_id", (F.col("id") % 500))
df_dim = spark.range(0, 500).withColumnRenamed("id", "dim_id").withColumn("tier", F.lit("gold"))

result = df_fact.join(df_dim, "dim_id").groupBy("tier").count()
result.write.mode("overwrite").parquet("/tmp/day15_baseline")
# note total duration + shuffle metrics from Spark UI

# tuned
spark.conf.set("spark.sql.shuffle.partitions", "50")           # sized for this data volume
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50mb") # ensures df_dim qualifies
result2 = df_fact.join(df_dim, "dim_id").groupBy("tier").count()
result2.write.mode("overwrite").parquet("/tmp/day15_tuned")
```
Compare total job duration and shuffle read/write bytes between the baseline and
tuned runs — confirm the tuned version uses a broadcast join (check `.explain()`) and
completes measurably faster.

## 6. Real-World Product Comparison

- **Databricks'** cluster-sizing recommendations and auto-tuning features
  (Photon-aware defaults) attempt to bake much of this playbook in automatically —
  part of what a managed platform sells is not needing to derive these heuristics
  yourself for common workload shapes.
- Every principle here transfers conceptually to **any** shuffle-based distributed
  engine — the same partition-sizing and broadcast-threshold reasoning applies (with
  different specific config names) to Trino, Presto, and other distributed SQL
  engines.

## 7. Common Production Pitfalls

- Copying tuning values from a different team's workload without validating against
  your own data size/shape and cluster memory budget.
- Raising the broadcast threshold without checking whether executor memory can
  actually accommodate broadcasting tables at the new, larger threshold.
- Tuning once and never revisiting — data volume and shape typically grow over time,
  and a partition-sizing choice that was correct a year ago may no longer be.

## 8. Review Questions
1. Why does partition sizing target a specific data-size range rather than a fixed
   partition count?
2. What's the risk of raising the broadcast threshold without checking executor
   memory?
3. Why are these "rules of thumb" rather than universal constants?
4. How would you validate a tuning change actually helped, using tools from earlier
   this month?

## 9. Proficiency Checkpoint
If you can derive a sensible starting tuning configuration for a described workload
and validate it with real before/after measurements, you're at Level 3.5.

## Next
Day 16 revisits your real memory over-allocation incident with exact numbers,
calculating precisely where the over-allocation occurred against your node's actual
RAM.
