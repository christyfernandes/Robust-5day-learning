# Day 9: Kafka — Exactly-Once Semantics (EOS)

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Wrap a produce-to-two-topics operation in a Kafka transaction and verify atomicity —
and explain what idempotent producers and the transactional API each solve.

## 2. Core Concept (basics → advanced)

Two separate mechanisms combine to give Kafka **exactly-once semantics**:

- **Idempotent producer** (`enable.idempotence=true`): solves *duplicate delivery from
  retries* — each producer gets a unique ID and each message a sequence number; the
  broker deduplicates any retried message with a sequence number it's already seen,
  even if the original write actually succeeded but the acknowledgment was lost over
  the network (a very common real cause of accidental "duplicate" writes without
  idempotence).
- **Transactional API** (`transactional.id` configured, `initTransaction`/
  `beginTransaction`/`commitTransaction`): solves *atomicity across multiple
  writes* — e.g., producing to two topics (or producing plus committing a consumer
  offset, the classic "consume-transform-produce" pattern) either **all** succeed
  together or **all** are rolled back, never a partial result visible to a
  `read_committed` consumer.

```
Without transactions:  produce(topic A) succeeds, produce(topic B) FAILS
                        → topic A has the write, topic B doesn't — inconsistent state

With transactions:     beginTransaction()
                        produce(topic A)
                        produce(topic B)
                        commitTransaction()
                        → a read_committed consumer sees EITHER both writes or neither
```

## 3. How It Really Works (Internals)

A **transaction coordinator** (a designated broker, tracked via an internal
`__transaction_state` topic) manages the transaction's lifecycle, writing **control
messages** (markers) to every partition involved, indicating whether the transaction
ultimately committed or aborted. A consumer configured with `isolation.level=
read_committed` filters out records belonging to any transaction that hasn't committed
(including one that's still in progress, or one that aborted) — it simply skips
those offsets when reading, rather than exposing partial/uncommitted writes at all.

This is architecturally similar in spirit to a database's two-phase commit
(Week 1, Day 5's 2PC lesson): a coordinator, participants (partitions across possibly
multiple topics), and a commit/abort decision applied atomically across all of them —
Kafka's transaction coordinator plays exactly the 2PC coordinator's role, adapted to
Kafka's log-based model.

## 4. Architecture & Design Pattern Spotlight

**Pattern: two-phase-commit-style transactional writes, adapted to a log-based
system.** Recognizing Kafka's transaction protocol as "2PC, but the participants are
partitions and the durable record is control messages in the log" connects directly
back to Week 1 Day 5's general distributed-transactions lesson — the same underlying
coordination problem, solved with Kafka-specific mechanics.

## 5. Hands-On Lab

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    transactional_id="day9-demo-producer",
    enable_idempotence=True,
)
producer.init_transactions()

try:
    producer.begin_transaction()
    producer.send("topic-a", b"event for A")
    producer.send("topic-b", b"event for B")
    producer.commit_transaction()
except Exception:
    producer.abort_transaction()
    raise
```
Run this successfully, then deliberately force an exception between the two `send()`
calls (e.g., simulate a failure) and call `abort_transaction()` instead — using a
`read_committed` consumer on both topics, verify: after a successful commit, both
messages appear; after an abort, **neither** appears, even though the producer
technically sent one of them to the broker before aborting.

## 6. Real-World Product Comparison

- Kafka's transactional API is what makes **Kafka Streams'** exactly-once processing
  guarantee possible under the hood (Day 8's KStream/KTable lesson) — Kafka Streams
  wraps its own read-process-write cycle in exactly this transactional mechanism.
- Compare to **database transactions**: the guarantee (atomicity across multiple
  writes) is conceptually identical, but Kafka's version is scoped specifically to
  writes across partitions/topics (plus consumer offset commits), not arbitrary
  read-modify-write logic the way an RDBMS transaction can express.

## 7. Common Production Pitfalls

- Enabling the transactional API without also configuring consumers for
  `read_committed` — without that isolation level, consumers see uncommitted
  (including eventually-aborted) writes anyway, defeating the purpose.
- Assuming idempotence alone (without the transactional API) gives you atomicity
  across multiple topics — it only deduplicates retries of the *same* message, not
  cross-topic atomicity.
- Underestimating the latency cost of transactions — the coordinator round-trip and
  control-message overhead add real latency compared to non-transactional produces;
  this is a genuine throughput/latency trade-off, not a free correctness upgrade.

## 8. Review Questions
1. What specific problem does the idempotent producer solve, versus what the
   transactional API solves?
2. What does a `read_committed` consumer actually filter out?
3. How is Kafka's transaction coordinator analogous to a 2PC coordinator?
4. Why doesn't idempotence alone provide cross-topic atomicity?

## 9. Proficiency Checkpoint
If you can correctly implement a transactional produce-to-two-topics operation and
explain exactly what guarantee it provides (and what it costs), you're at Level 3.

## Next
Day 10 covers log compaction and tiered storage — a direct parallel to your ClickHouse
hot/cold TTL setup.
