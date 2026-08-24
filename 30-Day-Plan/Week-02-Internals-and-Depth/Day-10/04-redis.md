# Day 10: Redis — Redis Cluster: Hash Slots & Gossip Protocol

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Stand up a 3-node Redis Cluster, insert keys, and observe slot distribution via
`CLUSTER KEYSLOT` — and explain how nodes discover cluster topology via gossip.

## 2. Core Concept (basics → advanced)

Redis Cluster shards data across nodes using a **fixed 16,384-slot keyspace** — every
key is hashed via CRC16 and mapped to one of these 16,384 slots
(`slot = CRC16(key) % 16384`), and each slot is assigned to exactly one node (with
replicas for durability, following the same primary/replica model as Sentinel, Day 9,
but now built into Cluster itself). This is conceptually adjacent to consistent hashing
(Week 1, Day 3) but uses a **fixed, enumerable slot count** rather than a continuous
hash ring — resharding means moving *whole slots* between nodes, a discrete, trackable
operation rather than an abstract ring-position recalculation.

```
Key "user:123" → CRC16("user:123") % 16384 → slot 5474

Slot ranges assigned to nodes:
  Node A: slots 0 - 5460
  Node B: slots 5461 - 10922
  Node C: slots 10923 - 16383

"user:123" (slot 5474) → lives on Node B
```

## 3. How It Really Works (Internals)

Nodes discover and maintain cluster topology via a **gossip protocol**: every node
periodically exchanges lightweight messages with a random subset of other nodes,
sharing what it knows about cluster state (which nodes are up, which slots they own,
recent failure suspicions) — over time, this decentralized, peer-to-peer information
exchange converges the whole cluster on a consistent view without any single
coordinator needing to broadcast to everyone directly. This is a different coordination
philosophy from the Raft-based quorums you've studied elsewhere this month (Kafka
KRaft, ClickHouse Keeper) — gossip trades strict, immediately-consistent agreement for
eventual convergence and much lower coordination overhead, appropriate for cluster
*topology* information that doesn't need the strict linearizability a data write might.

A client library that's **cluster-aware** caches the slot-to-node mapping and routes
each command directly to the correct node; a client that isn't cluster-aware (or has a
stale mapping after a resharding operation) gets a `MOVED` redirect response from
whichever node it contacted incorrectly, telling it exactly which node actually owns
that slot now.

## 4. Architecture & Design Pattern Spotlight

**Pattern: fixed-slot sharding (consistent-hashing-adjacent) + gossip-based topology
discovery.** Compare the sharding half directly to Kafka's partition assignment (Week
1, Day 3) and ClickHouse's explicit sharding key (Week 1, Day 4) — all three solve "how
do I distribute keys across nodes," with Redis Cluster's fixed slot count being a
middle ground between Kafka's fully-fixed partition count and a continuous consistent-
hashing ring. The gossip half is a genuinely different coordination pattern from every
Raft-based system you've studied — worth holding both patterns (strict quorum
consensus vs. eventually-consistent gossip) as separate tools for separate jobs.

## 5. Hands-On Lab

```bash
# minimal local 3-node cluster (ports 7000-7002), each with cluster-enabled config
redis-cli --cluster create 127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  --cluster-replicas 0

redis-cli -c -p 7000 SET user:123 "alice"
redis-cli -c -p 7000 CLUSTER KEYSLOT user:123     # which slot?
redis-cli -c -p 7000 CLUSTER NODES                 # which node owns that slot?
```
Insert ~1000 synthetic keys, then check slot distribution across all 3 nodes via
`CLUSTER COUNTKEYSINSLOT` summed per node's owned ranges — confirm it's roughly even.
Try connecting directly to a node that doesn't own a given key's slot without the `-c`
(cluster mode) flag and observe the `MOVED` response.

## 6. Real-World Product Comparison

- Redis Cluster combines what **Sentinel** (Day 9, failover only) and manual sharding
  would otherwise require as two separate systems — many teams migrate to Cluster
  specifically to get both sharding and failover from one coherent system rather than
  Sentinel-plus-a-homegrown-sharding-layer.
- **Cassandra**'s gossip protocol (directly descended from the same Amazon Dynamo
  lineage as consistent hashing itself) is architecturally very similar to Redis
  Cluster's — both chose gossip specifically for horizontal scalability of the
  coordination layer itself, avoiding a single coordinator becoming a bottleneck as
  node count grows.

## 7. Common Production Pitfalls

- Using multi-key operations (e.g., `MSET`, a Lua script touching multiple keys)
  across keys that hash to different slots — Cluster requires such operations' keys to
  be in the *same* slot, commonly solved with **hash tags** (`{user:123}:profile` and
  `{user:123}:orders` both hash on `user:123` only, guaranteeing the same slot).
- Not using a cluster-aware client library — silently eating `MOVED` redirects as
  errors instead of following them, or worse, retrying against the wrong node
  repeatedly.
- Assuming gossip convergence is instantaneous — during a resharding operation or a
  node failure, there's a real (if typically brief) window where different nodes may
  have a slightly stale view of cluster topology.

## 8. Review Questions
1. Why is Redis Cluster's fixed 16,384-slot model considered adjacent to, but distinct
   from, consistent hashing?
2. What's the practical purpose of a `MOVED` redirect?
3. Why does gossip trade strict consistency for lower coordination overhead, and why
   is that an acceptable trade for cluster topology specifically?
4. What problem do hash tags solve, and why do multi-key operations need them?

## 9. Proficiency Checkpoint
If you can predict which node owns a given key and correctly design hash-tagged keys
for a multi-key operation, you're at Level 3.

## Next
Day 11 covers caching patterns (cache-aside, read-through, write-through) — directly
relevant to your MDO portal cache-bypass investigation from Week 1.
