# Day 4: Architecture — Consensus: Paxos & Raft

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain what a consensus algorithm actually guarantees, walk through a Raft leader
election on paper, and name where Raft runs underneath tools you already use.

## 2. Core Concept (basics → advanced)

**Consensus** is the problem of getting multiple nodes to agree on a single value (or a
single ordered sequence of values) despite failures and network delays — foundational
to anything requiring "exactly one leader" or "one agreed-upon log order" in a
distributed system.

**Paxos** (the original, 1989) is famously correct but famously hard to understand and
implement — most real systems today use **Raft**, designed explicitly to be an
equivalent-strength but *understandable* consensus algorithm. Raft breaks the problem
into three separate sub-problems:
- **Leader election**: exactly one node becomes leader for a given "term" (a
  monotonically increasing epoch number).
- **Log replication**: the leader appends entries and replicates them to followers;
  an entry is **committed** once a majority of nodes have it.
- **Safety**: a set of rules ensuring a new leader always has all previously-committed
  entries (so committed data is never lost across leader changes).

```
Term 1: Node A is leader ──▶ replicates log to B, C
        (A crashes)
Term 2: B and C time out waiting for A's heartbeat → each may become a candidate
        → whichever gets a MAJORITY vote (here, needs 2 of 3) becomes leader
        → say C wins → C is leader for term 2, A (if it returns) steps down
```

## 3. How It Really Works (Internals)

Each node is a **follower**, **candidate**, or **leader**. Followers expect periodic
heartbeats from the leader; if a randomized election timeout elapses with no heartbeat,
a follower becomes a **candidate**, increments the term number, votes for itself, and
requests votes from peers. A node grants its vote to at most one candidate per term, and
a candidate becomes leader once it wins a **majority** of votes — the randomized timeout
(different per node) is specifically there to make split votes (multiple simultaneous
candidates) unlikely, and if one does happen, the random timeouts naturally desynchronize
on the next round.

Crucially, an entry is only **committed** (safe to act on) once replicated to a
majority — this is exactly the same "quorum" idea as Kafka's ISR/`min.insync.replicas`
(Day 4's Kafka lesson) and ClickHouse Keeper's own Raft-based coordination (Day 5) —
consensus algorithms and quorum-based replication are solving deeply related problems
with the same underlying mathematical guarantee: majorities of overlapping sets always
intersect, so at most one leader/value can ever be agreed upon per term.

## 4. Architecture & Design Pattern Spotlight

**Pattern: majority-quorum consensus as the foundation of leader election.** Once you
recognize "needs a majority of N nodes to agree" as the core primitive, you'll see it
everywhere this month: Kafka's KRaft controller quorum (Day 5), ClickHouse Keeper
coordinating your actual production cluster (Day 5), and etcd/ZooKeeper underneath
Kubernetes' own control plane. This is arguably the single most reused idea in all of
distributed systems.

## 5. Hands-On Lab

No code today — trace it on paper. Given a 5-node cluster (A, B, C, D, E) with A as the
current leader in term 3:
1. A crashes. Which nodes can become candidates, and what's the minimum number of votes
   needed to win?
2. Suppose B and D both become candidates simultaneously in term 4, and the vote
   splits 2-2-1 with no majority. What happens next (in terms of Raft's actual
   mechanism, not "it just retries")?
3. D wins term 5. What must be true about D's log, relative to A's last committed
   entries, for Raft's safety guarantee to hold?

## 6. Real-World Product Comparison

- **Kafka's KRaft mode** (replacing ZooKeeper) runs an actual Raft implementation for
  the *controller quorum* — cluster metadata (topic configs, partition assignments)
  now flows through the same kind of consensus log described above, rather than a
  separate ZooKeeper ensemble.
- **ClickHouse Keeper** is ClickHouse's own Raft-based replacement for the ZooKeeper
  dependency that `ReplicatedMergeTree` originally required — literally the coordination
  layer your live 3-node cluster runs today.
- **etcd** (Raft-based) underlies Kubernetes' entire control plane's consistency
  guarantees — every `kubectl apply` ultimately depends on a Raft-committed write.

## 7. Common Production Pitfalls

- Running a consensus-coordinated cluster with an **even** number of nodes — doesn't
  improve fault tolerance over one fewer node (majority math is the same or worse) and
  just adds cost; always prefer an odd count (3, 5) for the coordination layer.
- Misunderstanding "the cluster is up" as "consensus is healthy" — a quorum-based system
  can be serving *some* traffic while its coordination layer is degraded and one more
  failure away from a full outage.
- Not monitoring leader-election frequency — frequent, unexpected re-elections (rather
  than one-time events) usually indicate network flakiness or resource starvation on the
  coordination nodes themselves.

## 8. Review Questions
1. Why does Raft use randomized election timeouts specifically?
2. What does "committed" mean in Raft, precisely, and why does it require a majority?
3. Why is an odd node count almost always preferred for a consensus-coordinated cluster?
4. Name two systems you already use daily whose availability depends on a Raft
   (or Raft-like) quorum underneath.

## 9. Proficiency Checkpoint
If you can walk through a leader-election and log-replication scenario on paper and
correctly reason about what's safe to commit, you're at Level 2 moving firmly into
Level 3 territory on distributed systems fundamentals.

## Next
Day 5 goes to distributed transactions — 2PC, Saga, and Outbox — the next layer up
from "one agreed value" to "one agreed *multi-step business operation* across services."
