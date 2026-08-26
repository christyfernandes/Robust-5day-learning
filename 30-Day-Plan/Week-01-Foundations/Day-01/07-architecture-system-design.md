# Day 1: Architecture & System Design — CAP Theorem & Consistency Models

## Time: ~30 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
State the CAP theorem correctly (most people misstate it), explain why PACELC is the
more useful framing in practice, and map today's other 6 tracks onto specific points
on the consistency spectrum.

## 2. Core Concept (basics → advanced)

**Start here if this is genuinely new territory.** When a system's data lives on more
than one machine (a **distributed system**) — which is true of every tool you're
studying this month except a single laptop-only script — three properties become
things you have to actively think about, rather than getting for free the way you
would on one machine:
- **Consistency**: does every read see the most recent write, no matter which machine
  answers it?
- **Availability**: does every request get *some* response, even if that machine can't
  currently confirm it has the absolute latest data?
- **Partition tolerance**: does the system keep working at all when some machines
  temporarily can't talk to others (a **network partition** — e.g., a network cable
  gets unplugged, or two data centers lose their link to each other)?

**CAP theorem, precisely.** During an actual network partition, a distributed system
must choose between **Consistency** and **Availability** — it cannot have both at that
moment. (Why not? If part of the system can't hear from the rest, it can either refuse
to answer at all until it's sure it has the latest data — sacrificing availability —
or answer anyway with whatever data it has locally, which might be stale — sacrificing
consistency. There's no third option once the network link is actually down.) The
common mistake is treating CAP as "pick 2 of 3, always, everywhere" — in reality, this
trade-off only *bites* during an actual partition, which for most systems is a
relatively rare event; the real design question is what your system does *during* one,
not some permanent global setting.

**PACELC — the more useful extension.** Even *without* a partition (**E**, "else"), you
still choose between **Latency** and **Consistency** for every replicated system, every
single day: wait for all replicas to confirm they agree (consistent, but slower) or
respond immediately from the nearest replica (fast, but that replica might be a moment
behind the true latest value). This is the trade-off you're actually making constantly
in normal operation — which is why PACELC (Partition → Availability or Consistency;
Else → Latency or Consistency) is the framing that actually predicts real system
behavior, not just the rare-event case CAP alone describes.

```
        Partition happens?
         /            \
       Yes             No
        │               │
   choose C or A    choose Latency or Consistency
   (CAP)            (the "ELC" part of PACELC)
```

**Consistency models, roughly ordered strong → weak:**
- **Strong/linearizable** — reads always see the most recent write, system-wide, no
  exceptions.
- **Causal** — if A happened-before B, everyone who sees B also sees A (but two
  unrelated writes can still be seen in different orders by different readers).
- **Eventual** — given no new writes, all replicas *eventually* converge on the same
  value, but with no guarantee on how long "eventually" actually takes.

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

### Sample Completed Exercise

Since this lab produces written sentences rather than a tool's output, here's what a
correctly-reasoned answer looks like for two of today's tracks — use these as the
calibration for the other five, not something to copy for them:

> **Kafka** (with `acks=all`, `min.insync.replicas=2`): under a partition that leaves
> fewer than 2 in-sync replicas reachable, Kafka chooses **consistency over
> availability** — it will actively **reject** new writes to that partition rather
> than risk acknowledging one that could be silently lost, because the whole point of
> `min.insync.replicas` is a durability guarantee the system refuses to quietly break.

> **Redis** (standalone, default async replication): under a partition between a
> primary and its replica, Redis chooses **availability over consistency** — the
> primary keeps accepting writes and responding to clients immediately without waiting
> for the replica to confirm anything, so if that replica is later promoted (Sentinel,
> Week 2 Day 9) it may be missing the primary's most recent writes; the system stays
> "up," but a specific write can be silently lost from the replica's point of view.

Notice the shape both answers share: name the *specific configuration/mechanism*
responsible (not just "Kafka is consistent"), and state *what actually happens* to a
request during the partition (rejected? served with possibly-stale data?) — a strong
answer for the other five tracks should have that same concrete, mechanism-and-
consequence shape, not just a label like "eventually consistent."

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
<details><summary>Show answer</summary>

There has to be an actual network partition happening right now — some nodes unable
to communicate with others. Outside of a partition, a distributed system can, in
principle, be both consistent and available simultaneously; CAP's forced choice only
applies during the partition itself, not as some permanent, always-active constraint.

</details>

2. Why is PACELC a more complete model of real-world system behavior than CAP alone?
<details><summary>Show answer</summary>

Because partitions are relatively rare, but every single request to a replicated
system — partition or no partition — involves a real latency-vs-consistency choice
(wait for replicas to confirm agreement, or respond fast from the nearest one).
PACELC captures both the rare-event trade-off (CAP's P → A-or-C) and the constant,
everyday trade-off (PACELC's else → L-or-C), where CAP alone only describes the rare
case.

</details>

3. Give one concrete example (from today) of a system choosing availability over
   consistency, and one choosing the opposite.
<details><summary>Show answer</summary>

Redis with default async replication chooses availability over consistency — it
keeps serving writes immediately without waiting for replica confirmation. Kafka
configured with `acks=all` and `min.insync.replicas=2` chooses consistency over
availability — it will reject writes rather than risk acknowledging one that isn't
safely replicated.

</details>

4. Why do Kafka and ClickHouse both use Raft for metadata even if their main data path
   makes different trade-offs?
<details><summary>Show answer</summary>

Because metadata (who is the current leader, what has actually been committed) is
exactly the kind of information where being wrong even briefly can cause real
correctness problems (like two nodes both believing they're the leader) — so both
systems deliberately pay Raft's stronger-consistency cost specifically for that
narrow, critical piece of state, even while allowing looser trade-offs elsewhere (like
Kafka's tunable `acks` for the actual data path, or ClickHouse's async replica fetch
for bulk data, Week 1 Day 5).

</details>

## 9. Proficiency Checkpoint

**Quick Recap:**
- **CAP** applies only *during* an actual network partition: choose Consistency
  (reject/delay requests until certain) or Availability (answer anyway, possibly
  stale) — never both at that moment.
- **PACELC** extends this to *all* the time, partition or not: Else, choose Latency
  (answer fast, possibly stale) or Consistency (wait for replica agreement, slower).
- **Strong consistency**: always the latest write, everywhere. **Eventual
  consistency**: converges *eventually*, no guaranteed timeframe.
- A strong CAP/PACELC classification of any tool names the **specific mechanism**
  (a config flag, a replication behavior) and the **concrete consequence** during a
  partition — not just a label.
- **Kafka** (`acks=all`, `min.insync.replicas`) → leans consistency. **Redis**
  (default async replication) → leans availability. Both **Kafka's and ClickHouse's
  metadata layers** → strong consistency via Raft, regardless of their main data
  path's choice.

If you can correctly state CAP (without the common "pick 2 of 3, always" error) and
classify at least 3 of today's tools by their CAP/PACELC trade-off, you're at Level 2.

## Next
Day 2 covers replication strategies concretely — leader-follower, multi-leader, and
leaderless/quorum — the mechanisms that actually implement the consistency choices
discussed today.
