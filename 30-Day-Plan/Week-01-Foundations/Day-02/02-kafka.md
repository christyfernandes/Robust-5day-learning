# Day 2: Kafka — Producer Internals

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain what `acks` actually controls, what "idempotent producer" prevents
specifically, and how batching/compression settings trade latency for throughput.

## 2. Core Concept (basics → advanced)

**`acks` — the durability/latency dial:**
```
acks=0    → producer doesn't wait for any acknowledgment at all (fire and forget,
            fastest, can silently lose messages on broker failure)
acks=1    → wait for the partition LEADER to write the message (default balance)
acks=all  → wait for all in-sync replicas (ISR) to have the message (safest,
            slowest — this is what pairs with min.insync.replicas on the broker)
```

**Idempotent producer.** Without it, if a producer retries a send after a timeout
(because it didn't hear back, even though the broker actually got it), you can get a
**duplicate** message. Setting `enable.idempotence=true` gives each producer session a
unique ID plus a per-partition sequence number; the broker deduplicates retries with the
same ID+sequence, so retries become safe — this alone gets you exactly-once *at the
producer level* (a distinct, narrower guarantee than end-to-end exactly-once, which
also needs the consumer/sink side, covered in Week 2).

```python
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    acks="all",
    enable_idempotence=True,
    linger_ms=20,          # wait up to 20ms to batch more records together
    batch_size=32768,      # bytes, batch size trigger
    compression_type="lz4",
)
```

**Batching and `linger.ms`.** A producer doesn't send one network request per record —
it accumulates records into a batch (per partition) and sends the batch once it hits
`batch.size` bytes *or* `linger.ms` milliseconds elapses, whichever comes first. This is
a genuine latency-for-throughput trade: `linger.ms=0` sends immediately (lowest latency,
worst throughput); a higher value lets more records ride in one network round-trip.

## 3. How It Really Works (Internals)

```
App calls producer.send() repeatedly
          │
          ▼
   per-partition RECORD ACCUMULATOR (in producer's memory)
          │
     batch.size reached OR linger.ms elapsed
          │
          ▼
   Sender thread ships the batch over the network
          │
          ▼
   Broker (partition leader) appends to log, replicates per `acks` setting
```

Compression happens on the *whole batch*, not per-record — another reason batching
matters: `lz4`/`zstd`/`snappy` compress much better over a batch of similar records than
they would per-message, both saving network bandwidth and (often) disk space on the
broker.

## 4. Architecture & Design Pattern Spotlight

**Pattern: buffer-and-flush for throughput, with a tunable latency ceiling.** The same
shape reappears constantly in systems engineering — database write-ahead logs batching
`fsync` calls, HTTP clients batching requests, and (directly relevant later this week)
Elasticsearch's bulk indexing API. Once you've internalized "batch until size or time
threshold, whichever first," you'll recognize the same knob in several other tools this
month.

## 5. Hands-On Lab
```python
import time
from kafka import KafkaProducer

for linger in [0, 50]:
    producer = KafkaProducer(bootstrap_servers=["localhost:9092"], linger_ms=linger, batch_size=65536)
    start = time.time()
    for i in range(10_000):
        producer.send("orders", value=f"msg-{i}".encode())
    producer.flush()
    print(f"linger_ms={linger}: {time.time() - start:.2f}s")
```
Compare the two run times. `linger_ms=50` should show meaningfully higher throughput
for this many small messages — that's the batching trade-off made visible.

## 6. Real-World Product Comparison

- **Confluent's own guidance** for high-throughput pipelines routinely recommends
  raising `linger.ms` and `batch.size` well above the client defaults — the defaults
  favor low latency over maximum throughput, and most log-aggregation-style pipelines
  care more about throughput.
- Contrast with a **synchronous RPC client** (e.g., a typical REST client): no
  equivalent batching layer exists by default, because request/response semantics don't
  naturally support "wait a little, maybe more will show up" the way a fire-and-forget
  log append does.
- **Idempotent producers** are conceptually the same idea as **HTTP idempotency keys**
  used by payment APIs (Stripe, for instance, documents this pattern explicitly) — a
  client-generated identifier lets the server safely deduplicate a retried request.

## 7. Common Production Pitfalls
- Using `acks=1` (the historical default in many client libraries) for data you can't
  afford to lose, without realizing a leader failure right after acknowledging can
  still lose that message if it hadn't replicated yet.
- Setting `linger.ms` very high on a latency-sensitive path (e.g., anything
  user-facing) without realizing you've added that many milliseconds of worst-case
  delay to every request.
- Forgetting `enable.idempotence=true` and quietly accumulating duplicate messages
  under transient network blips, then debugging "duplicate" symptoms downstream instead
  of at the source.

## 8. Review Questions
1. What's the actual difference in what `acks=1` vs. `acks=all` waits for?
2. What specific problem does the idempotent producer solve, and how (mechanically)?
3. Why does compression work better on a batch than per-message?
4. Give one non-Kafka example of the same "batch until size or time, whichever first"
   pattern.

## 9. Proficiency Checkpoint
If you can correctly predict the durability/latency trade-off of a given
`acks`/`linger.ms`/idempotence configuration for a real workload, you're at Level 2,
moving into Level 3.

## Next
Day 3 covers the consumer side — consumer groups, partition assignment strategies, and
the rebalancing protocol that redistributes work when consumers join or leave.
