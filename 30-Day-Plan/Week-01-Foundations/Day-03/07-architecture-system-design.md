# Day 3: Architecture — Partitioning & Consistent Hashing

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain range, hash, and consistent-hash partitioning, and correctly identify which
strategy Kafka, Redis Cluster, and ClickHouse each actually use — and why.

## 2. Core Concept (basics → advanced)

Every distributed system that spreads data across multiple nodes needs a rule for "which
node does this piece of data live on." Three main strategies:

- **Range partitioning**: sort keys, split into contiguous ranges per node (e.g.,
  A–F → node 1, G–M → node 2...). Simple, and supports efficient range scans — but
  vulnerable to **hot ranges** if data isn't evenly distributed across the key space
  (e.g., a monotonically increasing timestamp key piles all new writes on one node).
- **Hash partitioning**: `hash(key) % num_nodes`. Spreads load evenly (a good hash
  function has no hot spots) but destroys range-scan locality, and — critically —
  **changing the number of nodes reshuffles almost every key's assignment**, since `%
  num_nodes` changes for nearly every key when `num_nodes` changes.
- **Consistent hashing**: nodes and keys are both hashed onto the same circular
  keyspace ("hash ring"); each key belongs to the next node clockwise from it. Adding or
  removing one node only reassigns the keys between it and its neighbor — a small,
  bounded fraction of the total keyspace, not nearly all of it.

```
Consistent hashing ring:

        Node A
       ╱      ╲
  Node D        Node B
       ╲      ╱
        Node C

Key "orders/123" hashes to a point on the ring → belongs to the next
node clockwise. Remove Node B → only the keys between A and B (that
used to route to B) move to C. Nodes A, C, D are entirely untouched.
```

## 3. How It Really Works (Internals)

Plain consistent hashing has one practical problem: with few nodes, the ring can be
unevenly divided (one node might own a much larger arc than another purely by hash
chance). The standard fix is **virtual nodes** — each physical node is hashed onto the
ring at many points (e.g., 100–200 virtual positions per physical node) instead of one,
so the law of large numbers smooths out the imbalance, and a node's *effective* share of
the keyspace is the sum of many small arcs rather than one potentially-lopsided arc.

Rebalancing cost is the real reason this matters: hash-mod partitioning's "reshuffle
almost everything" behavior means adding a single node to a 10-node hash-mod cluster can
require moving ~90% of all data — consistent hashing (with virtual nodes) moves roughly
`1/N` of the data for the same operation, which is the difference between "routine
capacity scaling" and "a multi-hour migration event."

## 4. Architecture & Design Pattern Spotlight

**Pattern: consistent hashing — the go-to answer whenever "add/remove a node without a
massive reshuffle" matters.** This single pattern underlies three systems you're
studying this month, each with a different flavor:
- **Kafka** partitions are hash-assigned at *topic creation* time with a fixed partition
  count — Kafka sidesteps the rebalancing problem by making partition count a rarely-changed
  decision, and instead scales by adding *consumers*, not by reshuffling partitions.
- **Redis Cluster** uses a fixed 16,384-slot hash space (not a literal ring, but the same
  underlying idea) — slots are hash-assigned to nodes, and resharding means moving whole
  slots between nodes, a bounded, controllable operation.
- **ClickHouse** distributed tables use an explicit sharding key you choose yourself
  (Day 4) — no automatic ring, because ClickHouse assumes shard topology changes rarely
  and deliberately, not as routine elastic scaling.

## 5. Hands-On Lab

No code today — this is a mapping exercise. For each of Kafka, Redis Cluster, and
ClickHouse, write one sentence answering: *what exactly gets hashed, onto what space,
and what has to move when you add one node?* Then do the same for a hypothetical
hash-mod (`% num_nodes`) scheme, and compare the "what moves" answer directly — this
contrast is the entire point of today's lesson.

## 6. Real-World Product Comparison

- **DynamoDB**'s original 2007 paper is the reason consistent hashing became a standard
  distributed-systems tool — it used consistent hashing with virtual nodes explicitly to
  solve the "add a node without a massive rebalance" problem for a fully decentralized,
  leaderless store.
- **Cassandra** (directly descended from the Dynamo paper) uses the same ring-based
  consistent hashing, and its "vnodes" feature is precisely the virtual-node technique
  described above.

## 7. Common Production Pitfalls

- Choosing a hash-mod scheme "because it's simpler" for a system that will need to scale
  node count over its lifetime — the rebalancing cost shows up later, often as a
  surprise, at exactly the moment you're trying to scale under load.
- Picking a partition/shard key with low cardinality or skewed real-world distribution
  (e.g., partitioning by `country` when 80% of traffic is one country) — no partitioning
  *strategy* fixes a bad partitioning *key*.
- Assuming "distributed" automatically means "evenly distributed" — always verify actual
  per-node/per-partition load, don't just trust the algorithm in the abstract.

## 8. Review Questions
1. Why does hash-mod partitioning reshuffle almost everything when node count changes?
2. What problem do virtual nodes solve in consistent hashing?
3. Why does Kafka avoid the rebalancing problem entirely rather than solving it?
4. What's the real difference between "distributed" and "evenly distributed," and why
   does it matter operationally?

## 9. Proficiency Checkpoint
If you can explain why Redis Cluster's 16,384 slots and DynamoDB's hash ring are the
"same pattern, different implementation," you're at Level 2 and building real Level 3
architectural intuition.

## Next
Day 4 goes to consensus — Raft in detail — the algorithm that lets a cluster agree on
*who's in charge* in the first place, which every partitioning scheme above quietly
depends on.
