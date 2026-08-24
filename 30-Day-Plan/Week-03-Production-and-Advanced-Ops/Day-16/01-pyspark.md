# Day 16: PySpark — Memory Deep-Dive Round 2: Your Real OOM Root Cause

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Using your own real executor/driver configuration numbers, calculate precisely where
the memory over-allocation occurred against your node's actual RAM.

## 2. Core Concept (basics → advanced)

Weeks 1 and 2 built every individual concept needed for this: the unified memory
model (Week 1, Day 5), executor sizing and overhead (Week 2, Day 9), and shuffle
spill (Week 2, Day 10). Today is purely applying all three together to your **actual**
incident numbers, rather than a synthetic example — turning "we had a memory
incident" into a precise, quantified root-cause explanation.

```
Full accounting for ONE executor's actual memory footprint on a node:

  spark.executor.memory              (configured JVM heap)
+ spark.executor.memoryOverhead      (JVM/off-heap/Tungsten overhead)
+ spark.executor.pyspark.memory      (separate Python process, if UDFs used)
+ any OS/other-process overhead already running on that node
──────────────────────────────────────────────────────────
= actual required physical memory for this ONE executor

× number of executors co-located on the SAME node
──────────────────────────────────────────────────────────
= actual required physical memory for the WHOLE node's Spark workload

vs. node's ACTUAL total RAM  ← the incident is precisely the gap between these two
```

## 3. How It Really Works (Internals)

The specific failure mode worth naming precisely: on a **shared single-node**
environment (your actual production setup), multiple executors (or an executor
alongside other non-Spark workloads) compete for the same finite physical RAM — Spark
itself has no visibility into what else is running on that node outside its own
configuration, so a correctly-configured *Spark-internal* memory budget can still be
wrong in absolute terms if the sum of everything actually running on the node exceeds
physical RAM. This is precisely why the calculation must include "any OS/other-process
overhead already running on that node," not just Spark's own accounting — Spark's
config values are a statement about what Spark *thinks* it needs, not a guarantee
about what's *actually available* on a shared node.

## 4. Architecture & Design Pattern Spotlight

**Pattern: unified memory model exhaustion — the gap between "correctly configured
in isolation" and "correctly sized for the actual shared environment."** This is
worth holding as a general lesson beyond Spark specifically: any resource-budgeting
calculation (Kafka cluster sizing, Day 15; ClickHouse Keeper quorum sizing, Week 1
Day 5) can be internally consistent and still wrong if it doesn't account for the
*actual* shared environment's other consumers.

## 5. Hands-On Lab

Using your actual production incident's real configuration values (executor memory,
overhead, number of executors, node RAM, and anything else known to run on that
node), fill in the full accounting table above with real numbers. Identify precisely:
- What was the calculated "required" total, using the configured values?
- What was the node's actual available RAM?
- What was the gap, and which specific term in the accounting (overhead? Python
  memory? co-located non-Spark processes? too many executors for the node?) was
  either missing or under-estimated in the original configuration?

Write this up as a short, precise root-cause paragraph — this is a directly reusable
incident-postmortem artifact for Day 21.

## 6. Real-World Product Comparison

- This exact "shared-node resource accounting" problem is why **Kubernetes'**
  resource `requests`/`limits` model (Week 1, Day 3) exists — to make exactly this
  kind of shared-node oversubscription explicit and enforced by the platform, rather
  than something each application must reason about independently.
- Managed platforms like **Databricks** reduce this risk by managing node
  allocation more centrally, at the cost of less direct visibility/control over
  exactly this kind of shared-resource accounting.

## 7. Common Production Pitfalls

- Treating a memory incident as "just add more RAM to the node" without first doing
  this precise accounting — sometimes the actual fix is correcting the configuration,
  not increasing capacity.
- Not documenting what *else* runs on a shared node when reasoning about Spark's own
  memory configuration — an incomplete accounting that omits co-located workloads.
- Fixing the immediate incident without updating the standard configuration template
  used for future jobs on the same kind of node — risking a recurrence.

## 8. Review Questions
1. Why can a Spark-internal memory configuration be self-consistent and still cause
   an OOM on a shared node?
2. What specific term is most commonly missing from a naive memory calculation?
3. Why does Kubernetes' resource model exist to address exactly this problem?
4. What should the actual fix address: configuration, node capacity, or both — and
   how would you know which, from your own numbers?

## 9. Proficiency Checkpoint
If you've produced a precise, numbers-based root-cause explanation for your own real
incident, you're at Level 3.5+ — this is genuinely production-grade incident analysis.

## Next
Day 17 covers monitoring — the Spark UI and History Server — the tools that would let
you catch this class of issue before it becomes an incident next time.
