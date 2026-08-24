# Day 13: ClickHouse — Kafka Table Engine: Direct Ingestion

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Create a `Kafka` engine table plus a Materialized View to land events directly into a
MergeTree table, without writing a separate consumer application.

## 2. Core Concept (basics → advanced)

The **`Kafka` table engine** lets ClickHouse consume directly from a Kafka topic as if
it were a special kind of table — but critically, a `Kafka`-engine table is **not
storage**; querying it directly consumes messages from the topic (moving the consumer
offset forward) rather than returning a stable, re-queryable result. The standard
production pattern pairs it with a **Materialized View** (Week 1, Day 6): the MV's
query reads from the `Kafka`-engine table and writes into a real, storage-backed
`MergeTree` table — the MV's insert-trigger mechanism becomes the actual, continuous
ingestion pipeline, entirely inside ClickHouse, with no external consumer application
needed at all.

```
Kafka topic "events"
       │
       ▼
Kafka-engine table "events_queue"  ← NOT storage; consuming this moves the Kafka offset
       │
       ▼ (Materialized View, triggered on each new block consumed)
MergeTree table "events"           ← REAL storage — this is what you actually query
```

## 3. How It Really Works (Internals)

Internally, ClickHouse spins up actual Kafka consumer threads (configurable
`kafka_num_consumers`) that continuously poll the topic, and the attached
Materialized View's insert-trigger logic (the same mechanism from Week 1, Day 6's
normal-MV lesson) runs on each consumed block, transforming and inserting it into the
target MergeTree table. Because this is the *identical* mechanism as any other normal
Materialized View, the same limitation applies: the MV's query can only operate on the
newly-consumed block, not the whole target table — appropriate for straightforward
ingestion/light transformation, not for anything requiring a full-table
recomputation on each batch.

Consumer group semantics work essentially as expected (Week 1, Day 3) — if you
configure multiple ClickHouse nodes consuming the same topic with the same consumer
group, partitions are distributed across them the same way any Kafka consumer group
behaves, giving you natural horizontal ingestion scaling tied directly to the source
topic's partition count.

## 4. Architecture & Design Pattern Spotlight

**Pattern: native streaming ingestion — the log (Kafka) directly feeding the table
engine (MergeTree) via the same materialized-view mechanism used for other
incremental transformations, eliminating a separate consumer application layer
entirely.** This is architecturally elegant specifically because it reuses two
patterns you've already fully internalized (Kafka consumer groups, Materialized
Views) rather than introducing genuinely new mechanics — recognizing that reuse is
itself the lesson.

## 5. Hands-On Lab

```sql
CREATE TABLE events_queue (
    org_id UInt32, event_type String, amount Nullable(Float64), event_time DateTime
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'localhost:9092',
         kafka_topic_list = 'events',
         kafka_group_name = 'clickhouse_events_group',
         kafka_format = 'JSONEachRow';

CREATE TABLE events (
    org_id UInt32, event_type String, amount Nullable(Float64), event_time DateTime
) ENGINE = MergeTree ORDER BY (org_id, event_time);

CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT * FROM events_queue;
```
Produce a batch of JSON events into the `events` Kafka topic, then query the `events`
MergeTree table directly — confirm data lands there automatically, with no separate
consumer script running. Check `system.kafka_consumers` for consumer-group lag and
health.

## 6. Real-World Product Comparison

- This native-ingestion pattern is a genuine differentiator relative to **BigQuery**,
  where landing streaming Kafka data typically requires an external tool (Dataflow,
  or a custom consumer) writing into BigQuery's streaming insert API — ClickHouse
  keeps the entire ingestion pipeline inside the database itself.
- Compare to your **Flink-based ingestion** approach (studied all month) — the Kafka
  table engine is simpler (no separate job to deploy/manage) but less flexible for
  complex transformation/enrichment logic than a full Flink job; the right choice
  depends on how much processing genuinely needs to happen between Kafka and
  ClickHouse.

## 7. Common Production Pitfalls

- Querying the `Kafka`-engine table directly (outside of the MV) expecting stable,
  repeatable results — each query consumes and advances the offset, so this pattern
  is fundamentally different from querying a normal table.
- Not monitoring `system.kafka_consumers` for lag/errors — a silently failing or
  lagging ingestion MV can go unnoticed without explicit monitoring, since there's no
  separate consumer application's own health checks to rely on.
- Using this pattern for ingestion requiring complex, multi-step transformation logic
  that doesn't fit a single MV's query — this is where a dedicated Flink job (or
  separate consumer application) becomes the better-fitting tool.

## 8. Review Questions
1. Why is a `Kafka`-engine table not considered real storage?
2. What role does the Materialized View play in this ingestion pattern?
3. How does this pattern reuse both Kafka consumer-group semantics and
   Materialized-View mechanics you already know?
4. When would a dedicated Flink job be the better choice than this native pattern?

## 9. Proficiency Checkpoint
If you can set up a working native Kafka-to-MergeTree ingestion pipeline and correctly
explain its limitations, you're at Level 3 — directly relevant to evaluating
ingestion options for your migration.

## Next
Day 14 is this week's integrated lab and review — reproducing your real PySpark,
Flink, and ClickHouse incidents end to end.
