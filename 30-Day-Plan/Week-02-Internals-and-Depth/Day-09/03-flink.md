# Day 9: Flink — Exactly-Once Sinks: Two-Phase Commit

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Configure a Flink Kafka sink for exactly-once delivery and verify no duplicates after a
forced restart.

## 2. Core Concept (basics → advanced)

Flink's internal state can be made exactly-once via checkpointing (Week 1, Day 6) — but
getting exactly-once **all the way out to an external sink** (like Kafka) requires
additional coordination, because the sink's writes are external side effects that
checkpointing alone doesn't automatically make transactional.

Flink solves this with a **TwoPhaseCommitSinkFunction** pattern: writes to the external
system happen inside a transaction that's tied to Flink's own checkpoint cycle —
**pre-commit** happens when a checkpoint is taken (the sink flushes its buffered writes
into an open transaction, but doesn't finalize it yet), and the transaction is only
**committed** once the checkpoint itself is confirmed complete across the whole job.
If a failure happens before the checkpoint completes, the pre-committed (but
not-yet-committed) transaction is aborted on recovery — meaning the external system
never sees a partial, uncommitted write survive a failure.

```
Checkpoint N starts
       │
       ▼
Sink: pre-commit (flush buffered writes into an OPEN external transaction)
       │
       ▼
Checkpoint N confirmed complete across ALL operators
       │
       ▼
Sink: COMMIT the transaction  ← only now does the external system see the data
                                 (if checkpoint N had failed, this transaction
                                  would instead be ABORTED on recovery)
```

## 3. How It Really Works (Internals)

For a Kafka sink specifically, this is implemented **directly on top of Kafka's own
transactional producer API** (Day 9's Kafka lesson) — Flink's checkpoint completion is
what triggers the Kafka transaction's `commitTransaction()` call. This is a genuinely
elegant composition: Flink handles "when is it safe to commit" (tied to its own
distributed checkpoint consistency), and Kafka's transactional API handles "how to
commit atomically" — two systems' exactly-once mechanisms composed together rather than
Flink reimplementing Kafka's transaction protocol itself.

The practical consequence: a **downstream `read_committed` consumer** of the sink
topic never sees a duplicate, even if Flink restarts from a checkpoint and replays
some already-processed input — because any write from a pre-checkpoint attempt that
never got confirmed as committed is simply never visible to `read_committed` readers
at all.

## 4. Architecture & Design Pattern Spotlight

**Pattern: two-phase commit tied to a checkpoint barrier — the general 2PC pattern
(Week 1, Day 5) applied specifically to make external side effects consistent with
internal distributed snapshot state.** This is the same coordination discipline as
Kafka's own transactional producer (Day 9's Kafka lesson), composed one layer up:
Flink's checkpoint is the "commit signal," and the sink's 2PC implementation is the
mechanism that acts on it.

## 5. Hands-On Lab

```python
from pyflink.datastream.connectors.kafka import KafkaSink, KafkaRecordSerializationSchema, DeliveryGuarantee

sink = KafkaSink.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_record_serializer(
        KafkaRecordSerializationSchema.builder()
            .set_topic("output-topic")
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
    ) \
    .set_delivery_guarantee(DeliveryGuarantee.EXACTLY_ONCE) \
    .build()

stream.sink_to(sink)
```
With checkpointing enabled (Week 1, Day 6), run this job, then forcibly kill a
TaskManager mid-run (as you did in that earlier lab). After Flink recovers from the
last checkpoint and reprocesses some input, use a `read_committed` consumer against
`output-topic` and count total messages — verify the count matches expected output
exactly, with no duplicates from the reprocessed input.

## 6. Real-World Product Comparison

- This exact mechanism (checkpoint-tied 2PC to a Kafka sink) is what makes Flink a
  common choice at companies like **Alibaba and Uber** for financially or
  operationally sensitive pipelines, where duplicate output isn't just an inconvenience
  but a real correctness/business problem (e.g., duplicate charge events).
- Contrast with **Kafka Streams' own exactly-once guarantee** (Day 8) — conceptually
  the same underlying idea (transactional writes tied to processing progress), but
  Kafka Streams ties it to its own internal processing loop rather than Flink's
  distributed checkpoint barrier mechanism.

## 7. Common Production Pitfalls

- Setting `DeliveryGuarantee.AT_LEAST_ONCE` (or leaving the default) when the actual
  requirement is exactly-once — a common, easy-to-miss configuration gap that looks
  correct until a failure/restart actually produces visible duplicates.
- Not configuring the downstream consumer with `isolation.level=read_committed` — the
  sink can be perfectly correctly configured for exactly-once, but a plain
  `read_uncommitted` consumer still sees uncommitted/aborted writes.
- Underestimating transaction-related latency — checkpoint-tied commits mean output
  visibility is tied to checkpoint interval, a real latency floor for downstream
  consumers expecting near-instant visibility.

## 8. Review Questions
1. What's the difference between "pre-commit" and "commit" in the two-phase commit
   sink pattern?
2. Why is Flink's checkpoint completion the right trigger for committing the external
   transaction?
3. How does this pattern rely on Kafka's own transactional producer API underneath?
4. What consumer-side configuration is required to actually observe the exactly-once
   guarantee?

## 9. Proficiency Checkpoint
If you can configure an exactly-once Kafka sink correctly and verify zero duplicates
after a forced restart, you're at Level 3 — a directly deployable production skill.

## Next
Day 10 covers bounded vs. unbounded sources — your live JobManager-instability issue,
now with checkpointing and exactly-once mechanics as full context.
