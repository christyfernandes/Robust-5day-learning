# Day 1: Kafka — Event Streaming Foundations

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain Kafka as a distributed, partitioned **commit log** (not a traditional message
queue), and be able to reason about how a message's key determines its partition and
therefore its ordering guarantee.

## 2. Core Concept (basics → advanced)

**Kafka is a log, not a queue.** In a traditional queue (RabbitMQ, SQS), a message is
removed once consumed. In Kafka, a message is **appended** to a partition and stays
there until its retention period expires — many independent consumer groups can read
the same data at their own pace, each tracking its own position. This single design
choice is why Kafka became the default "event backbone": one write, many independent
readers, replayable.

```
Topic: "orders" (3 partitions, replication factor 3)

Partition 0: [msg0][msg1][msg2][msg3]...  ← append-only, ordered within this partition
Partition 1: [msg0][msg1][msg2]...
Partition 2: [msg0][msg1][msg2][msg3][msg4]...

Ordering guarantee: ONLY within a partition. Across partitions, no ordering guarantee.
```

**Producers, brokers, consumers, consumer groups:**
- **Producer** sends a record to a topic. If you supply a **key**, Kafka hashes it to
  pick the partition — same key always → same partition → ordering preserved for that
  key. No key → round-robin (or sticky-batch) across partitions.
- **Broker** is one Kafka server; a cluster is many brokers, each holding some
  partitions.
- **Consumer group**: consumers in the same group split the partitions between them —
  this is how Kafka parallelizes consumption. Two groups reading the same topic are
  fully independent of each other.

## 3. How It Really Works (Internals)

A partition is physically a set of **log segment files** on disk, append-only, plus an
index file mapping offsets to file positions. Kafka relies heavily on the **OS page
cache** rather than its own in-process cache — writes go through `write()` (not
`fsync()` per message) and reads use `sendfile()` for a **zero-copy** transfer straight
from page cache to network socket, bypassing the JVM heap entirely. This is a large part
of why Kafka achieves such high throughput on commodity disks: it's leaning on
kernel-level I/O primitives instead of reinventing them.

```
Producer → serialize → pick partition (hash(key) % num_partitions, or sticky round-robin)
                              │
                              ▼
                    Broker (leader for that partition)
                              │
                 append to log segment (page cache, async fsync)
                              │
                 replicate to follower brokers (in-sync replicas, ISR)
```

An **offset** is just the position of a record within its partition — a simple
monotonically increasing integer per partition, not a global sequence number.

## 4. Architecture & Design Pattern Spotlight

**Pattern: log-structured storage as the source of truth.** The same idea underlies
Elasticsearch's segment files and ClickHouse's MergeTree parts — append-only,
immutable-once-written storage that's later merged/compacted, rather than in-place
updates. Once you see this pattern once, you'll recognize it in Weeks 2–4 across four
different tools. It's also the substrate for **event sourcing** (Architecture, Week 4):
if your log is durable and replayable, it can be your system of record, not just a
transport layer.

## 5. Hands-On Lab

```bash
# Docker (single-node KRaft mode — no ZooKeeper needed in modern Kafka)
docker run -d --name kafka -p 9092:9092 apache/kafka:latest

# Create a topic with 3 partitions
kafka-topics.sh --create --topic orders --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

```python
from kafka import KafkaProducer, KafkaConsumer
import json

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Send 6 orders, 3 distinct customer keys -> watch which partition each lands on
for i in range(6):
    customer = f"customer-{i % 3}"
    fut = producer.send("orders", key=customer.encode(), value={"order_id": i, "customer": customer})
    meta = fut.get(timeout=10)
    print(f"key={customer:12s} -> partition {meta.partition}, offset {meta.offset}")
```

Run it twice. Confirm the same customer key always lands on the same partition —
that's your ordering guarantee in action.

## 6. Real-World Product Comparison

- **LinkedIn** built Kafka to solve exactly this: dozens of internal systems needing the
  same activity-stream data, without every producer having to know every consumer.
- **Netflix's Keystone pipeline** uses Kafka as the ingestion backbone for hundreds of
  billions of events/day feeding both real-time (Flink) and batch (Spark) consumers —
  the same event, read once, consumed twice at different paces. That's the pattern you
  should recognize by Week 4.
- Contrast with **RabbitMQ**: a true message broker with routing (exchanges, bindings),
  built for task distribution and RPC-style messaging, not long-term replay. If you need
  "many independent consumers can replay history," Kafka; if you need "flexible routing
  for a task queue," RabbitMQ is usually simpler and a better fit.

## 7. Common Production Pitfalls
- No key on high-volume topics → messages round-robin across partitions with no
  ordering guarantee at all, which surprises people expecting FIFO-per-topic behavior.
- Confusing "message consumed" with "message deleted" — Kafka doesn't delete on read;
  retention/compaction policy controls when data actually leaves the log (Week 2, Day 10).
- Too few partitions chosen upfront — partition count can only be *increased*, never
  decreased, and increasing it after the fact can break existing key-to-partition
  ordering assumptions.

## 8. Review Questions
1. Why is "no ordering guarantee across partitions" a feature, not just a limitation?
2. What does `sendfile()`-based zero-copy actually avoid copying?
3. If two independent consumer groups read the same topic, do they affect each other's
   offsets?
4. What's the one design decision that makes partition count hard to change later?

## 9. Proficiency Checkpoint
If you can correctly predict which partition a keyed message lands on, and explain why
that gives you per-key ordering but not global ordering, you're at Level 2.

## Next
Day 2 goes into the producer's internals in more depth — acks, idempotence, batching,
and what "exactly-once" actually means at the producer level.
