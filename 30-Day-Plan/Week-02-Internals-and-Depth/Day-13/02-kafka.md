# Day 13: Kafka — Kafka Connect & Debezium CDC

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Stand up Debezium against a sample Postgres table and watch row changes flow into a
Kafka topic — and explain how CDC captures changes without querying the source
database directly.

## 2. Core Concept (basics → advanced)

**Kafka Connect** is Kafka's framework for building reusable, configuration-driven
**source connectors** (pull data *into* Kafka from an external system) and **sink
connectors** (push data *out of* Kafka into an external system) — the same underlying
worker/task model MirrorMaker 2 (Day 12) is itself built on, applied generically to any
external system rather than specifically cluster-to-cluster replication.

**Debezium** is a widely-used source connector implementation specifically for
**Change Data Capture (CDC)** — rather than periodically *querying* a source database
for changes (which is inefficient and can miss rapid intermediate changes), Debezium
reads the database's own **write-ahead log / replication log** directly (Postgres's
WAL, MySQL's binlog) — the exact same mechanism the database uses internally for its
own durability and replication (Week 1, Day 3's WAL discussion) — and turns each
committed change into a Kafka event.

```
Postgres table UPDATE
       │
       ▼ (writes to Postgres's own WAL, as it always does — nothing CDC-specific here)
Postgres WAL
       │
       ▼ Debezium reads the WAL directly (via logical replication)
Kafka topic: one event per row-level change, in commit order
```

## 3. How It Really Works (Internals)

Because Debezium reads the WAL rather than polling with `SELECT` queries, it captures
**every** committed change, in order, with minimal added load on the source database
(reading a replication stream is a fundamentally different, much cheaper operation
than repeated polling queries) — and critically, it doesn't miss changes that a
polling approach could miss between poll intervals (e.g., a row updated twice between
two poll cycles — polling would only ever see the final value, while WAL-based CDC
sees both changes as distinct events, which matters for anything downstream that cares
about the full change history, not just current state).

This connects directly to your own architecture: CDC via Debezium is precisely how you
would feed real-time Postgres/MySQL changes into a Kafka-centric pipeline (feeding
Flink, or landing directly into ClickHouse via its Kafka table engine, Day 13's
ClickHouse lesson) without building custom polling infrastructure yourself.

## 4. Architecture & Design Pattern Spotlight

**Pattern: change-data-capture as a connector pattern, reading a database's own
replication log rather than polling.** This is architecturally identical in spirit to
how a Kafka replica reads a leader's log (Week 1, Day 4) or how ClickHouse replicas
fetch parts via Keeper-coordinated metadata (Week 1, Day 5) — "read the authoritative
log directly, rather than re-deriving state via periodic queries" is a recurring
efficient-replication pattern across every system studied this month.

## 5. Hands-On Lab

```bash
# Postgres: enable logical replication (postgresql.conf)
# wal_level = logical

docker run -d --name debezium-connect -p 8083:8083 \
  -e BOOTSTRAP_SERVERS=localhost:9092 debezium/connect:2.6

curl -X POST localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "orders-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "localhost", "database.dbname": "testdb",
    "table.include.list": "public.orders",
    "topic.prefix": "cdc"
  }
}'
```
Update a row in the `orders` table directly via `psql`, then consume from the
resulting `cdc.public.orders` topic — inspect the event structure (Debezium's
standard change-event envelope: `before`, `after`, operation type). Update the same
row twice in quick succession and confirm you see two distinct change events, not just
the final state.

## 6. Real-World Product Comparison

- **Debezium** (open-source, CNCF-adjacent) is the most widely adopted CDC connector
  for exactly this reason — it directly leverages databases' native replication
  mechanisms rather than reinventing change detection.
- Companies migrating from a traditional OLTP database toward a Kafka-centric
  real-time architecture (a very similar shape to your own BigQuery→ClickHouse
  migration, one layer up the stack) very commonly use Debezium as the entry point
  that turns "data trapped in a transactional database" into "a real-time event
  stream," feeding everything downstream from there.

## 7. Common Production Pitfalls

- Enabling CDC without accounting for its impact on the source database's WAL
  retention/disk usage — logical replication slots (which Debezium uses) prevent WAL
  segments from being recycled until consumed, and a stalled or crashed connector can
  cause the source database's disk usage to grow unexpectedly.
- Not handling schema changes on the source table gracefully — a column
  added/removed/retyped on the source database needs a corresponding strategy on the
  consuming side (schema evolution, Week 1 Day 6's Schema Registry lesson becomes
  directly relevant here).
- Assuming CDC captures data *before* it was ever written to the source database —
  CDC only captures changes going forward from when it's enabled; historical
  backfill of pre-existing data needs a separate initial snapshot mechanism.

## 8. Review Questions
1. Why does reading the WAL directly avoid the "missed intermediate changes" problem
   polling has?
2. What's the risk of an unmonitored, stalled CDC connector to the source database
   itself?
3. How is this pattern structurally similar to Kafka's own replica-fetch mechanism?
4. What does CDC *not* automatically give you, regarding pre-existing historical data?

## 9. Proficiency Checkpoint
If you can stand up a working CDC pipeline and correctly reason about its impact on
the source database, you're at Level 3.

## Next
Day 14 is this week's integrated lab and review, applying everything from Week 2
directly to your real production systems.
