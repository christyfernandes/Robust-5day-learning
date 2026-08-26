# Day 1: Kafka — Event Streaming Foundations

## Time: ~30 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain Kafka as a distributed, partitioned **commit log** (not a traditional message
queue), and be able to reason about how a message's key determines its partition and
therefore its ordering guarantee.

## 2. Core Concept (basics → advanced)

**Start here if Kafka is genuinely new to you.** Kafka is a system for moving data
between other systems reliably, at high volume, in the form of a continuous stream of
small records (a "record" is just one event — e.g., "user 42 clicked button X at time
T"). One system **produces** (writes) records; one or more other systems **consume**
(read) them. What makes Kafka specifically useful, versus just calling one system's
API directly from another, is that the producer and consumers never need to know about
each other or even be running at the same time — the producer just writes to Kafka,
and any number of independent consumers can read that same data whenever they're
ready, at their own pace.

**Kafka is a log, not a queue — and this is the single most important thing to
understand first.** In a traditional message queue (RabbitMQ, SQS), once a consumer
reads a message, that message is typically removed — one message, one reader, then
it's gone. Kafka works completely differently: a record is **appended** to the end of
a running list (called a **log**) and just stays there until its configured retention
period expires, regardless of who has or hasn't read it yet. Many independent
**consumer groups** can read the exact same data, each at their own pace, each simply
remembering its own current read position (called an **offset**) in that log — reading
never removes anything. This one design choice is why Kafka became the default
"event backbone" for large systems: one write, any number of independent readers, and
data can even be re-read from the beginning later if needed (**replay**).

```
Topic: "orders" (3 partitions, replication factor 3)

Partition 0: [msg0][msg1][msg2][msg3]...  ← append-only, ordered within this partition
Partition 1: [msg0][msg1][msg2]...
Partition 2: [msg0][msg1][msg2][msg3][msg4]...

Ordering guarantee: ONLY within a partition. Across partitions, no ordering guarantee.
```

A **topic** is just the named category of data (e.g., "orders") — think of it like a
table name. A topic is physically split into multiple **partitions** (numbered 0, 1,
2, ... above) purely so that reading and writing can be parallelized across multiple
machines — each partition is its own independent, ordered log; Kafka makes **no
ordering promise at all across different partitions** of the same topic, only within
one partition.

**Producers, brokers, consumers, consumer groups — the four roles worth knowing by
name:**
- **Producer**: the client sending a record to a topic. If you supply a **key** (e.g.,
  a customer ID) with the record, Kafka hashes that key to deterministically pick a
  partition — the same key *always* lands on the same partition, which is exactly how
  you get ordering guarantees for a specific entity (e.g., "all of customer 42's
  events, in order") even though the topic overall has no global order. No key at all
  → Kafka spreads records round-robin (or in efficient batches) across partitions with
  no ordering promise whatsoever.
- **Broker**: one single Kafka server process. A Kafka **cluster** is a group of
  brokers working together, with each partition physically stored on (and served by)
  one or more of them.
- **Consumer group**: a named group of consumers that split a topic's partitions
  between themselves, so the group as a whole processes the topic faster than one
  consumer could alone (each partition is read by exactly one consumer *within* a
  given group). Two completely different consumer groups reading the same topic are
  entirely independent of each other — neither affects the other's read position.

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
monotonically increasing integer per partition (0, 1, 2, 3, ...), not a global
sequence number shared across the whole topic. Two different partitions both have an
offset "0," "1," "2" — they're independent counters.

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
from kafka import KafkaProducer
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

### Sample Output

Kafka's default partitioner hashes the key using a specific, well-defined algorithm
(murmur2, ported directly from the Java client) — which means the partition a given
key lands on is **fully deterministic and computable in advance**, not random. For
this exact lab's three keys, against a fresh 3-partition topic, you should see:

```
key=customer-0    -> partition 1, offset 0
key=customer-1    -> partition 0, offset 0
key=customer-2    -> partition 2, offset 0
key=customer-0    -> partition 1, offset 1
key=customer-1    -> partition 0, offset 1
key=customer-2    -> partition 2, offset 1
```

Reading this line by line:
- Every message with **the same key always lands on the same partition** — `customer-0`
  is on partition 1 both times it appears, `customer-1` is always on partition 0,
  `customer-2` is always on partition 2. This is the concrete, visible proof of the
  "same key → same partition" rule from the Core Concept section above — it isn't
  spread around, it isn't random, it's a pure function of the key's bytes.
- The **offset increments independently per partition**, starting from 0 each — the
  second message for `customer-0` gets offset 1 *within partition 1*, completely
  unrelated to what offset any other partition is at. There is no global, topic-wide
  offset counter.
- If you ran this against a topic that already had messages in it (not a totally
  fresh topic), the specific partition numbers above would stay exactly the same
  (the hash of `"customer-0"` never changes), but the **offsets would start higher** —
  wherever that partition's log had already reached.
- Notice the *partition numbers themselves* (1, 0, 2) look arbitrary — that's expected.
  The hash function's job is only to be *consistent*, not to produce numbers in any
  particular order relative to the keys.

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
<details><summary>Show answer</summary>

Because giving up global ordering is exactly what allows partitions to be spread
across multiple brokers and read/written in parallel — a single, strictly globally
ordered log would have to live on one machine and be written to sequentially, which
would cap Kafka's throughput at whatever one disk/one machine could do. Kafka instead
guarantees ordering only where it's actually needed (per-key, via partition
assignment), which is enough for the vast majority of real use cases while still
allowing full horizontal scalability.

</details>

2. What does `sendfile()`-based zero-copy actually avoid copying?
<details><summary>Show answer</summary>

Normally, sending data from disk to a network socket requires copying it: disk → OS
page cache → application's memory (JVM heap, in Kafka's case) → socket buffer → NIC.
`sendfile()` lets the OS transfer bytes directly from the page cache to the socket
buffer, skipping the trip through the application's own memory entirely. This avoids
both the extra memory copies and the JVM garbage-collection pressure that copying
into the heap would otherwise create.

</details>

3. If two independent consumer groups read the same topic, do they affect each other's
   offsets?
<details><summary>Show answer</summary>

No. Each consumer group tracks its own committed offset per partition, completely
independently. Group A being far ahead or behind has zero effect on Group B's
position — this is exactly what makes Kafka's one-write-many-independent-readers
model work.

</details>

4. What's the one design decision that makes partition count hard to change later?
<details><summary>Show answer</summary>

Keyed messages are routed to partitions via `hash(key) % num_partitions`. If you
change `num_partitions`, that formula's result changes for most existing keys —
messages for the same key that used to reliably land on partition 1 might now land on
partition 2, silently breaking the per-key ordering guarantee any downstream consumer
was relying on. This is why Kafka only allows increasing partition count (never
decreasing), and why picking a sensible partition count upfront matters more than it
might initially seem to.

</details>

## 9. Proficiency Checkpoint

**Quick Recap:**
- **Log, not queue**: reading a message doesn't delete it; many independent consumer
  groups can replay the same data at their own pace.
- **Topic** = named category; **partition** = one of a topic's parallel, independently-
  ordered sub-logs; **broker** = one Kafka server; **cluster** = many brokers together.
- **Ordering guarantee**: only within a single partition, never across partitions of
  the same topic.
- **Same key → same partition, always** — deterministic via hashing, not random —
  which is how you get ordering for a specific entity without needing global ordering.
- **Offset** = a per-partition, independently-incrementing position counter; there is
  no shared, topic-wide offset.
- **Consumer group** = a set of consumers splitting a topic's partitions between them;
  different groups reading the same topic never affect each other.

If you can correctly predict which partition a keyed message lands on, and explain why
that gives you per-key ordering but not global ordering, you're at Level 2.

## Next
Day 2 goes into the producer's internals in more depth — acks, idempotence, batching,
and what "exactly-once" actually means at the producer level.
