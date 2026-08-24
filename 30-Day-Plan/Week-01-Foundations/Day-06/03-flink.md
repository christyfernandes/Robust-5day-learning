# Day 6: Flink — Checkpointing (Chandy-Lamport)

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Enable checkpointing, kill a TaskManager mid-job, and verify recovery from the last
checkpoint — the exact mechanism behind real JobManager instability debugging.

## 2. Core Concept (basics → advanced)

Flink needs a way to take a **globally consistent snapshot** of a running job's entire
state (every operator's state, plus its exact position in every input stream) without
stopping the world — pausing every operator across a whole cluster to synchronize
would be prohibitively slow at any real scale.

The answer is the **Chandy-Lamport algorithm** (adapted as Flink's checkpointing
mechanism): special **checkpoint barrier** records are injected into the stream at the
sources, and flow downstream *alongside* regular data, in-order. When an operator
receives a barrier on **all** of its input channels, it snapshots its own current state,
forwards the barrier downstream, and continues processing. Because barriers flow
in-order with the data they logically precede, every operator's snapshot corresponds to
"state as of exactly this point in each input stream" — consistent across the whole
job, without ever pausing computation.

```
Source ──▶ [barrier] ──▶ Operator A ──▶ [barrier] ──▶ Operator B ──▶ [barrier] ──▶ Sink
              │                            │                            │
        A snapshots state           B snapshots state            Sink snapshots
        the instant it sees         the instant it's received     state; checkpoint
        the barrier, then           barriers on ALL its inputs     is complete once
        forwards it                 (alignment)                   every operator acks
```

## 3. How It Really Works (Internals)

For operators with **multiple input channels** (e.g., a `keyBy` result being consumed
by a downstream join), the operator must wait for the barrier to arrive on *every*
input channel before it can snapshot — this is **barrier alignment**, and it's exactly
where checkpoint duration can blow up if one input channel is slow or backed up: the
operator buffers data from the channels that already delivered their barrier while
waiting for the slow one, and that buffering is itself a real memory/latency cost.
**Unaligned checkpointing** (an optimization) instead lets the operator snapshot
immediately on the *first* barrier received, treating any not-yet-arrived in-flight
data as part of the state to be snapshotted directly — trading larger checkpoint
size for dramatically reduced checkpoint duration under backpressure. This directly
matters to your real production debugging: a JobManager repeatedly failing to complete
checkpoints, and consumer lag piling up, is exactly the symptom of barrier alignment
stalling behind a backpressured operator.

A **savepoint** is a manually-triggered, more portable checkpoint — used for
deliberate operations like upgrading job code or rescaling parallelism, whereas
checkpoints are the automatic, periodic fault-tolerance mechanism.

## 4. Architecture & Design Pattern Spotlight

**Pattern: distributed consistent snapshot via marker-based barrier propagation.** This
is a genuinely elegant, specific algorithm (not just "periodically save state") worth
knowing by name — Chandy-Lamport's core insight (markers flowing in-band with the data
they logically bound) recurs conceptually anywhere a distributed system needs a
consistent global snapshot without a stop-the-world pause.

## 5. Hands-On Lab

```python
env.enable_checkpointing(10000)  # every 10 seconds
env.get_checkpoint_config().set_checkpoint_storage_dir("file:///tmp/flink-checkpoints")
```
Run a simple stateful streaming job (e.g., today's dedup operator from Day 5, or a
running count) against a continuous synthetic source. While it's running:
```bash
# find and kill a TaskManager process to simulate a real failure
kill -9 <taskmanager-pid>
```
Watch the JobManager's logs — it should detect the failure, restart the affected
tasks, and restore state from the last completed checkpoint (check
`/tmp/flink-checkpoints` for the checkpoint directories, and verify the job's running
count is correct after restart — not reset to zero, and not double-counted).

## 6. Real-World Product Comparison

- This is **directly** the mechanism behind the JobManager instability you've debugged
  in production — a job cycling through failed/incomplete checkpoints is very often a
  barrier-alignment stall (a backpressured operator or a genuinely misconfigured
  bounded source never sending its final barrier) rather than a resource problem per se.
- Both **Uber** and **Alibaba** (heavy Flink users) rely on unaligned checkpointing
  specifically for high-backpressure jobs where alignment stalls were causing
  checkpoint timeouts at scale — the exact optimization named above.

## 7. Common Production Pitfalls

- Setting a checkpoint interval too aggressive relative to actual checkpoint duration —
  checkpoints start queuing behind each other, competing with actual data processing for
  resources.
- Not distinguishing a barrier-alignment stall (a backpressure symptom) from a genuine
  TaskManager crash when triaging a failed checkpoint — very different root causes,
  very different fixes.
- Forgetting that a savepoint and an automatic checkpoint, while similar in mechanism,
  serve different operational purposes — don't rely on checkpoints for a deliberate
  code-upgrade rollback plan; use savepoints.

## 8. Review Questions
1. Why do checkpoint barriers flow in-band with regular data instead of via a separate
   control channel?
2. What specifically causes a barrier-alignment stall, and why does it manifest as
   growing checkpoint duration?
3. What does unaligned checkpointing trade away, and what does it gain?
4. What's the practical difference between a checkpoint and a savepoint?

## 9. Proficiency Checkpoint
If you can look at a real checkpoint-duration metric graph and reason about whether
it's a backpressure/alignment issue versus a resource issue, you're at Level 2 moving
into genuine Level 3 territory — directly applicable to your live JobManager debugging.

## Next
Day 7 combines this week's concepts into one hands-on lab session, including your
first ADR.
