# Day 5: PySpark — Memory Model & Caching

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain Spark's unified memory model (execution vs. storage), choose the right
`persist()` storage level for a given situation, and understand where GC pressure
actually comes from.

## 2. Core Concept (basics → advanced)

Each executor's JVM heap is split (via the **Unified Memory Manager**) into two
logical, but not rigidly separate, regions:
- **Execution memory**: working space for shuffles, joins, sorts, aggregations — needed
  *during* a computation.
- **Storage memory**: space for cached/persisted DataFrames and broadcast variables —
  needed *across* computations.

Unlike Spark's older static split, the unified model allows the two to **borrow from
each other** under memory pressure: execution can evict cached storage blocks if it
urgently needs the space (storage blocks are the cheaper thing to lose, since they can
be recomputed from lineage), and vice versa within configured limits. This dynamic
borrowing is why `.cache()` doesn't hard-reserve memory the way you might assume — a
cached DataFrame can be silently evicted under pressure and recomputed on next access,
which shows up as an unexpected slowdown rather than an error.

```
Executor JVM Heap
├── Reserved memory (small, fixed overhead)
└── Unified memory pool (spark.memory.fraction, default 60% of heap)
      ├── Execution memory  ◄──┐  can borrow from
      └── Storage memory    ───┘  each other dynamically
```

`persist()` storage levels let you choose the trade-off explicitly:
`MEMORY_ONLY` (fastest, evicted if it doesn't fit), `MEMORY_AND_DISK` (spills to disk
instead of recomputing — usually the safer default), `MEMORY_ONLY_SER` (serialized,
smaller footprint, CPU cost to deserialize on read).

## 3. How It Really Works (Internals)

Spark uses **Tungsten**, its own binary in-memory row format, specifically to avoid JVM
object overhead and reduce garbage collection pressure — a plain Java object per row
(with per-object headers, boxing of primitives, pointer chasing) is dramatically more
GC-expensive than Tungsten's compact, off-heap-friendly binary layout. This is exactly
why `.cache()`'ing a DataFrame is far cheaper, memory-wise, than the equivalent RDD of
Python/Java objects would be — the DataFrame API keeps data in Tungsten's format, an RDD
of arbitrary objects does not.

**GC overhead** becomes a real production problem specifically when: (a) too much
Storage memory is pinned by cached DataFrames that don't fit, forcing constant
eviction/recompute cycles, or (b) heavy use of Python UDFs or `.collect()`-style
operations forces materializing large numbers of actual JVM/Python objects instead of
staying in Tungsten's compact format — this is precisely the shape of the GC-overhead
errors you've hit in production during DataFrame cache operations on shared,
memory-constrained nodes.

## 4. Architecture & Design Pattern Spotlight

**Pattern: dynamic memory pool allocation with borrowing.** Rather than statically
partitioning memory (the old Spark 1.x model, and the simpler mental model most people
still assume), the unified manager treats execution and storage as **elastic pools**
that negotiate at runtime — the same general idea as an OS's dynamic page cache sizing,
or a JVM's own generational heap regions resizing under different allocation pressure.

## 5. Hands-On Lab

```python
df = spark.range(0, 20_000_000).withColumn("val", F.rand())

df.persist(StorageLevel.MEMORY_ONLY)
df.count()   # materializes the cache

df2 = spark.range(0, 20_000_000).withColumn("val", F.rand())
df2.persist(StorageLevel.MEMORY_AND_DISK)
df2.count()
```
Open the Spark UI → **Storage** tab. Compare: how much of each DataFrame actually fit
in memory (`Fraction Cached`)? For `MEMORY_ONLY`, if it doesn't fully fit, what
happens on a subsequent `.count()` — is it recomputed, and can you see that in the
**Jobs** tab (a new job appearing for supposedly "cached" data)?

## 6. Real-World Product Comparison

- **Tungsten's off-heap-friendly binary format** solves largely the same problem as
  **Flink's managed memory** (its own byte-array-based state backend, avoiding
  JVM-object GC pressure for large state) — both frameworks independently arrived at
  "don't let the JVM garbage collector see millions of small objects" as the answer.
- **Databricks' Photon engine** goes further, executing natively in C++ and sidestepping
  JVM memory/GC concerns for the execution path entirely — a different, more aggressive
  solution to the same underlying problem.

## 7. Common Production Pitfalls

- Caching a DataFrame that's larger than available Storage memory with
  `MEMORY_ONLY` — silent partial caching plus repeated recompute, often mistaken for
  "caching isn't working" rather than "caching is working, but the data doesn't fit."
- Not un-persisting DataFrames once no longer needed — they continue occupying Storage
  memory pool space for the rest of the job, directly contributing to memory pressure on
  other operations, which is a real root cause of the executor/driver over-allocation
  incident you debugged.
- Sizing executor memory without accounting for the reserved + unified-pool split — the
  usable Storage/Execution memory is meaningfully less than the raw configured executor
  memory.

## 8. Review Questions
1. Why can execution memory evict cached storage blocks, and why is that considered safe?
2. What's the practical difference between `MEMORY_ONLY` and `MEMORY_AND_DISK` when data
   doesn't fit?
3. Why does Tungsten's binary format reduce GC pressure compared to plain JVM objects?
4. How would you diagnose "silent cache eviction and recompute" from the Spark UI alone?

## 9. Proficiency Checkpoint
If you can explain why your own production GC-overhead incident happened in terms of
Storage/Execution memory pressure (not just "not enough RAM"), you're at Level 2 moving
into Level 3 — and you now have real vocabulary for that postmortem.

## Next
Day 6 covers Structured Streaming — Spark's micro-batch model — setting up the direct
Lambda/Kappa comparison with Flink's true streaming that Week 4's architecture day
revisits explicitly.
