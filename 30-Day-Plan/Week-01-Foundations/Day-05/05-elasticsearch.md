# Day 5: Elasticsearch — Cluster Architecture

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Sketch node-role assignment for a realistic cluster size, and explain how shard/replica
placement and cluster-state consensus actually work together.

## 2. Core Concept (basics → advanced)

An Elasticsearch cluster is made of nodes with distinct **roles** (a single node can
hold multiple roles, but production clusters typically separate them for isolation):
- **Master-eligible nodes**: maintain and vote on **cluster state** (index metadata,
  shard-to-node mapping, cluster settings) — a small, dedicated set (odd number, same
  quorum logic as Raft) for stability, since master elections are disruptive if they
  happen too often.
- **Data nodes**: hold actual shard data and handle indexing/search/aggregation
  workload.
- **Ingest nodes**: run ingest pipelines (pre-processing documents before indexing).
- **Coordinating-only nodes**: route requests and merge results (the "scatter-gather
  coordinator" role from Day 4's aggregation lesson) without holding data themselves —
  useful as a stable, load-balanced query entry point in larger clusters.

Every index is split into **primary shards** (the actual partitioning of that index's
data) plus zero or more **replica shards** per primary (for redundancy and read
scale-out) — replicas are never placed on the same node as their primary, so a single
node failure can't take out both a primary and its own replica simultaneously.

## 3. How It Really Works (Internals)

**Cluster state** — the map of which shard lives on which node, index settings, etc. —
is maintained via a Raft-like consensus protocol among master-eligible nodes (modern
Elasticsearch uses its own implementation, conceptually in the same family as Day 4's
Raft lesson: a quorum of master-eligible nodes must agree before a cluster-state change
is committed). This is architecturally independent from how *data* is replicated
between a primary and its replica shards — that's a separate, simpler
primary-forwards-to-replicas write path, not itself Raft-coordinated.

This is the key structural insight: **metadata consensus (who's in charge, what shards
exist) and data replication (copying actual documents) are two separate mechanisms
solving two separate problems** — the same separation you'll see explicitly named
tomorrow in ClickHouse's Keeper (metadata) + async replica fetch (data) architecture.

## 4. Architecture & Design Pattern Spotlight

**Pattern: master-eligible quorum (consensus for metadata) + independent data
sharding/replication (a separate mechanism for data).** This split — a small quorum
deciding "what the cluster looks like," and a larger, differently-mechanized layer
actually moving data around — recurs directly in ClickHouse (Keeper decides metadata;
replica fetch moves data) and in Kafka KRaft (controller quorum decides partition
assignment; ISR replication moves the actual log data).

## 5. Hands-On Lab

Sketch (on paper or in a text file) a role assignment for a 6-node cluster serving a
workload with: heavy continuous indexing, moderate search query load, and a
requirement to survive any single node failure without losing data or search
availability. Consider:
- How many master-eligible nodes, and why an odd number?
- How many data nodes, and would you separate "hot" (recent, frequently indexed) from
  "warm" (older, read-mostly) data node roles?
- Would you add a dedicated coordinating-only node, and under what query-load
  condition would that become worthwhile?

## 6. Real-World Product Comparison

- Elasticsearch's **hot-warm-cold** node-role pattern (via node attributes + index
  lifecycle management) is the direct conceptual sibling of ClickHouse's TTL-based
  hot/cold tiering (Week 2) — both solve "recent data needs fast storage, old data
  needs cheap storage" with role/tier-aware placement rather than one-size-fits-all
  storage.
- **GitHub's code search** and **Uber**'s logging infrastructure both run
  purpose-separated node roles at scale for exactly the isolation reason above: a
  misbehaving ingest pipeline shouldn't be able to destabilize master election.

## 7. Common Production Pitfalls

- Running master-eligible and data roles on the same nodes in a cluster under heavy
  indexing load — a data-node resource spike (GC pause, disk pressure) can delay
  cluster-state consensus, since the same node is trying to do both jobs.
- Under-provisioning master-eligible node count (running with just 1, with no fallback)
  — a single point of failure for the entire cluster's ability to change state at all.
- Confusing "cluster is green" (shard allocation is healthy) with "cluster state
  consensus is healthy" — these are related but distinct health signals.

## 8. Review Questions
1. Why are master-eligible node count and cluster-state consensus kept separate from
   data replication?
2. Why must a replica shard never be placed on the same node as its primary?
3. What's the purpose of a coordinating-only node, and when does it become worth adding?
4. Why is odd master-eligible node count preferred, using the same reasoning as Day 4's
   Raft lesson?

## 9. Proficiency Checkpoint
If you can design a role-separated cluster topology for a stated workload and justify
each role's count, you're at Level 2 moving into Level 3.

## Next
Day 6 covers indexing internals — segments, refresh/flush/merge — the mechanism behind
"near-real-time" search, and a direct structural cousin of tomorrow's ClickHouse
Materialized Views lesson.
