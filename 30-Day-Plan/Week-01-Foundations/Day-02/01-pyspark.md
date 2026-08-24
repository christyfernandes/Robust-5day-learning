# Day 2: PySpark — DataFrame API, Spark SQL & the Catalyst Optimizer

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Trace what actually happens between writing a `.filter().join().groupBy()` chain and
Spark executing it — the four-stage optimization pipeline — well enough to predict
which of two equivalent queries Spark will run faster.

## 2. Core Concept (basics → advanced)

**DataFrame operations, the vocabulary you'll use constantly:**
```python
df = spark.read.parquet("orders.parquet")

result = (
    df.filter(df.amount > 100)
      .select("customer_id", "amount", "order_date")
      .groupBy("customer_id")
      .agg({"amount": "sum"})
)

df.createOrReplaceTempView("orders")
spark.sql("SELECT customer_id, SUM(amount) FROM orders WHERE amount > 100 GROUP BY customer_id")
```
These two blocks — DataFrame API and raw SQL — produce **the same physical plan**. This
isn't a coincidence: both are just different front-ends onto the same underlying
Catalyst optimizer.

## 3. How It Really Works (Internals)

**Catalyst's four phases**, in order:
```
Your code / SQL
      │
      ▼
1. Unresolved Logical Plan   (parsed, but column/table names not yet validated)
      │  (Analyzer: resolve against catalog/schema)
      ▼
2. Resolved Logical Plan     (all references validated, types known)
      │  (rule-based optimizer: predicate pushdown, constant folding,
      │   column pruning, etc.)
      ▼
3. Optimized Logical Plan    ("push the filter as close to the data source as
      │                       possible" is a rule applied here, for example)
      │  (planner: generate candidate physical plans, cost-based selection
      │   for things like join strategy)
      ▼
4. Physical Plan             (this is what actually executes — concrete join
                               algorithm chosen, exchange/shuffle boundaries fixed)
```

**Concretely, what "optimized" means:** if you write `df.select(...).filter(...)` (filter
*after* select), Catalyst will still often push the filter down to run *before* the
select and even before a join, because filtering early reduces the data volume flowing
through everything downstream — the **logical** plan gets rewritten regardless of the
order you happened to write the calls in. This is exactly why DataFrame code and
equivalent SQL produce identical performance: Catalyst normalizes both into the same
logical plan before optimizing.

You can see all four phases yourself:
```python
result.explain(mode="extended")
```

## 4. Architecture & Design Pattern Spotlight

**Pattern: rule-based + cost-based query optimization**, the same overall shape used by
every mature SQL engine (Postgres's planner, BigQuery, Trino). Once you've internalized
this four-phase pipeline for Spark, reading Trino's or Postgres's `EXPLAIN` output
becomes far more legible — you're looking for the same categories of decisions
(pushdown, pruning, join strategy) even though the specific rules differ.

## 5. Hands-On Lab
```python
df = spark.read.parquet("orders.parquet")

# Two equivalent queries, written differently:
q1 = df.filter(df.amount > 100).select("customer_id", "amount")
q2 = df.select("customer_id", "amount").filter(df.amount > 100)

q1.explain(mode="extended")
q2.explain(mode="extended")
```
Confirm the **physical plans** for `q1` and `q2` are identical, despite the different
write order — this is Catalyst's optimized logical plan doing its job. Then try adding
a `.join()` and inspect whether it chose `BroadcastHashJoin` or `SortMergeJoin` (Day 4
in Week 1 covers why).

## 6. Real-World Product Comparison

- **Databricks' Photon** engine is, among other things, a from-scratch native-code
  re-implementation of Spark's physical execution layer that still plugs into the same
  Catalyst-produced physical plan — same optimizer, dramatically faster execution
  layer underneath.
- **Trino/Presto** has an analogous cost-based optimizer producing similarly-shaped
  physical plans (with its own exchange/shuffle equivalents) — if you can read a Spark
  physical plan, a Trino query plan will feel familiar rather than foreign.
- Contrast with a naive in-house SQL-on-Hadoop tool with no cost-based optimizer: the
  order you write your query *would* matter for performance, because there's no
  rewriting step — a good motivator for why this whole optimizer layer exists.

## 7. Common Production Pitfalls
- Writing overly clever manual query reordering "for performance" — usually
  unnecessary and sometimes counterproductive, since Catalyst already reorders based on
  cost, and hand-reordering can obscure intent for the next reader.
- Wrapping filter conditions inside Python UDFs — Catalyst can't push a UDF-based
  predicate down or reason about it the way it can a native `filter()` expression,
  silently disabling a whole category of optimization.
- Not checking `.explain()` when a "simple" query is mysteriously slow — the physical
  plan usually reveals the real cause (an unexpected shuffle, a missed pushdown) within
  seconds of looking.

## 8. Review Questions
1. Why do the DataFrame API and Spark SQL produce identical performance for equivalent
   queries?
2. Name the four Catalyst phases in order, and what changes between "resolved logical"
   and "optimized logical."
3. Why does wrapping a condition in a Python UDF disable pushdown optimization?
4. What would you look at first if a query's physical plan seemed unexpectedly slow?

## 9. Proficiency Checkpoint
If you can read a `.explain(mode="extended")` output and identify at least the physical
plan's join strategy and whether a shuffle occurs, you're at Level 2, moving into Level 3.

## Next
Day 3 covers Spark's cluster architecture in more depth — driver/executor/stage/task
scheduling mechanics, and where a shuffle boundary in today's physical plans actually
executes across the cluster.
