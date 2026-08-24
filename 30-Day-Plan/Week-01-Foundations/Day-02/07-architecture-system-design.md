# Day 2: Architecture & System Design — Replication Strategies

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Name and distinguish the three fundamental replication strategies, and correctly
classify each of this week's 6 tools by which one it uses (and why that choice fits the
tool's purpose).

## 2. Core Concept (basics → advanced)

**Three fundamental replication strategies:**

```
Leader-Follower (single-leader)          Multi-Leader                     Leaderless (quorum)
     ┌────────┐                          ┌────────┐  ┌────────┐          ┌────────┐ ┌────────┐
     │ Leader │◄── all writes            │Leader A│  │Leader B│          │ Node A │ │ Node B │
     └───┬────┘                          └───┬────┘  └───┬────┘          └───┬────┘ └───┬────┘
      ┌──┴──┐                                └────┬───────┘               write to W of N,
   ┌──▼─┐ ┌─▼──┐                            each accepts writes,          read from R of N,
   │Flwr│ │Flwr│                            replicates to the other       (W+R > N for
   └────┘ └────┘                            (needs conflict resolution)    strong consistency)
```

- **Leader-follower (single-leader):** all writes go to one leader, which replicates to
  followers. Simple to reason about (no write conflicts possible), but the leader is a
  single point of write-availability — if it's down, writes stop (until failover).
- **Multi-leader:** more than one node accepts writes (often one per data center),
  replicating to each other — better write availability across regions, but now you
  need a strategy for **conflicting concurrent writes** to the same record.
- **Leaderless/quorum:** no designated leader at all; a write succeeds once **W** nodes
  acknowledge it, and a read queries **R** nodes and reconciles; choosing `W + R > N`
  guarantees every read overlaps with the most recent write's acknowledged set.

## 3. How It Really Works (Internals)

Map this week's actual tools onto these three strategies — this is the payoff:

| Tool | Strategy | Why this fits its purpose |
|------|----------|------------------------------|
| **Kafka** (per partition) | Leader-follower | One partition leader keeps ordering simple and unambiguous; followers exist purely for durability/failover, never accept direct writes |
| **Redis** (Sentinel/Cluster) | Leader-follower, with Sentinel doing quorum-based **failover** (not quorum writes) | Simplicity + speed matter more than multi-region write availability for a cache |
| **ClickHouse** (ReplicatedMergeTree) | Leader-follower for data, **but quorum (Raft, via Keeper)** for metadata/coordination | Data replication can be async and eventually consistent; but "who owns this part, what's been merged" must be strongly consistent |
| **Elasticsearch** | Leader-follower per shard (primary + replica shards) | Same shape as Kafka's per-partition leader — one primary per shard accepts writes, replicas serve reads and stand by for failover |

Notice the recurring shape: **per-partition/per-shard leader-follower for the bulk data
path**, combined with a **separate Raft-based quorum layer for cluster metadata**
(Kafka's KRaft controller quorum, ClickHouse's Keeper). This is not a coincidence —
it's usually cheaper to make metadata strongly consistent (small, infrequent changes)
than to make every data write wait on quorum.

## 4. Architecture & Design Pattern Spotlight

**Pattern: separate consistency requirements for data vs. metadata.** Once you notice
this split, you'll see it as a deliberate, reusable design choice, not an accident of
any one tool: pay the quorum/consensus cost only where correctness genuinely can't be
relaxed (leadership, partition ownership, schema), and let the higher-volume data path
use a cheaper replication model.

## 5. Hands-On Lab
For Kafka, Redis, ClickHouse, and Elasticsearch, write one line each: "This tool uses
[leader-follower / multi-leader / leaderless] for its data path, and
[none / Raft / other] for metadata, because ______." Use the table above as a starting
point, but write the "because" yourself — that's the actual skill.

## 6. Real-World Product Comparison

- **DynamoDB** (Amazon) is the canonical leaderless/quorum system, directly descended
  from the original 2007 Dynamo paper — designed explicitly to keep accepting writes
  even during network partitions, at the cost of needing conflict resolution
  (vector clocks, or "last writer wins" as a simpler fallback).
- **CouchDB and some multi-region database setups** use multi-leader replication
  specifically to allow writes to succeed locally in every region without waiting on a
  cross-region round trip — at the cost of needing to resolve conflicting edits.
- **Kafka and ClickHouse**, as covered above, both chose leader-follower with a
  separate Raft-based metadata layer — a strong signal that this hybrid shape is a
  mature, common answer for systems needing both throughput and coordination
  correctness.

## 7. Common Production Pitfalls
- Assuming "multi-leader" automatically means "more available" without accounting for
  the real complexity of conflict resolution it introduces — it's a genuine trade, not
  a free upgrade.
- Confusing Redis Sentinel's quorum-based **failover decision** with true leaderless
  quorum **writes** — Sentinel still results in a single leader at any given moment; it
  just uses quorum to *decide* which node becomes leader next.
- Treating every replication strategy as interchangeable "just for durability" — the
  strategy also directly determines your consistency guarantees and failure behavior,
  which is the entire point of studying them.

## 8. Review Questions
1. What's the core trade Leader-follower gives up in exchange for its simplicity?
2. Why does multi-leader replication need conflict resolution, and leader-follower
   generally doesn't?
3. What does `W + R > N` guarantee in a leaderless/quorum system?
4. Why do Kafka and ClickHouse both pair "leader-follower for data" with "Raft/quorum
   for metadata" rather than picking one strategy for everything?

## 9. Proficiency Checkpoint
If you can correctly classify each of this week's tools by replication strategy and
explain *why* that strategy fits the tool's job, you're at Level 2, moving into Level 3.

## Next
Day 3 covers partitioning/sharding strategies — range, hash, and consistent hashing —
the complementary decision to replication (how data is *split*, not just *copied*).
