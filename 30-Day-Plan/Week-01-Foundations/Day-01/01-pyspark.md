# Day 1: PySpark — Distributed Compute Foundations

## Time: ~30 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain why Spark exists (what it fixed about MapReduce), correctly describe the
RDD → DataFrame → Dataset relationship, and run a first job while being able to name
what "lazy evaluation" actually defers.

## 2. Core Concept (basics → advanced)

**Start here if Spark is genuinely new to you.** Spark is a system for running
computations across many machines at once, instead of one. You write code that looks
almost like normal Python/Pandas code operating on a table of data, but behind the
scenes that table is split into pieces (called **partitions**) and spread across
multiple machines (called **nodes**) working together as a **cluster** — the whole
point is that a computation too big or too slow for one machine's memory/CPU can
finish in a reasonable time by splitting the work across many machines in parallel.

**The problem Spark solved.** Before Spark, the dominant tool for this was Hadoop
MapReduce. MapReduce split work into two phases (map, then reduce) and wrote the
intermediate results **to disk** between every phase — reliable, but disk is slow
(orders of magnitude slower than RAM). For a computation with many steps chained
together (common in ETL pipelines, and essential for iterative algorithms like machine
learning training, which repeats the same computation many times over), that meant
paying disk-write/disk-read cost over and over for data that could easily have stayed
in memory the whole time. Spark's core idea: keep intermediate data **in memory**
across steps by default, and only spill to disk when memory actually runs out or you
explicitly ask for durability. This is the single biggest reason Spark is faster than
MapReduce for multi-step workloads.

**RDD (Resilient Distributed Dataset)** — Spark's original, foundational data
abstraction. In plain terms: an RDD is "a collection of data, split into partitions,
spread across the cluster, that Spark knows how to rebuild if a piece is lost." Two
words worth unpacking:
- **Immutable**: once created, an RDD's data never changes in place. Every
  transformation (like `.filter()`) produces a brand-new RDD rather than modifying the
  old one — this sounds wasteful, but it's exactly what makes the next point possible.
- **Resilient (via lineage)**: instead of protecting against data loss by keeping
  duplicate copies of the actual data (the way Kafka replicates messages to multiple
  brokers, Week 1 Day 4), Spark keeps a recipe — called **lineage** — of every
  transformation that produced this RDD from its original source. If a machine dies
  and a partition is lost, Spark doesn't need a backup copy; it just re-runs the
  recipe for that one missing partition. This only works because the recipe steps are
  (usually) deterministic — run the same transformation on the same input, get the
  same output, every time.

**DataFrame** — a distributed table *with a schema* (named, typed columns — think of
it like a spreadsheet or a SQL table, not a bag of arbitrary Python objects), built on
top of the same RDD engine underneath. Because Spark knows the schema upfront, its
query optimizer (called **Catalyst**, covered in depth on Day 2) can reason about your
query the way a database optimizer reasons about SQL — deciding to check a cheap
filter before an expensive join, skipping columns you never asked for, and more —
none of which is possible with a plain RDD of opaque Python objects, since Spark has
no way to look inside them.

**Dataset** — the JVM-typed version of a DataFrame (Scala/Java only). Python has no
compile-time type checking the way the JVM does, so in PySpark you work at the
DataFrame level essentially all the time; "Dataset" is worth knowing by name but you
won't touch it directly in this track.

```
RDD            → low-level, no schema, you write all the logic     (rarely used directly today)
DataFrame      → schema known, Catalyst-optimized, Python/Scala/SQL (what you'll use ~95% of the time)
Dataset        → DataFrame + compile-time type safety                (JVM only — Scala/Java)
```

**Lazy evaluation.** In plain terms: when you write `df.filter(...).select(...)`,
Spark does **not** run either of those operations yet. It just writes down a plan —
"eventually, do a filter, then a select" — the same way writing a recipe down isn't
the same as cooking the meal. Nothing actually executes until you call an **action**
(`.collect()`, `.show()`, `.write`, `.count()`, `.take()`) — think of the action as the
moment you actually start cooking. This matters in two very practical ways: (1) errors
inside a transformation often only surface when the action finally runs, which can be
confusing the first time it happens — you'll see the error "later" than you expected;
and (2) because Spark sees your *whole* recipe before running any of it, it can
reorder and optimize the entire chain first (e.g., doing a cheap filter before an
expensive join instead of after, even if you wrote the filter second) — this
optimization step is exactly what Day 2 covers in depth.

## 3. How It Really Works (Internals)

There are actually **two separate hierarchies** here, and conflating them is a common
source of confusion — one is about the physical machines/processes doing the work,
the other is about how Spark breaks your logical computation into schedulable pieces.

**Hierarchy 1 — the infrastructure (the "who"):**

```
                     ┌───────────────┐
                     │    Driver     │   ← runs your main() / notebook code, builds the
                     │ (SparkContext)│     plan, schedules work, collects final results
                     └───────┬───────┘
                             │
                   ┌─────────┴──────────┐
                   │   Cluster Manager   │  (Standalone / YARN / Kubernetes — decides
                   └─────────┬──────────┘   WHICH machines the executors run on)
             ┌───────────────┼───────────────┐
        ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
        │Executor1│     │Executor2│     │Executor3│   ← separate JVM processes that
        │ (JVM)   │     │ (JVM)   │     │ (JVM)   │      actually run the work and
        └─────────┘     └─────────┘     └─────────┘      hold cached data in memory
```

The **Driver** is the one process running your actual Python script — it never
processes your data itself; its job is to plan, coordinate, and collect small final
results. **Executors** are separate worker processes (JVMs), possibly on different
physical machines, that do the real data processing. The **Cluster Manager** is a
separate service whose only job is deciding which physical machines get to run
executors — it has no idea what a "shuffle" or a "stage" is; that's a layer above it.

**Hierarchy 2 — the work breakdown (the "what," created fresh every time an action runs):**

```
Application (your whole spark-submit run / notebook session)
   └── Job            ← ONE per action call (.collect(), .count(), .write(), ...)
         └── Stage     ← a job is split into stages at every SHUFFLE boundary
               └── Task ← a stage is split into tasks, ONE PER PARTITION —
                           tasks are the actual unit that gets scheduled onto
                           an executor's CPU core
```

A **shuffle** is what happens when data needs to physically move between partitions
to be regrouped — for example, `groupBy` needs every row with the same key to end up
together, even though those rows started out scattered across different partitions on
different machines, so data has to be written out, redistributed over the network, and
read back in on the correct side. Operations that need this (`groupBy`, `join`,
`distinct`, `repartition`, `reduceByKey`, `sortBy`) are called **wide** transformations,
and each one creates a new stage boundary. Operations that don't need this
(`filter`, `map`, `select`, `flatMap`) are called **narrow** transformations — Spark
can run a whole chain of them back-to-back on one partition, on one executor, with zero
network movement, so they get bundled into the *same* stage rather than creating new
ones.

**The rule for predicting a shuffle, stated plainly:** look at your chain of
transformations one at a time. Every time you hit `groupBy`, `join`, `distinct`,
`repartition`, `reduceByKey`, or `sortBy`, that's a new stage boundary. Everything
between two such operations (or before the first one, or after the last one) is one
stage.

## 4. Architecture & Design Pattern Spotlight

**Pattern: lineage-based fault tolerance + lazy DAG construction.** Instead of
replicating data for durability (Kafka's approach) or checkpointing continuously
(Flink's approach), Spark trades recompute time for simplicity: lose a partition,
replay the lineage. This only works well because transformations are (mostly)
deterministic — keep that in mind before using non-deterministic UDFs in a pipeline
you need to be safely re-runnable.

## 5. Hands-On Lab

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Day1WordCount")
    .master("local[4]")   # 4 worker threads, all on this one machine — no real
    .getOrCreate()          # cluster needed to learn the concepts below

)
sc = spark.sparkContext

# A small, self-contained text sample (repeated, so counts are meaningful) —
# deliberately NOT reading a system file like /etc/hosts, since that path doesn't
# exist on every OS and its content varies machine to machine.
sample_text = """
the quick brown fox jumps over the lazy dog
the dog barks at the fox
the fox runs away from the dog
spark processes data across a cluster of machines
spark uses a directed acyclic graph to plan work
the driver builds the plan the executors run the tasks
""".strip()

lines = (sample_text + "\n") * 60   # repeat to get a non-trivial word count
text_rdd = sc.parallelize(lines.strip().split("\n"), numSlices=4)  # 4 partitions

counts = (
    text_rdd.flatMap(lambda line: line.split())   # narrow: one line -> many words
            .map(lambda word: (word, 1))          # narrow: word -> (word, 1)
            .reduceByKey(lambda a, b: a + b)       # WIDE — this is the shuffle
)
# Nothing has run yet — everything above is still just a plan (a DAG).

top_words = counts.takeOrdered(10, key=lambda pair: -pair[1])  # <-- the ACTION
for word, count in top_words:
    print(f"{word}: {count}")
```

Run it, then open `http://localhost:4040` (the Spark UI — only reachable *while the
script is still running*; it disappears the instant `spark.stop()` runs or the script
exits, which is a common first-time gotcha if your script finishes too fast to click
into it — add a `input("press enter to exit...")` right before the end if you want
time to look around). Click the **Jobs** tab, then into the one job, then the
**Stages** tab.

### Sample Output

Running the script prints the actual word counts to your terminal — this part is
deterministic, so you should see exactly this:

```
the: 600
fox: 180
dog: 180
plan: 120
spark: 120
a: 120
quick: 60
barks: 60
at: 60
runs: 60
```

And the **Stages** tab of the Spark UI will show something shaped like this (exact
timings will differ run to run — the pattern is what matters):

```
Stage Id  Description                          Tasks: Succeeded/Total  Shuffle Read  Shuffle Write
1         takeOrdered at day1_job.py:29          4/4                    ~1.2 KB
0         reduceByKey at day1_job.py:23           4/4                                  ~1.2 KB
```

Reading this line by line:
- **Two stages total (Stage 0 and Stage 1), not one.** That's your shuffle boundary
  made visible — count the stages, subtract one, and that's roughly how many wide
  transformations ran (here: exactly one, `reduceByKey`).
- **Stage 0** covers everything from `parallelize` through `flatMap`, `map`, and the
  *local* half of `reduceByKey` (each partition first combines its own matching keys
  before anything moves across the network — an optimization called a "map-side
  combine"). It ends with a **Shuffle Write**: each of the 4 tasks writes its
  partially-combined key/count pairs to local disk, organized by which downstream
  partition will need them.
- **Stage 1** can't start until *every* Stage 0 task finishes writing — it needs data
  from all of them. Its **Shuffle Read** is exactly Stage 0's Shuffle Write: each Stage
  1 task pulls the pieces relevant to it from every Stage 0 task, finishes combining
  matching keys (now that they're finally co-located), computes the local top-10 via
  `takeOrdered`, and sends that small final result back to the Driver.
- **Tasks: Succeeded/Total shows 4/4 in both stages** — that's the partition count
  (`numSlices=4`) made visible: exactly one task per partition, per stage.
- Notice there's **no third stage**. `takeOrdered` is an action, and actions gather a
  final result back to the Driver — they don't automatically create a new stage on
  their own the way a `groupBy` or `join` does.

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
<details><summary>Show answer</summary>

Because Spark bets that recomputing a lost partition (replaying a deterministic chain
of transformations) is cheaper overall than the storage and network cost of keeping
duplicate copies of every partition, the way Kafka replicates every message to
multiple brokers. This trade only holds because transformations are (mostly)
deterministic — the same input always produces the same output, so "replay the
recipe" reliably reconstructs exactly what was lost.

</details>

2. What specifically triggers a new stage boundary?
<details><summary>Show answer</summary>

A wide transformation — any operation where the output partitions need data gathered
from *multiple* input partitions, requiring a shuffle (data physically moving across
the network/disk to be regrouped). Concretely: `groupBy`, `join`, `distinct`,
`repartition`, `reduceByKey`, `sortBy`. Narrow transformations (`map`, `filter`,
`select`, `flatMap`) never trigger a new stage — Spark fuses them into whichever
stage is already running.

</details>

3. Why doesn't a Python UDF benefit from whole-stage codegen the way built-in functions do?
<details><summary>Show answer</summary>

Whole-stage codegen (covered in depth in Week 2) works by having Catalyst generate
optimized JVM bytecode for a chain of operations it fully understands. A Python UDF
is an opaque black box to Catalyst — it has no idea what's inside your Python
function, so it can't fuse it into generated code. Instead, every row has to be
serialized out of the JVM, handed to a separate Python process to run your function,
and the result serialized back — a real, measurable per-row tax that built-in
`pyspark.sql.functions` never pay, since those run natively inside the JVM where
Catalyst can see and optimize them.

</details>

4. What's the practical difference between `.collect()` and `.take(10)` for a huge dataset?
<details><summary>Show answer</summary>

`.collect()` pulls **every** row in the entire (possibly huge) distributed dataset
back to the single Driver process's memory — for a genuinely large dataset this can
easily exceed the Driver's JVM heap and crash it (a driver OOM). `.take(10)` (or
`takeOrdered`) only pulls a small, bounded number of rows back, and Spark is smart
enough to try to compute just enough partitions to satisfy that small request rather
than processing the whole dataset when it can avoid it — dramatically safer for
exploring a large dataset.

</details>

## 9. Proficiency Checkpoint

**Quick Recap:**
- **Driver** = the one process running your script; plans and coordinates, never
  touches your actual data directly.
- **Executor** = a separate JVM worker process that does the real data processing and
  holds cached partitions in memory; there are usually several, often on different
  machines.
- **Cluster Manager** = decides which physical machines executors run on; has zero
  awareness of stages/tasks/shuffles.
- **Job** = created once per action call (`.collect()`, `.count()`, `.write()`, ...).
- **Stage** = a job split apart at every shuffle (wide-transformation) boundary.
- **Task** = a stage split apart into one unit per partition — the actual thing
  scheduled onto an executor's core.
- **Shuffle-triggering rule**: `groupBy`, `join`, `distinct`, `repartition`,
  `reduceByKey`, `sortBy` → new stage. `map`, `filter`, `select`, `flatMap` → same stage.

If you can explain the Driver/Executor/Job/Stage/Task hierarchy — including which two
of those are physical processes and which three are logical work units — and
correctly predict where a shuffle will occur in a given chain of transformations,
you're solidly at Level 2.

## Next
Day 2 goes one level deeper into the DataFrame API itself and Catalyst's optimization
passes — the "what happens between your `.filter()` call and the physical plan" story.
