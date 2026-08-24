# Day 5: ClickHouse — Replication: ReplicatedMergeTree & Keeper

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Trace exactly how a write propagates through your own 3-node cluster — from insert, to
Keeper metadata, to replica fetch — and explain why ClickHouse built its own Keeper
instead of depending on ZooKeeper.

## 2. Core Concept (basics → advanced)

`ReplicatedMergeTree` (the engine underlying every table in your production cluster)
separates two concerns explicitly:
- **Metadata coordination**: which parts exist, which replica is responsible for
  merging them, replication queue state — handled by **ClickHouse Keeper**, a
  Raft-based coordination service (originally ZooKeeper-compatible, now ClickHouse's own
  from-scratch reimplementation for better performance and operational simplicity).
- **Actual data replication**: the bytes of each data part — replicated via a simple
  **fetch** mechanism between replicas (a replica downloads a part directly from
  whichever replica already has it), not through Keeper itself (Keeper only ever stores
  small metadata entries, never bulk data).

```
INSERT on Replica 1
        │
        ▼
Replica 1 writes the part locally, THEN registers it in Keeper
        │ (Keeper: small metadata entry — "part abc123 exists on replica 1")
        ▼
Keeper (Raft-replicated across your 3 Keeper nodes) propagates this metadata
        │
        ▼
Replica 2, Replica 3 notice the new entry in their replication queue (via Keeper)
        │
        ▼
Replica 2, Replica 3 FETCH the actual part bytes directly from Replica 1 (not via Keeper)
```

## 3. How It Really Works (Internals)

This is the exact same separation of concerns you just studied in Elasticsearch (Day 5)
and Kafka KRaft (Day 5): **a small Raft-coordinated metadata layer, and a separate,
simpler data-movement mechanism.** ClickHouse Keeper specifically stores: the list of
active parts per replica, the replication queue (pending fetch/merge operations), and
distributed DDL coordination (so an `ALTER TABLE` issued on one replica is correctly
applied everywhere). Keeper does **not** store or transport actual table data —
that would defeat the entire purpose of keeping the coordination layer small and fast.

ClickHouse built its own Keeper (rather than continuing to depend on ZooKeeper, which
`ReplicatedMergeTree` originally required) primarily for two reasons: ZooKeeper's Java
runtime and general-purpose design added real operational overhead and a JVM dependency
to an otherwise C++, JVM-free system, and ClickHouse's specific access patterns (many
small, frequent metadata writes from a replication queue) benefited from a
purpose-built implementation rather than a general-purpose coordination service.

## 4. Architecture & Design Pattern Spotlight

**Pattern: Raft-coordinated metadata + independent async data replication.** By this
point in the week you've now seen this exact pattern three times (Elasticsearch's
master quorum + shard replication, Kafka's KRaft controller + ISR, and now ClickHouse
Keeper + part fetch) — recognizing it as one reusable architectural idea, rather than
three unrelated systems each doing their own thing, is precisely the Level 3+ thinking
this curriculum is building toward.

## 5. Hands-On Lab

On your actual 3-node cluster:
```sql
-- on replica 1
INSERT INTO events VALUES (...);

-- immediately check Keeper's view of the replication queue on replica 2
SELECT * FROM system.replication_queue WHERE table = 'events';

-- and check which replicas currently hold the new part
SELECT * FROM system.parts WHERE table = 'events' ORDER BY modification_time DESC LIMIT 5;
```
Watch the replication queue entry appear and then clear as replica 2/3 complete their
fetch. If you have access, briefly stop one replica, insert more data, then restart it
and watch it catch up via the replication queue — this is your real cluster's actual
recovery mechanism, made visible.

## 6. Real-World Product Comparison

- **ZooKeeper** is still what many older ClickHouse deployments (and other systems like
  Kafka pre-KRaft, and Hadoop/HBase) use for the same class of problem — Keeper is
  ClickHouse's answer to the exact same "do we really need a whole separate JVM-based
  coordination service" question KRaft asked of Kafka.
- This is precisely the coordination layer your **live production cluster** already
  runs — HAProxy handles client-facing load balancing, while Keeper handles this
  internal metadata coordination, two entirely separate concerns in your own deployed
  architecture.

## 7. Common Production Pitfalls

- Under-provisioning the Keeper quorum (fewer than 3 nodes, or co-locating all Keeper
  instances with heavy data-node load) — a slow Keeper quorum slows down every DDL
  statement and every part registration cluster-wide.
- Not monitoring `system.replication_queue` length — a growing, un-draining queue is an
  early warning sign of a replica falling behind or a network issue between replicas,
  well before it becomes a full outage.
- Assuming Keeper stores/transports data — sizing Keeper's storage or network capacity
  as if it needs to handle bulk data volume, when it only ever handles small metadata
  entries.

## 8. Review Questions
1. What specifically does Keeper store, and what does it deliberately not store?
2. Why does a replica fetch a part directly from another replica instead of through
   Keeper?
3. Why did ClickHouse build its own Keeper instead of continuing to require ZooKeeper?
4. What's the operational early-warning value of monitoring `system.replication_queue`?

## 9. Proficiency Checkpoint
If you can trace a write from `INSERT` through Keeper metadata to a completed replica
fetch, on your own real cluster, you're at a genuine Level 3 on this specific topic —
this is production infrastructure you already operate, now with the internals made explicit.

## Next
Day 6 covers Materialized Views — normal vs. **Refreshable** — directly setting up this
week's task of mapping BigQuery scheduled queries onto ClickHouse equivalents.
