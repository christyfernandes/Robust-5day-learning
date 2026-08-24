# Day 4: Kafka — Broker Internals & Leader Election

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain what ISR actually enforces, what `min.insync.replicas` does under a broker
failure, and what happens end-to-end when a partition leader dies.

## 2. Core Concept (basics → advanced)

Every partition has exactly one **leader** broker (handles all reads/writes for that
partition) and zero or more **follower** brokers (replicate the leader's log). The
**in-sync replica set (ISR)** is the subset of replicas — leader plus followers — that
are currently caught up within an acceptable lag threshold. Only ISR members are
eligible to become the new leader if the current one fails, because only they're
guaranteed to have all acknowledged data.

```
Partition 0, replication factor 3:

  Leader (Broker 1)  ──replicates──▶  Follower (Broker 2) [in ISR]
                     ──replicates──▶  Follower (Broker 3) [in ISR]

  If Broker 1 dies → controller picks a new leader FROM THE ISR ONLY
  (Broker 2 or 3 — never a replica that had fallen behind)
```

`acks=all` (the durability-safe setting) means the producer waits for the write to be
acknowledged by **all current ISR members**, not literally every replica — which is why
`min.insync.replicas` matters: it sets the *minimum* ISR size required for a write to
succeed at all. With `replication.factor=3` and `min.insync.replicas=2`, you can lose one
broker and keep accepting writes safely; lose two, and Kafka correctly refuses writes
rather than silently accepting them with insufficient durability.

## 3. How It Really Works (Internals)

Each partition is physically a sequence of **log segments** on disk (not one giant file
— segments roll over at a configurable size/time, enabling efficient deletion of old
data and efficient reads via segment-level indexes). Every segment has an accompanying
**offset index** (offset → byte position in the segment file) and **time index**
(timestamp → offset), which is how a consumer can seek to "give me messages from
timestamp X" without scanning the whole log from the start.

**Leader election**: the **controller** (itself elected via Raft in modern KRaft-mode
Kafka — Day 5) detects a leader failure via missed heartbeats, and picks the new leader
from the ISR — typically the replica with the most caught-up log (the "preferred
replica" logic also factors in for planned rebalancing, to keep leadership evenly spread
across brokers under normal operation). An **unclean leader election** (electing a
replica *outside* the ISR — disabled by default, and rightly so) would restore
availability faster after certain failures but at the cost of silently losing any
messages the out-of-sync replica never received.

## 4. Architecture & Design Pattern Spotlight

**Pattern: leader-follower replication with a quorum-based durability guarantee.** This
is the same shape as Postgres synchronous replication (`synchronous_commit=on` +
`synchronous_standby_names`) — a write isn't "done" until enough replicas confirm it,
where "enough" is a tunable trade-off between durability and availability. You'll see
this exact pattern again in ClickHouse's `ReplicatedMergeTree` (Day 5) and Redis Sentinel
(Week 2).

## 5. Hands-On Lab

```bash
# 3-broker local cluster, topic with replication factor 3, min.insync.replicas=2
kafka-topics.sh --create --topic durability-test --partitions 1 \
  --replication-factor 3 --config min.insync.replicas=2 \
  --bootstrap-server localhost:9092

kafka-topics.sh --describe --topic durability-test --bootstrap-server localhost:9092
# note which broker is the Leader, which are in Isr

# kill the leader broker's process
kill -9 <leader-broker-pid>

# immediately re-describe the topic — a NEW leader should already be elected
kafka-topics.sh --describe --topic durability-test --bootstrap-server localhost:9092
```
Watch the `Isr` field shrink when you kill the leader, then watch a new `Leader` get
elected from what remains. Now try producing with `acks=all` while only 1 broker is
alive (below `min.insync.replicas=2`) and observe the producer error.

## 6. Real-World Product Comparison

- **LinkedIn** (and most serious Kafka deployments) run `acks=all` +
  `min.insync.replicas=2` + `replication.factor=3` as the standard durability baseline
  for anything that can't tolerate data loss — trading a small amount of latency for a
  concrete, provable durability guarantee.
- Compare to **Postgres synchronous replication**: the same "wait for N replicas" idea,
  but at the transaction-commit level rather than the per-record level — conceptually
  identical trade-off, different granularity.

## 7. Common Production Pitfalls

- Running with `min.insync.replicas` equal to `replication.factor` (e.g., both 3) —
  looks maximally safe, but means losing even *one* broker halts all writes entirely;
  usually the wrong trade for availability.
- Enabling unclean leader election "to reduce downtime" without understanding it can
  silently drop acknowledged messages — a durability regression disguised as an
  availability improvement.
- Not monitoring ISR shrinkage as a leading indicator — a partition running with a
  shrunk ISR for a sustained period is one more broker failure away from a full outage.

## 8. Review Questions
1. Why can only ISR members become the new leader?
2. What does `min.insync.replicas=2` with `replication.factor=3` actually guarantee, and
   what does it refuse?
3. Why is unclean leader election disabled by default?
4. How does the offset/time index let a consumer seek by timestamp without a full scan?

## 9. Proficiency Checkpoint
If you can correctly predict what happens to writes, reads, and leadership under a
single-broker failure for a given `replication.factor`/`min.insync.replicas`
combination, you're at Level 2 moving toward Level 3.

## Next
Day 5 covers KRaft mode — the Raft-based controller quorum that now runs this whole
leader-election process, having replaced ZooKeeper.
