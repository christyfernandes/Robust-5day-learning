# Day 13: Flink — Scaling: Parallelism, Slots & Reactive Mode

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Rescale a running job from a savepoint at a different parallelism, and explain the
relationship between parallelism, task slots, and elastic/reactive scaling.

## 2. Core Concept (basics → advanced)

**Parallelism** is how many parallel instances of each operator a job runs (e.g.,
parallelism=4 means 4 parallel copies of each operator, each handling roughly 1/4 of
the keyspace for keyed operations). **Task slots** are the actual resource unit a
TaskManager offers — each TaskManager is configured with some number of slots, and a
job's total parallelism must fit within the cluster's total available slots.

```
TaskManager 1: [slot][slot][slot][slot]    ← 4 slots
TaskManager 2: [slot][slot][slot][slot]    ← 4 slots
                                             = 8 total slots available

Job with parallelism=8 → uses exactly all 8 slots, one operator-instance per slot
Job with parallelism=4 → uses only 4 of the 8 available slots
```

Historically, changing a running job's parallelism required stopping it (with a
**savepoint** — a manually-triggered, portable checkpoint, Week 1 Day 6), then
restarting it from that savepoint with a new parallelism configuration — Flink
redistributes keyed state across the new number of parallel instances automatically
during this restart, based on key groups.

## 3. How It Really Works (Internals)

**Reactive mode** (and the Kubernetes Operator's autoscaling built on top of it)
removes the manual stop-and-restart step: the job automatically adjusts its
parallelism to match currently available task slots as the underlying cluster scales
up or down (e.g., via Kubernetes horizontal pod autoscaling adding/removing
TaskManager pods) — the job reacts to available resources rather than requiring an
explicit, deliberate rescale operation.

Under the hood, rescaling (manual or reactive) relies on Flink's **key-group**
mechanism: keyed state (Week 1, Day 5) isn't assigned directly to a specific parallel
instance number, but to one of a fixed, larger number of key groups, which are then
distributed across however many parallel instances currently exist — this
indirection is exactly what makes state redistribution during a parallelism change
possible without needing to know the new parallelism in advance when the state was
originally written.

## 4. Architecture & Design Pattern Spotlight

**Pattern: elastic scaling of a stateful stream job, enabled by an indirection layer
(key groups) between logical state ownership and physical parallel-instance
assignment.** This same "add an indirection layer to enable elastic reassignment"
idea appears in Kafka Cluster's fixed hash slots (Week 2, Day 10) and consistent
hashing generally (Week 1, Day 3) — a recurring solution whenever a system needs to
support changing its degree of parallelism/distribution without a full data reshuffle
tied to the exact old/new instance counts.

## 5. Hands-On Lab

```bash
# trigger a savepoint for a running job
flink savepoint <job-id> file:///tmp/flink-savepoints

# stop the job, then restart from the savepoint at a DIFFERENT parallelism
flink run -s file:///tmp/flink-savepoints/savepoint-xxxx \
  -p 8 \
  your_job.py
```
Run a stateful job (e.g., a running count) at parallelism=4, produce some events,
trigger a savepoint, then restart at parallelism=8 from that savepoint. Verify the
running counts are correct and continuous (not reset), confirming state was
correctly redistributed across the new parallelism.

## 6. Real-World Product Comparison

- The **Flink Kubernetes Operator**'s autoscaler builds directly on Reactive Mode,
  using observed backpressure/utilization metrics (Day 11's backpressure lesson) to
  decide when to scale parallelism up or down automatically — a concrete example of
  multiple weeks' concepts (backpressure monitoring, state redistribution) composing
  into one operational capability.
- Contrast with **Spark's dynamic allocation** (Week 2, Day 9) — conceptually similar
  goal (elastic resource use) but a different mechanism, since Spark's batch/micro-
  batch execution model doesn't carry the same continuously-running keyed-state
  redistribution challenge that true streaming rescaling does.

## 7. Common Production Pitfalls

- Manually rescaling without taking a savepoint first — restarting from an automatic
  checkpoint at a different parallelism is not guaranteed to be supported the same way
  savepoints are designed to be.
- Enabling reactive/autoscaling without understanding its interaction with
  checkpointing overhead — frequent rescaling events each involve a state
  redistribution cost, and overly aggressive autoscaling thresholds can cause
  thrashing.
- Assuming rescaling is instantaneous — state redistribution takes real time
  proportional to state size, a practical consideration for how quickly autoscaling
  can actually respond to a load spike.

## 8. Review Questions
1. What's the practical relationship between parallelism and task slots?
2. Why does the key-group indirection make state redistribution possible during a
   rescale?
3. How does Reactive Mode remove the need for a manual stop-and-restart cycle?
4. Why isn't rescaling instantaneous, even with reactive/autoscaling enabled?

## 9. Proficiency Checkpoint
If you can rescale a real stateful job from a savepoint and explain why state
redistribution works correctly, you're at Level 3.

## Next
Day 14 is this week's integrated lab and review, applying everything from Week 2
directly to your real production systems.
