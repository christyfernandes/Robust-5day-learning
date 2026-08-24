# Day 11: Kafka — Performance Tuning

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Run `kafka-producer-perf-test`, vary `batch.size` and `linger.ms`, and chart the
resulting throughput/latency trade-off.

## 2. Core Concept (basics → advanced)

Kafka producer throughput and latency are governed largely by **batching** —
individual small messages are far less efficient to send (per-message network/
protocol overhead) than batching many messages into one request. Two key knobs
control this trade-off directly:

- **`batch.size`**: the maximum number of bytes the producer will accumulate per
  partition before sending a batch (a soft cap, not exact — a batch sends early if
  `linger.ms` elapses first).
- **`linger.ms`**: how long the producer will *wait*, hoping to accumulate a fuller
  batch, before sending what it has anyway — `linger.ms=0` (the default) sends
  essentially immediately, prioritizing latency over batching efficiency;
  `linger.ms=20` deliberately trades a small amount of added latency for
  meaningfully larger, more efficient batches under real load.

```
linger.ms=0:  msg1 → SEND, msg2 → SEND, msg3 → SEND  (low latency, small batches,
                                                        higher per-message overhead)

linger.ms=20: msg1, msg2, msg3 accumulate for up to 20ms → SEND as ONE larger batch
                                                        (slightly higher latency,
                                                         much better throughput)
```

## 3. How It Really Works (Internals)

On the broker side, throughput is also shaped by **compression** (`compression.type`
— `lz4`/`zstd` trade CPU for reduced network/disk I/O, usually a clear win at Kafka's
typical message volumes) and by how many **partitions** a producer writes across (more
partitions parallelize load but increase the number of independent in-flight batches
the producer must manage, with diminishing returns past a point tied to actual
consumer parallelism). On the consumer side, `fetch.min.bytes` and
`fetch.max.wait.ms` mirror the exact same batching trade-off from the other
direction — a consumer can wait to accumulate a fuller fetch response instead of
returning immediately with whatever's currently available.

The throughput/latency curve you'll chart in today's lab isn't a Kafka-specific
oddity — it's the same fundamental trade-off underlying nearly every high-throughput
system: batching amortizes fixed per-operation overhead across more work, at the cost
of making any *individual* operation wait slightly longer for that batch to fill.

## 4. Architecture & Design Pattern Spotlight

**Pattern: throughput vs. latency via batching — a trade-off, not a "one is
correct" question.** The right `linger.ms` value depends entirely on your actual use
case: a user-facing, latency-sensitive path (e.g., "confirm this order was placed")
wants low `linger.ms`; a high-volume analytics ingestion pipeline (where a few extra
milliseconds per batch is invisible against the overall pipeline's end-to-end latency)
benefits from a much higher `linger.ms` for meaningfully better throughput and lower
broker load.

## 5. Hands-On Lab

```bash
kafka-producer-perf-test.sh --topic perf-test --num-records 1000000 \
  --record-size 1024 --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092 batch.size=16384 linger.ms=0

kafka-producer-perf-test.sh --topic perf-test --num-records 1000000 \
  --record-size 1024 --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092 batch.size=65536 linger.ms=20
```
Run both, and chart the reported `records/sec` and average latency for each
configuration. Repeat with `compression.type=lz4` added to both, and compare total
throughput improvement from compression alone versus from batching alone.

## 6. Real-World Product Comparison

- **LinkedIn** (Kafka's origin) tunes `linger.ms` and `batch.size` differently across
  different topic classes internally — user-facing event topics favor lower latency;
  bulk analytics ingestion topics favor higher throughput — the same trade-off applied
  deliberately per use case rather than one global setting.
- This is the same throughput/latency trade-off pattern as **TCP Nagle's algorithm**
  (batching small writes to reduce packet overhead, at a small latency cost) — a
  recurring theme anywhere small operations are batched for network efficiency.

## 7. Common Production Pitfalls

- Leaving `linger.ms=0` for a high-volume ingestion pipeline "because it's the
  default," missing meaningful throughput gains available for near-zero real latency
  cost given the pipeline's actual tolerance.
- Setting `linger.ms` high for a genuinely latency-sensitive path without realizing
  the cost — every message now waits up to `linger.ms` even under light load, not just
  under heavy load.
- Not measuring actual production throughput/latency before and after a tuning
  change — these settings interact with real traffic patterns in ways synthetic
  benchmarks don't always capture precisely.

## 8. Review Questions
1. What's the practical difference between `batch.size` and `linger.ms`?
2. Why does a higher `linger.ms` typically improve throughput at some latency cost?
3. Why might two different topics in the same cluster warrant different tuning?
4. How is this the same trade-off as TCP's Nagle algorithm?

## 9. Proficiency Checkpoint
If you can chart a real throughput/latency curve and justify a specific tuning choice
for a stated use case, you're at Level 3.

## Next
Day 12 covers Kafka MirrorMaker 2 and multi-cluster geo-replication topologies.
