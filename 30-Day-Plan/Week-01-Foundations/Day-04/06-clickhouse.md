# Day 4: ClickHouse — Distributed Tables & Sharding Key Selection

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain how a `Distributed` table routes queries to shards, and design a sharding key
for a realistic events table while reasoning explicitly about skew.

## 2. Core Concept (basics → advanced)

A ClickHouse cluster's data is split across **shards** (each shard holds a disjoint
subset of the data, usually itself replicated for durability). A `Distributed` table
engine is a lightweight, storage-less "view" sitting in front of the real
per-shard tables (usually `ReplicatedMergeTree`) — queries against the `Distributed`
table get fanned out to every shard, executed locally on each, and the partial results
are merged on whichever node received the original query.

```
Client query
     │
     ▼
Distributed table (no data of its own — just routing logic)
     │
     ├──▶ Shard 1: local ReplicatedMergeTree (subset of data)
     ├──▶ Shard 2: local ReplicatedMergeTree (subset of data)
     └──▶ Shard 3: local ReplicatedMergeTree (subset of data)
             (each shard scans its own local granules — Day 3's sparse index — 
              then results are merged back at the query's entry node)
```

The **sharding key** (an expression, e.g., `cityHash64(org_id)`) decides which shard a
given row is written to. Get it right, and: (a) writes are evenly spread across shards,
and (b) queries filtering by that key can sometimes be routed to a single shard instead
of fanning out to all of them (query locality, the distributed analog of Day 3's
sparse-index skip).

## 3. How It Really Works (Internals)

`cityHash64(key) % num_shards` is the common default sharding expression — note the
same rebalancing weakness as any hash-mod scheme (Day 3's Architecture lesson): adding a
shard reshuffles most existing rows' "correct" shard assignment, though existing data
physically stays put (ClickHouse doesn't auto-migrate rows on shard-count change — this
is a deliberate manual operation, unlike Kafka partition reassignment).

Two failure modes to explicitly design against:
- **Write skew**: a poorly chosen key sends disproportionate write volume to one shard
  (e.g., sharding by a low-cardinality `region` when 80% of events are one region).
- **Query fan-out cost**: any query that doesn't filter on (or align with) the sharding
  key must hit *every* shard and merge results — this is fine for genuinely
  cluster-wide aggregations, but if most of your actual queries filter by, say,
  `org_id`, and you sharded by something else, you're paying full fan-out cost on every
  single query unnecessarily.

## 4. Architecture & Design Pattern Spotlight

**Pattern: scatter-gather over shards, driven by a sharding key — the exact same
structural decision as Kafka's partition-key choice.** Both ask "what field decides
physical placement, and does that align with how data will actually be read?" The
sharding key decision you make this week for your BigQuery-to-ClickHouse migration is
the single highest-leverage architectural choice in the whole POC — it's worth treating
with the same seriousness as a Kafka partition-key decision, not an afterthought.

## 5. Hands-On Lab

```sql
-- config: cluster with 3 shards defined in remote_servers XML

CREATE TABLE events_local ON CLUSTER my_cluster (
    org_id UInt32,
    event_time DateTime,
    event_type String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
ORDER BY (org_id, event_time);

CREATE TABLE events ON CLUSTER my_cluster AS events_local
ENGINE = Distributed(my_cluster, default, events_local, cityHash64(org_id));
```
Insert synthetic rows for ~50 distinct `org_id` values, with one `org_id` deliberately
representing 60% of rows (simulating one dominant tenant). Query
`system.parts` per shard (`SELECT hostName(), count() FROM clusterAllReplicas(...)`) to
see the actual row distribution — does the dominant org_id's shard have visibly more
data than the others? Now imagine sharding by `event_type` instead (far lower
cardinality) and reason through why that would be worse.

## 6. Real-World Product Comparison

- **Kafka**'s partition-key decision (Day 3) and ClickHouse's sharding-key decision
  are, structurally, the same design question asked at two different layers of the same
  kind of pipeline — get comfortable naming this pattern once, and you'll recognize it
  everywhere.
- **eBay** and **Uber**'s ClickHouse deployments both put real engineering effort into
  sharding-key selection specifically because query patterns (dashboards filtering by a
  specific tenant/region) determine whether most queries hit one shard or fan out to
  all — directly your MDO portal situation.

## 7. Common Production Pitfalls

- Sharding by a field that's convenient (e.g., an auto-increment ID) rather than the
  field your actual query patterns filter by most often.
- Not checking real per-shard row/query-load distribution after go-live — a sharding
  key that looked fine on paper can still produce skew from real-world traffic patterns
  that differ from synthetic test data.
- Confusing the sharding key with the `ORDER BY` key — they solve different problems
  (which shard vs. which granule) and can legitimately be different columns.

## 8. Review Questions
1. What does a `Distributed` table actually store, if anything?
2. Why does a query that doesn't align with the sharding key have to hit every shard?
3. What's the concrete difference in purpose between the sharding key and the `ORDER
   BY` key?
4. Why is a low-cardinality field almost always a bad sharding-key choice?

## 9. Proficiency Checkpoint
If you can design a sharding key for a given table + query-pattern description and
explain the skew/fan-out trade-offs of your choice, you're at Level 2 moving into a
real Level 3 — directly useful for this week's actual production decision.

## Next
Day 5 covers ClickHouse replication — `ReplicatedMergeTree` + Keeper — the mechanism
that makes each shard durable, which is exactly your live 3-node cluster's architecture.
