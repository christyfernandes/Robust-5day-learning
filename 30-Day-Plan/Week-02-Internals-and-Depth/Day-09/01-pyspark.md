# Day 9: PySpark — Executor Sizing & Dynamic Allocation

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Calculate correct executor-memory and overhead settings for a given node's total RAM —
directly applicable to your shared single-node production setup.

## 2. Core Concept (basics → advanced)

Every executor's actual memory footprint is **more** than just `spark.executor.memory`
— it also needs **overhead memory** (for JVM internals, off-heap allocations, and
anything Tungsten allocates outside the regular heap), controlled by
`spark.executor.memoryOverhead` (default: max of 384MB or 10% of executor memory).

```
Total memory an executor actually needs on a node:

  spark.executor.memory  (the JVM heap you configure)
  + spark.executor.memoryOverhead  (JVM/off-heap/Tungsten overhead)
  + spark.executor.pyspark.memory (if using Python UDFs — a SEPARATE Python process's
                                    memory, not shared with the JVM heap at all)
  ─────────────────────────────────────────────────
  = actual memory the node must have available for ONE executor
```

On a **shared single node**, the classic mistake: sizing multiple executors' configured
memory to sum to the node's total RAM, while forgetting overhead and Python-process
memory are *additional* — the node then runs out of actual physical memory even though
the sum of `spark.executor.memory` values looked correct on paper. This is precisely
the shape of the executor/driver memory over-allocation incident.

## 3. How It Really Works (Internals)

**Dynamic allocation** (`spark.dynamicAllocation.enabled=true`) lets Spark add/remove
executors during a job's lifetime based on actual pending-task backlog, rather than
requiring a fixed executor count decided upfront — genuinely useful for workloads with
uneven stage-to-stage resource needs, but it interacts with cluster-manager scheduling
(YARN's capacity scheduler queues, or Kubernetes' pod scheduling and resource
requests/limits) in ways that matter operationally: a Spark job requesting more
executors than the cluster manager can currently grant doesn't fail — it just waits,
which can look like a "stuck" job rather than an explicit resource error.

The **driver** also needs correct sizing, independently from executors —
`spark.driver.memory` plus its own overhead — and a driver OOM (from, e.g., a
`.collect()` pulling too much data, Day 3's pitfall) is a categorically different
failure from an executor OOM, even though both show up as "the job died with an OOM."

## 4. Architecture & Design Pattern Spotlight

**Pattern: resource pooling / bin-packing under a scheduler.** Both YARN's capacity
scheduler and Kubernetes' pod scheduler are solving the same bin-packing problem —
fitting variably-sized resource requests into available node capacity — with different
allocation philosophies (YARN's hierarchical queues with guaranteed minimums vs.
Kubernetes' request/limit model with the kubelet enforcing cgroup-based isolation).
Understanding executor sizing as "a bin-packing request to a scheduler," not just "a
Spark config," reframes memory-tuning incidents as a scheduling problem with a
Spark-specific vocabulary.

## 5. Hands-On Lab

Given a node with **32GB total RAM**, shared with other workloads that need a reserved
8GB, calculate a safe executor configuration:
```
Available for Spark: 32GB - 8GB (reserved) = 24GB

If running 3 executors on this node:
  Per-executor budget: 24GB / 3 = 8GB
  memoryOverhead (10%): ~800MB
  → spark.executor.memory should be set to LEAVE ROOM for overhead:
    spark.executor.memory = 7g   (NOT 8g — that leaves no room for the ~800MB overhead)
    spark.executor.memoryOverhead = 800m
```
Do this calculation for your actual shared node's real RAM and reserved-workload
figures, and compare against whatever configuration caused your real
over-allocation incident — identify precisely which term (overhead? Python
memory? driver memory on the same node?) was missing from the original math.

## 6. Real-World Product Comparison

- **Kubernetes'** resource `requests`/`limits` model is now the more common target for
  new Spark deployments (Spark-on-K8s, Day 3) — and it makes the overhead-memory
  omission mistake even more visible, since a pod that exceeds its memory `limit` gets
  OOM-killed by the kubelet directly, a sharper failure signal than YARN's more
  forgiving container memory enforcement in some configurations.
- **Databricks** autoscaling and cluster-sizing recommendations bake in overhead
  calculations automatically — part of what a managed platform is selling: not having
  to do this arithmetic by hand, at the cost of less direct control over it.

## 7. Common Production Pitfalls

- Sizing `spark.executor.memory` to consume 100% of a node's per-executor budget,
  leaving no room for `memoryOverhead` — the exact root cause pattern behind memory
  over-allocation incidents on shared nodes.
- Forgetting that Python UDF-heavy workloads need `spark.executor.pyspark.memory`
  budgeted *separately* — this memory lives in independent Python worker processes, not
  inside the JVM heap you sized for `spark.executor.memory`.
- Not distinguishing driver OOM from executor OOM when triaging — different causes
  (usually `.collect()`/broadcast-related for the driver; usually data skew/caching for
  executors), different fixes.

## 8. Review Questions
1. What three separate memory budgets does a Python-UDF-heavy executor actually need?
2. Why does leaving no room for `memoryOverhead` cause problems that only appear under
   real load, not in testing?
3. Why is a driver OOM a categorically different failure from an executor OOM?
4. How does Kubernetes' resource enforcement make an overhead-memory miscalculation
   more immediately visible than some YARN configurations would?

## 9. Proficiency Checkpoint
If you can correctly calculate safe executor memory settings for a real, shared node
and explain each component of the calculation, you're at Level 3 — and you now have a
real root-cause framework for your own production incident.

## Next
Day 10 covers shuffle internals — external spill to disk — directly relevant to your
disk-space-at-87% concern.
