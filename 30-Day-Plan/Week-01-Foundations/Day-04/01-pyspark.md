# Day 4: PySpark — Join Strategies & Skew

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Name Spark's three main join strategies, explain when the optimizer picks each one, and
recognize + fix data skew — directly applicable to the ClickHouse fan-out problem you're
solving at work this same week.

## 2. Core Concept (basics → advanced)

A join between two DataFrames needs matching rows to end up on the same executor. How
Spark gets them there depends on the size of the tables involved:

- **Broadcast hash join**: the smaller table is sent, in full, to *every* executor
  (no shuffle of the large table at all). Fast — but only works when the small side
  actually fits comfortably in each executor's memory (default threshold: 10MB, tunable).
- **Shuffle hash join**: both tables are shuffled by join key so matching keys land on
  the same executor, then a hash table is built from the smaller side per-partition.
  Works for larger tables than broadcast allows, but pays full shuffle cost on both sides.
- **Sort-merge join**: both sides are shuffled *and* sorted by join key, then merged
  like a zipper. Spark's default for large-large joins — more shuffle+sort overhead than
  a hash join, but far more memory-stable (no need to hold a full hash table for one side).

```
Broadcast:  small table copied to every executor → no shuffle of big table
Shuffle-hash / sort-merge: BOTH tables shuffled by key → matching rows co-located
```

## 3. How It Really Works (Internals)

The Catalyst optimizer picks a strategy automatically based on estimated table sizes
(from statistics, if available, or size hints) — you can force a specific strategy with
a join hint (`.hint("broadcast")`) when you know better than the optimizer's estimate,
which is common when statistics are stale or a filter dramatically shrinks a table that
Spark doesn't yet know is small.

**Skew** happens when one join key value is disproportionately common (e.g., a
`null`/default org_id, or one dominant customer). In a shuffle-based join, *all* rows for
that one key land on a single task — that task becomes a straggler holding up the entire
stage, no matter how many executors you add, because you can't split one key's rows
across multiple tasks in a plain shuffle join. The standard fix is **salting**: append a
random suffix to the skewed key on both sides (matching ranges), artificially splitting
the hot key's rows across multiple synthetic keys/tasks, then aggregate the partial
results back together.

## 4. Architecture & Design Pattern Spotlight

**Pattern: broadcast (avoid the shuffle) vs. partitioned shuffle (co-locate then
merge).** This exact choice — send the small side everywhere vs. redistribute both
sides by key — is precisely the same decision ClickHouse's query planner makes with a
`GLOBAL JOIN` (its version of broadcast) vs. a plain distributed join (its version of
shuffle), and it's the direct root cause of your real MDO portal fan-out problem: a join
that should be broadcast-sized behaving like a full shuffle join across every shard.

## 5. Hands-On Lab

```python
# small dimension table + large fact table
dim = spark.createDataFrame([(1, "gold"), (2, "silver")], ["id", "tier"])
fact = spark.range(0, 5_000_000).withColumnRenamed("id", "user_id") \
            .withColumn("dim_id", (F.col("user_id") % 2) + 1)

# force each strategy, compare via .explain()
fact.join(dim.hint("broadcast"), fact.dim_id == dim.id).explain()
fact.join(dim.hint("shuffle_hash"), fact.dim_id == dim.id).explain()
fact.join(dim.hint("merge"), fact.dim_id == dim.id).explain()
```
Read each physical plan — find `BroadcastHashJoin` vs. `ShuffleHashJoin` vs.
`SortMergeJoin` in the output. Then engineer artificial skew (make 90% of `dim_id`
rows the value `1`) and compare stage duration in the Spark UI across strategies.

## 6. Real-World Product Comparison

- **BigQuery**'s query planner makes the same broadcast-vs-shuffle decision
  automatically based on table statistics — the exact same failure mode (an
  under-sized-looking dimension table actually being large post-filter) causes the same
  kind of unexpected full-shuffle join cost there too.
- This is the direct parallel to your **ClickHouse fan-out issue**: a `GLOBAL JOIN`
  broadcasts a subquery's result to every shard once; a plain `JOIN` in a distributed
  query can silently re-execute the right-side subquery per shard — the "silent
  multiplication" mechanism you're actively debugging on the MDO portal dashboards.

## 7. Common Production Pitfalls

- Letting a "small" dimension table grow past the broadcast threshold without noticing
  — the join silently falls back to shuffle, and the job just gets slower with no error.
- Not recognizing task-duration skew in the Spark UI (a few tasks taking 10x longer than
  the median) as a data-skew symptom rather than a "the cluster is slow today" symptom.
- Salting without also aggregating the results back correctly — salting a key for the
  join but forgetting the post-join re-aggregation step produces subtly wrong output,
  not an error.

## 8. Review Questions
1. Why does a broadcast join avoid shuffling the large table entirely?
2. What specifically makes a shuffle-based join vulnerable to skew, structurally?
3. How does salting fix skew without changing the actual join semantics?
4. What's the direct parallel between Spark's broadcast join and ClickHouse's `GLOBAL JOIN`?

## 9. Proficiency Checkpoint
If you can look at a slow join's Spark UI task-duration distribution and correctly
diagnose "skew" vs. "just needs a broadcast hint," you're at Level 2 moving into Level 3
— and you now have the exact vocabulary for this week's ClickHouse fan-out investigation.

## Next
Day 5 moves from join mechanics to memory: Spark's unified memory model and caching —
what actually happens when you call `.cache()`.
