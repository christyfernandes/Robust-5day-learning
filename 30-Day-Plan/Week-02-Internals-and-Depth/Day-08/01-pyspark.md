# Day 8: PySpark — Catalyst + Tungsten: Whole-Stage Codegen

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Read `.explain(mode="codegen")` output for a simple job and explain what whole-stage
code generation actually eliminates compared to naive row-at-a-time execution.

## 2. Core Concept (basics → advanced)

Day 1 introduced Catalyst's four-phase optimization pipeline (unresolved → resolved →
optimized logical → physical plan). Today's question is what happens *after* a physical
plan is chosen: how does Spark actually execute it efficiently?

Naive execution would call a `next()`-style iterator function per operator, per row —
for a chain of `filter → project → aggregate`, that's three virtual function calls per
row, each with its own overhead (this is exactly how the classic "Volcano" query
execution model works, and it's simple but slow at scale). **Whole-stage code
generation** instead *fuses* a whole chain of operators into a single generated Java
function, compiled at runtime — collapsing what would be three virtual calls per row
into inlined code with no per-operator function-call overhead at all.

```
Naive (Volcano model):        Whole-stage codegen:

for row in filter_iter():       // ONE generated function, JIT-compiled:
    for row in project_iter():  for (row : input) {
        for row in agg_iter():      if (predicate(row)) {          // filter, inlined
            ...                        val = project(row)          // project, inlined
                                       agg.update(val)              // aggregate, inlined
(3 virtual calls PER ROW)          }
                                 }
```

## 3. How It Really Works (Internals)

Not every operator can be fused this way — operators that need a full shuffle
(Day 3's wide transformations) are natural fusion boundaries, since data has to leave
the current executor. Within a stage (between shuffle boundaries), though, Catalyst's
`WholeStageCodegenExec` generates actual Java source code for the fused chain of
operators, compiles it via Janino (a lightweight in-memory Java compiler) at runtime,
and executes the compiled bytecode — genuinely no different, performance-wise, from
hand-written Java for that specific chain of operations.

This is also where Tungsten's binary row format (Day 5) pays off directly: generated
code operates on Tungsten's compact in-memory representation, avoiding JVM object
overhead and enabling better CPU cache utilization (processing data that's laid out
densely in memory, rather than scattered objects with pointer-chasing) — the codegen
and the binary format are two halves of the same performance strategy, not independent
optimizations.

## 4. Architecture & Design Pattern Spotlight

**Pattern: JIT-compiled, fused batch processing — the general strategy of "generate
specialized code for this specific query, on the fly" instead of interpreting a generic
plan.** This is the exact same philosophy as ClickHouse's vectorized execution (today's
ClickHouse lesson) and modern JIT-compiled database engines generally — both reject
generic, interpreted per-row execution in favor of specialized, compiled execution paths
built for the query at hand.

## 5. Hands-On Lab

```python
df = spark.range(0, 10_000_000).withColumn("val", F.col("id") * 2)
result = df.filter(F.col("val") > 1000).groupBy((F.col("id") % 10)).count()
result.explain(mode="codegen")
```
Read the output — find the `WholeStageCodegen` markers wrapping the filter and
aggregate. Now force a shuffle boundary by adding a `.repartition()` before the
`groupBy`, and re-run `.explain(mode="codegen")` — notice the codegen boundary
now falls exactly at the shuffle.

## 6. Real-World Product Comparison

- **ClickHouse's vectorized engine** (today's ClickHouse lesson) achieves a similar
  goal — avoid slow, generic per-row interpretation — via a different mechanism
  (batch-of-columns SIMD processing rather than runtime-compiled fused code). Both are
  legitimate, widely-used answers to the same underlying performance problem.
- **Databricks Photon** goes a step further, replacing the JVM-based codegen path
  entirely with a native, vectorized C++ execution engine — Photon and Tungsten
  codegen are two different generations of the same underlying goal.

## 7. Common Production Pitfalls

- Writing Python UDFs for logic that could be expressed in built-in
  `pyspark.sql.functions` — Python UDFs are opaque to Catalyst and *cannot* be fused
  into generated code, forcing a much slower row-by-row JVM↔Python round trip for every
  single row.
- Assuming codegen applies uniformly regardless of query shape — very wide `SELECT`
  statements (hundreds of columns) or deeply nested expressions can hit codegen size
  limits and silently fall back to the slower interpreted path.
- Not recognizing a shuffle boundary as a codegen boundary — expecting fusion across a
  shuffle, which structurally cannot happen.

## 8. Review Questions
1. What specifically does whole-stage codegen eliminate compared to the Volcano model?
2. Why can't a Python UDF be fused into generated code?
3. Why does a shuffle boundary also become a codegen boundary?
4. How do Tungsten's binary format and codegen complement each other?

## 9. Proficiency Checkpoint
If you can read real `codegen`-mode explain output and correctly identify fusion
boundaries and why they occur there, you're at Level 3.

## Next
Day 9 covers executor sizing and dynamic allocation — directly relevant to your shared
single-node production setup.
