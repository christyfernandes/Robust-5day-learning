# Day 3: PySpark — Cluster Architecture & the Shuffle

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Correctly draw the driver/cluster-manager/executor relationship, identify where a job
splits into stages, and explain precisely what a shuffle is and why it's expensive.

## 2. Core Concept (basics → advanced)

Day 1 introduced the driver/executor picture at a high level. Today: what actually
decides *when* Spark needs to move data between machines, because that's the single
biggest lever on job performance.

A **transformation** is either **narrow** (each output partition depends on exactly one
input partition — `map`, `filter`, `select`) or **wide** (each output partition may
depend on *many* input partitions — `groupBy`, `join`, `distinct`, `repartition`). Narrow
transformations can be pipelined within a single task on a single executor with zero
network I/O. Wide transformations require a **shuffle**: every executor writes its data
to disk, partitioned by the target key, and every other executor then reads the
partitions it needs over the network. This is the single most expensive operation type
in Spark — it involves disk I/O, network I/O, and serialization, all at once.

```
Narrow (map/filter):           Wide (groupBy/join) → SHUFFLE:

 P1 ─▶ P1'                      P1 ─┐         ┌─▶ P1' (needs data from ALL of P1,P2,P3)
 P2 ─▶ P2'                      P2 ─┼── disk ─┼─▶ P2' (needs data from ALL of P1,P2,P3)
 P3 ─▶ P3'                      P3 ─┘  write/ └─▶ P3' (needs data from ALL of P1,P2,P3)
                                       network
 (same executor,                       read
  no network)                   (every executor talks to every other executor)
```

## 3. How It Really Works (Internals)

The **cluster manager** (Standalone, YARN, or Kubernetes) is only responsible for one
thing: giving the driver a set of containers/processes to run executors in. It does not
know anything about Spark stages, tasks, or shuffles — that scheduling intelligence lives
entirely in the driver's **DAGScheduler** and **TaskScheduler**.

1. **DAGScheduler** walks the logical plan backwards from the action, and cuts it into
   **stages** at every shuffle boundary. Stages have a strict dependency order — stage 2
   can't start until every task in stage 1 has written its shuffle output.
2. **TaskScheduler** takes one stage at a time and schedules its **tasks** (one per
   partition) onto available executor cores, respecting data locality where possible
   (prefer running a task on the executor that already holds that partition in memory or
   on local disk).
3. Shuffle output is written to local disk on the *writing* executor (the **shuffle
   write**), registered with the driver's **MapOutputTracker**, and then pulled over the
   network by the *reading* executor (the **shuffle read**) in the next stage. This is
   why a lost executor after its shuffle write can still cause a stage recompute — the
   data is on that specific machine's local disk, not replicated.

`spark-submit --master local[4]` runs everything — driver and 4 "executor threads" — in
a single JVM process, which is why it's the right way to learn the *scheduling* concepts
without needing a real cluster: the stage/task/shuffle boundaries are identical, only the
network hop becomes a thread hand-off.

## 4. Architecture & Design Pattern Spotlight

**Pattern: master-worker with a stateless scheduling layer.** The driver (master) holds
all scheduling state; executors (workers) are simple task-execution loops with no
knowledge of the overall DAG. This is the same shape as Kubernetes' control-plane/kubelet
split and Kafka Connect's worker model — a pattern worth recognizing whenever you see
"one coordinator, many dumb executors."

## 5. Hands-On Lab

```bash
pip install pyspark --break-system-packages
spark-submit --master local[4] --conf spark.ui.enabled=true my_job.py
```

Where `my_job.py` does a `groupBy` or `join` on a DataFrame of a few hundred thousand
rows. While it's running (or from the history server after), open `http://localhost:4040`
→ **Stages** tab. Find:
- How many stages did your job get split into?
- Which stage boundary corresponds to your `groupBy`/`join`?
- Click into that stage — look at **Shuffle Read/Write** sizes. Is the shuffle size
  reasonable given your input size, or does it suggest a Cartesian product went wrong?

## 6. Real-World Product Comparison

- **Spark-on-YARN**: the traditional on-prem/Hadoop-ecosystem deployment — YARN's
  ResourceManager plays the "cluster manager" role, well-suited when Spark shares a
  cluster with other Hadoop-ecosystem tools.
- **Spark-on-Kubernetes**: each executor is a pod; this is now the default choice for new
  deployments, since it lets Spark share infrastructure and tooling (autoscaling,
  observability) with the rest of a cloud-native stack.
- **Databricks Photon**: replaces Spark's JVM-based execution engine with a native
  vectorized C++ engine for the actual task execution, while keeping the driver-side
  DAGScheduler/TaskScheduler logic conceptually the same — proof that the scheduling
  architecture and the execution engine are separable concerns.

## 7. Common Production Pitfalls

- Joining two large tables without checking for a key skew — one hot key sends a
  disproportionate amount of shuffle data to one task, and that one task becomes the
  straggler that determines your entire job's wall-clock time.
- Repeated `repartition()` calls "just in case" — each one is a full shuffle; only
  repartition when you have a specific reason (e.g., before a wide operation, or to fix
  a known skew).
- Reading the Spark UI's "duration" instead of "shuffle read/write" when diagnosing a
  slow stage — duration tells you *that* something is slow, shuffle metrics tell you *why*.

## 8. Review Questions
1. What's the precise difference between a narrow and a wide transformation?
2. Why does the cluster manager have no knowledge of "stages"?
3. If an executor dies after completing its shuffle write but before the next stage reads
   it, what has to happen?
4. Why can `local[4]` mode teach you real stage/shuffle behavior despite having no
   network?

## 9. Proficiency Checkpoint
If you can look at a job's DAG and correctly predict every shuffle boundary before
running it, you're at a strong Level 2 moving into Level 3.

## Next
Day 4 covers join strategies directly — broadcast vs. shuffle-hash vs. sort-merge — which
is where shuffle cost becomes a strategic choice rather than just something that happens
to you.
