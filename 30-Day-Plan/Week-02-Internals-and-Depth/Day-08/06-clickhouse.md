# Day 8: ClickHouse — Query Execution Internals: The Vectorized Engine

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Use `EXPLAIN PIPELINE` to see the actual vectorized execution stages of a query, and
explain why processing batches of columns beats row-at-a-time execution.

## 2. Core Concept (basics → advanced)

Day 1 introduced "columnar + vectorized" at a high level. Today: what "vectorized"
concretely means at the execution-engine level. Rather than processing one row at a
time (calling a function per row, with per-call overhead), ClickHouse's engine
processes data in **blocks** — batches of a few thousand values from a single column at
a time — and each operation (a filter, an arithmetic expression, an aggregation step)
is implemented to operate on an entire block at once, often using **SIMD** (Single
Instruction, Multiple Data) CPU instructions that apply the same operation to multiple
values in a single CPU cycle.

```
Row-at-a-time (a plain OLTP-style engine):
  for each row: evaluate WHERE price > 100  (one comparison, one function call, per row)

Vectorized, block-at-a-time (ClickHouse):
  load a BLOCK of, say, 65536 `price` values into a contiguous array
  apply ONE SIMD comparison instruction across many values simultaneously
  (far fewer function calls; far better CPU cache utilization; the CPU's
   branch predictor isn't fighting per-row conditional branching)
```

## 3. How It Really Works (Internals)

The **query pipeline** (visible via `EXPLAIN PIPELINE`) is a graph of processing stages
— each stage pulls a block from the stage before it, transforms it, and pushes a block
to the next stage; stages can run in parallel across multiple CPU cores (ClickHouse
aggressively parallelizes within a single query across cores, not just across nodes).
This block-based pipeline is precisely why ClickHouse can saturate modern many-core
CPUs so effectively on analytical queries: each core processes its own stream of
blocks largely independently, only synchronizing at genuine merge points (like a final
`GROUP BY` merge across per-core partial aggregates).

This connects directly to Day 3's sparse-index lesson: the sparse index decides *which
granules* to read; the vectorized engine decides *how efficiently* those granules, once
read, are actually processed — two separate but complementary performance mechanisms.

## 4. Architecture & Design Pattern Spotlight

**Pattern: batch-of-columns (vectorized) processing — solving the same "avoid
row-at-a-time overhead" problem as Spark's Tungsten whole-stage codegen (today's
PySpark lesson), via a different mechanism.** Spark generates and JIT-compiles fused
code per query; ClickHouse instead has a fixed, highly-optimized set of vectorized
operators that process any query's blocks efficiently without per-query code
generation. Both are legitimate, widely-adopted answers to the identical underlying
performance problem — worth being able to name both, and their trade-offs, explicitly.

## 5. Hands-On Lab

```sql
EXPLAIN PIPELINE
SELECT org_id, count() FROM events WHERE event_type = 'purchase' GROUP BY org_id;
```
Read the output — identify the parallel processing stages (often shown as multiple
identical branches, one per CPU core assigned to the query) and the final merge stage
where per-core partial `GROUP BY` results are combined. Compare the pipeline for a
simple `SELECT count()` (no `GROUP BY`) against today's query, and note how much
simpler the pipeline becomes without a grouping key to partition work by.

## 6. Real-World Product Comparison

- **DuckDB** (an increasingly popular embedded analytical engine) uses a very similar
  vectorized execution model — the general vectorized-engine approach isn't unique to
  ClickHouse, but a broader OLAP-engine design philosophy shared across the category.
- Contrast directly with **Spark's Tungsten codegen** (today's PySpark lesson): compiled
  fused code vs. fixed vectorized operators — genuinely different engineering
  philosophies converging on the same performance goal.

## 7. Common Production Pitfalls

- Writing queries with per-row scalar UDFs (custom functions not implemented in a
  vectorized-friendly way) — can defeat the vectorization benefit for that part of the
  query, similar to how a Python UDF defeats Spark's codegen.
- Assuming vectorization alone solves performance regardless of query design — a poor
  `ORDER BY`/sharding key choice (Days 3-4, Week 1) still forces scanning far more data
  than necessary, and vectorization only makes that unnecessary scan faster, not
  unnecessary.
- Not accounting for how many CPU cores a query actually gets to parallelize across
  when reasoning about expected performance — under concurrent query load, per-query
  parallelism is naturally reduced.

## 8. Review Questions
1. What specifically does "vectorized" mean at the execution level?
2. Why does block-at-a-time processing improve CPU cache utilization compared to
   row-at-a-time?
3. How do ClickHouse's vectorized engine and Spark's Tungsten codegen solve the same
   problem differently?
4. Why doesn't vectorization alone compensate for a poorly chosen `ORDER BY` key?

## 9. Proficiency Checkpoint
If you can read a real `EXPLAIN PIPELINE` output and explain the parallel/merge
structure it shows, you're at Level 3.

## Next
Day 9 tackles the JOIN fan-out problem directly — your live production issue,
now with the vectorized execution model as context for why it happens.
