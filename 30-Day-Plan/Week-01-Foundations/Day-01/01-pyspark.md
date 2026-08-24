# Day 1: PySpark — Distributed Compute Foundations

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain why Spark exists (what it fixed about MapReduce), correctly describe the
RDD → DataFrame → Dataset relationship, and run a first job while being able to name
what "lazy evaluation" actually defers.

## 2. Core Concept (basics → advanced)

**The problem Spark solved.** Hadoop MapReduce persisted intermediate results to disk
between every map and reduce stage. For iterative workloads (ML training, graph
algorithms) or multi-step ETL, that meant repeated disk I/O for data that could easily
fit in memory. Spark's core idea: keep data in memory across steps, and only write to
disk when you run out of memory or explicitly need durability.

**RDD (Resilient Distributed Dataset)** — the original abstraction. An RDD is an
immutable, partitioned collection, with a recorded **lineage** (the chain of
transformations that produced it) instead of the data itself being replicated for fault
tolerance. If a partition is lost, Spark recomputes it from lineage rather than reading
a replica — this is the "resilient" part, and it's a meaningfully different fault-model
choice than, say, Kafka's approach of replicating the actual data (Day 4 will make this
contrast explicit).

**DataFrame** — a distributed table with a schema, on top of the RDD execution engine.
Because the schema is known upfront, Spark's query optimizer (Catalyst) can reason about
the query the way a database optimizer does — reorder filters, prune columns, choose
join strategies — none of which is possible with an opaque RDD of Python objects.

**Dataset** — the JVM-typed version (Scala/Java only; PySpark effectively works at the
DataFrame level since Python doesn't have JVM-checked types).

```
RDD            → low-level, no schema, you write the logic          (rarely used directly today)
DataFrame      → schema known, Catalyst-optimized, Python/Scala/SQL  (what you'll use ~95% of the time)
Dataset        → DataFrame + compile-time type safety (JVM only)
```

**Lazy evaluation.** `df.filter(...).select(...)` does not run anything — it builds a
logical plan. Nothing executes until an **action** (`.collect()`, `.show()`, `.write`,
`.count()`) is called. This matters operationally: errors in a transformation chain
often only surface at the action, and Spark can optimize the *whole* chain before
running any of it (e.g., push a filter down before a join instead of after).

## 3. How It Really Works (Internals)

```
                     ┌───────────────┐
                     │    Driver     │   ← runs your main(), builds the DAG,
                     │ (SparkContext)│     schedules tasks, collects results
                     └───────┬───────┘
                             │
                   ┌─────────┴──────────┐
                   │   Cluster Manager   │  (Standalone / YARN / Kubernetes)
                   └─────────┬──────────┘
             ┌───────────────┼───────────────┐
        ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
        │Executor1│     │Executor2│     │Executor3│   ← run tasks, hold cached
        │ (JVM)   │     │ (JVM)   │     │ (JVM)   │      partitions in memory
        └─────────┘     └─────────┘     └─────────┘
```

A job is split into **stages** at every shuffle boundary (a shuffle = data needs to move
between partitions, e.g. for a `groupBy` or `join`). Each stage is split into **tasks**,
one per partition — tasks are the actual unit of scheduling onto executor cores.
Everything before the first action is just a **DAG (directed acyclic graph)** of these
stages; nothing runs until you call an action, and the DAG scheduler then works
backwards from the action to figure out what actually needs computing.

## 4. Architecture & Design Pattern Spotlight

**Pattern: lineage-based fault tolerance + lazy DAG construction.** Instead of
replicating data for durability (Kafka's approach) or checkpointing continuously
(Flink's approach), Spark trades recompute time for simplicity: lose a partition, replay
the lineage. This only works well because transformations are (mostly) deterministic —
keep that in mind before using non-deterministic UDFs in a pipeline you need to be safely
re-runnable.

## 5. Hands-On Lab

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Day1WordCount").master("local[4]").getOrCreate()

text = spark.sparkContext.textFile("/etc/hosts")  # any text file works
counts = (
    text.flatMap(lambda line: line.split())
        .map(lambda word: (word, 1))
        .reduceByKey(lambda a, b: a + b)
)
# Nothing has run yet — this is still a DAG.
for word, count in counts.take(10):
    print(word, count)   # <-- the action. THIS is when Spark actually executes.
```

Run it, then open `http://localhost:4040` (the Spark UI, live only while the job runs)
and find the DAG visualization for this job. Identify: how many stages? Where's the
shuffle boundary (hint: `reduceByKey`)?

## 6. Real-World Product Comparison

- **Databricks** was founded by Spark's original creators — the entire company is built
  on making Spark's cluster-management pain (the box above) disappear via a managed
  control plane, plus a proprietary faster execution engine (Photon).
- **Netflix and Airbnb** run Spark on top of large multi-tenant clusters for batch ETL
  and feature pipelines, typically orchestrated by Airflow, feeding a data lake
  (S3/Parquet/Iceberg) — the same shape you'll build toward in Week 2's lakehouse day.
- Contrast with **Trino/Presto**: also a distributed SQL engine with a cost-based
  optimizer, but designed for interactive federated queries across many sources rather
  than heavy multi-stage ETL — Spark and Trino often coexist in the same company for
  different jobs.

## 7. Common Production Pitfalls

- Calling `.collect()` on a large DataFrame — pulls all data to the driver's single JVM
  heap and OOMs it. (This is a distinct failure mode from the executor OOM you'll debug
  in Week 2 — driver OOM vs executor OOM have different root causes and fixes.)
- Assuming a transformation ran because no error was thrown — remember, nothing runs
  until an action.
- Using Python UDFs heavily — they force row-by-row serialization between the JVM and
  a Python process, losing most of Catalyst's optimization benefit. Prefer built-in
  `pyspark.sql.functions` where possible.

## 8. Review Questions
1. Why does Spark recompute lost partitions from lineage instead of reading a replica?
2. What specifically triggers a new stage boundary?
3. Why doesn't a Python UDF benefit from whole-stage codegen the way built-in functions do?
4. What's the practical difference between `.collect()` and `.take(10)` for a huge dataset?

## 9. Proficiency Checkpoint
If you can explain the Driver/Executor/Stage/Task hierarchy and correctly predict where
a shuffle will occur in a given chain of transformations, you're solidly at Level 2.

## Next
Day 2 goes one level deeper into the DataFrame API itself and Catalyst's optimization
passes — the "what happens between your `.filter()` call and the physical plan" story.
