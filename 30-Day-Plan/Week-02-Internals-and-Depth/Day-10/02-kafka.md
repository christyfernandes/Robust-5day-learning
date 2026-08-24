# Day 10: Kafka — Log Compaction & Tiered Storage

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Create a compacted topic, write multiple values for the same key, and confirm only the
latest survives compaction — and draw the direct parallel to your ClickHouse hot/cold
TTL setup.

## 2. Core Concept (basics → advanced)

Kafka's default retention model deletes records after a time/size threshold, regardless
of key. **Log compaction** (`cleanup.policy=compact`) is a different retention
strategy entirely: instead of deleting old records by age, it guarantees **at least the
latest record for every key is retained forever**, while older records for the *same*
key are eligible for removal once compaction runs. This turns a Kafka topic into
something closer to a durable key-value store's changelog — "what's the current value
for key X" is always answerable from the topic itself, no matter how long ago it was
last written.

```
Before compaction:  (user1, "logged in")  (user2, "clicked")  (user1, "logged out")  (user1, "purchased")

After compaction:                          (user2, "clicked")                        (user1, "purchased")
                     (older user1 records removed — only the LATEST per key survives)
```

**Tiered storage** (a newer Kafka capability) extends retention economics further:
older log segments are moved to cheaper object storage (S3/GCS-compatible) while
remaining transparently readable through the same Kafka consumer API — recent, "hot"
data stays on local broker disk for low-latency access; older, "cold" data lives more
cheaply in object storage, fetched on demand when actually requested.

## 3. How It Really Works (Internals)

Compaction runs as a background process per partition, working on **closed log
segments** (never the currently-active segment being written to) — it scans a segment,
builds a map of the latest offset per key, and rewrites the segment retaining only
those latest-offset records (plus, optionally, a configurable grace period /
`min.compaction.lag.ms` before a record becomes eligible, giving consumers time to see
intermediate values if that matters for a given use case). This is directly why
compaction is *not* a guarantee that every intermediate value is retained — a fast
consumer might miss superseded values entirely, which is fine for "current state"
use cases (a KTable's changelog, Day 8) but wrong if you actually need the full history
of changes.

Tiered storage's tier-boundary is essentially a Kafka-native version of the exact same
hot/cold decision your ClickHouse TTL configuration makes — recent segments on fast
local disk, older segments moved to cheaper, slower object storage, with the consumer
API abstracting over which tier actually serves a given read.

## 4. Architecture & Design Pattern Spotlight

**Pattern: compacted log = "latest value per key," retained forever — the direct
structural parallel to your ClickHouse hot/cold TTL-to-GCS setup, applied to Kafka's
log instead of ClickHouse's MergeTree parts.** Both systems recognize the same
underlying economic reality: not all data needs equally expensive, equally fast
storage, and both let you express a retention/tiering *policy* declaratively rather
than manually managing where data physically lives.

## 5. Hands-On Lab

```bash
kafka-topics.sh --create --topic user-state --partitions 1 \
  --config cleanup.policy=compact --config min.cleanable.dirty.ratio=0.01 \
  --bootstrap-server localhost:9092

# write multiple values for the SAME key
kafka-console-producer.sh --topic user-state --bootstrap-server localhost:9092 \
  --property "parse.key=true" --property "key.separator=:" <<'EOF'
user1:logged_in
user1:clicked
user1:logged_out
user1:purchased
EOF

# force compaction to run (or wait for the background compaction thread)
# then consume from the beginning:
kafka-console-consumer.sh --topic user-state --bootstrap-server localhost:9092 \
  --from-beginning --property print.key=true
```
Confirm only `user1:purchased` (the latest value) survives after compaction runs —
the earlier values for `user1` should be gone, even though you produced four separate
records for that key.

## 6. Real-World Product Comparison

- Log compaction is exactly what makes Kafka a viable **backing store for KTables**
  (Day 8) and for service-to-service "latest known state" use cases (e.g., a
  service's own changelog of "current config per tenant") — without compaction, a
  changelog topic would grow unboundedly forever.
- **Confluent's** tiered storage and **AWS MSK's** equivalent both implement this same
  hot/cold split for Kafka's own log segments — directly comparable, in intent, to the
  TTL-to-GCS policy you've already configured on your ClickHouse cluster.

## 7. Common Production Pitfalls

- Using compaction for a use case that actually needs the full history of changes
  (e.g., an audit log) — compaction explicitly discards intermediate values, which is
  the wrong retention model if every historical value matters, not just the latest.
- Not accounting for `min.compaction.lag.ms` when reasoning about "how fresh is my
  compacted view" — a record isn't necessarily compacted away immediately, and
  consumers reading quickly enough may still briefly see superseded values.
- Assuming tiered-storage reads from cold tiers are equally fast as hot-tier reads —
  they're transparent to the consumer API, but genuinely slower, the same trade-off
  your ClickHouse TTL-to-GCS setup makes explicitly.

## 8. Review Questions
1. What specifically does log compaction guarantee, and what does it explicitly not
   guarantee?
2. Why does compaction only operate on closed segments, never the active one?
3. How is Kafka's tiered storage conceptually identical to your ClickHouse TTL-to-GCS
   policy?
4. When would compaction be the *wrong* retention model for a given use case?

## 9. Proficiency Checkpoint
If you can correctly decide whether compaction or time-based retention fits a given
use case, and explain the direct parallel to your ClickHouse tiering setup, you're at
Level 3.

## Next
Day 11 covers Kafka performance tuning — the producer/broker/consumer knobs that
determine actual throughput and latency, now that you understand storage/retention
mechanics fully.
