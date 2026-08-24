# Day 1: Architecture & System Design — CAP Theorem & Consistency Models

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
State the CAP theorem correctly (most people misstate it), explain why PACELC is the
more useful framing in practice, and map today's other 6 tracks onto specific points
on the consistency spectrum.

## 2. Core Concept (basics → advanced)

**CAP theorem, precisely.** During a **network partition** (P — some nodes can't talk
to others), a distributed system must choose between **Consistency** (every read sees
the latest write) and **Availability** (every request gets a response, even if it might
be stale). You do *not* get to choose all three, but note the precise condition: this
trade-off only *bites* during an actual partition. The common mistake is treating CAP as
"pick 2 of 3, always" — in reality, partitions are rare-ish events, and the real design
question is what your system does *during* one.

**PACELC — the more useful extension.** Even *without* a partition (E — else), you
still choose between **Latency** and **Consistency** for every replicated system: wait
for all replicas to agree (consistent, slower) or respond from the nearest replica
(fast, possibly stale). This is the trade-off you're making *every single day*, not
just during rare partition events — which is why PACELC is the framing that actually
predicts real system behavior.

```
        Partition happens?
         /            \
       Yes             No
        │               │
   choose C or A    choose Latency or Consistency
   (CAP)            (the "ELC" part of PACELC)
```

**Consistency models, roughly ordered strong → weak:**
- **Strong/linearizable** — reads always see the most recent write, system-wide.
- **Causal** — if A happened-before B, everyone who sees B also sees A (but unrelated
  writes can be seen in different orders by different readers).
- **Eventual** — given no new writes, all replicas *eventually* converge, with no
  guarantee on how long "eventually" takes.

## 3. How It Really Works (Internals)

Map real systems from today's other tracks onto this spectrum, concretely:
- **Kafka** with `acks=all` and `min.insync.replicas=2`: chooses consistency (a write
  isn't acknowledged until enough replicas have it) over availability during a
  partition — if too few replicas are reachable, writes are rejected rather than risk
  data loss.
- **Redis** (standalone, async replication): chooses availability/low latency by
  default — a write is acknowledged before followers confirm it, so a follower promoted
  during a partition can be momentarily behind (a small, real consistency gap).
- **Elasticsearch/ClickHouse replicas**: tunable per query/write — you can ask for
  stronger read guarantees at a latency cost, or accept eventual consistency for speed.

This is the payoff of Day 1's Architecture track: you're not learning CAP in the
abstract, you're building a lens that makes every other tool's replication choice
legible as *the same underlying decision*, made differently.

## 4. Architecture & Design Pattern Spotlight

**Pattern: the CAP/PACELC framework itself**, used as a design tool. When you evaluate
any new distributed system, ask: (1) what does it do during a partition — reject
writes, or serve possibly-stale reads? (2) even without a partition, does it favor
lowest latency or strongest consistency by default, and is that tunable? Answering
these two questions for a new tool gets you 80% of the way to understanding its
behavior under stress, before you've read a line of its internals.

## 5. Hands-On Lab
For each of today's other 6 tracks, write one sentence: "Under a network partition, X
chooses ______ because ______." Use what you learned in today's other lessons — you
already have the raw material (Kafka's ISR/acks, Redis's async replication,
Elasticsearch's/ClickHouse's replica model). This exercise is the actual skill: turning
a system's documented behavior into a CAP/PACELC statement.

## 6. Real-World Product Comparison

- **DynamoDB** (Amazon) was explicitly designed around the "leaderless, eventually
  consistent, always-available" end of the spectrum — the original Dynamo paper is the
  most-cited justification for choosing availability over strict consistency at scale.
- **Spanner** (Google) takes the opposite bet: strong external consistency across
  globally distributed replicas, paid for with atomic clocks (TrueTime) and higher write
  latency — a genuinely different trade-off, not a "worse" one.
- **Kafka and ClickHouse Keeper** both use **Raft** underneath (Day 4) specifically
  because they need strong consistency for *metadata* (who's the leader, what's
  committed) even while the bulk data path may make different trade-offs elsewhere.

## 7. Common Production Pitfalls
- Treating CAP as "pick 2 of 3, forever" instead of "what happens during a partition,
  specifically" — this misreading leads to bad system comparisons in interviews and
  design docs alike.
- Assuming "eventual consistency" means "eventually, soon" — with no SLA on
  convergence time, "eventual" can, in pathological cases, be a very long time.
- Picking a consistency model as a one-time global decision instead of per-operation —
  most real systems (including several you'll use this month) let you tune this per
  read/write.

## 8. Review Questions
1. What specifically has to be true for the CAP trade-off to actually bite?
2. Why is PACELC a more complete model of real-world system behavior than CAP alone?
3. Give one concrete example (from today) of a system choosing availability over
   consistency, and one choosing the opposite.
4. Why do Kafka and ClickHouse both use Raft for metadata even if their main data path
   makes different trade-offs?

## 9. Proficiency Checkpoint
If you can correctly state CAP (without the common "pick 2 of 3, always" error) and
classify at least 3 of today's tools by their CAP/PACELC trade-off, you're at Level 2.

## Next
Day 2 covers replication strategies concretely — leader-follower, multi-leader, and
leaderless/quorum — the mechanisms that actually implement the consistency choices
discussed today.
