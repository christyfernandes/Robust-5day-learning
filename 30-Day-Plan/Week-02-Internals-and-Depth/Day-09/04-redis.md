# Day 9: Redis — Sentinel: Quorum-Based Automated Failover

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Set up 3 Sentinels with 1 primary and 1 replica, kill the primary, and watch Sentinel
correctly promote the replica — and explain why a quorum of Sentinels is required.

## 2. Core Concept (basics → advanced)

**Sentinel** is a separate set of processes that monitor Redis primary/replica sets and
handle **automated failover** — detecting a dead primary and promoting a replica to
take over, without requiring manual intervention. Critically, Sentinel itself is a
small distributed system with its own agreement problem: a *single* Sentinel deciding
"the primary is dead" based only on its own view of the network could be wrong (it
might be a network partition *between that one Sentinel and the primary*, with the
primary actually fine and reachable from everywhere else) — so failover requires a
**quorum** of Sentinels to independently agree the primary is unreachable before
acting.

```
3 Sentinels monitoring 1 primary + 1 replica:

Sentinel A: "I can't reach the primary" (subjectively down)
Sentinel B: "I can't reach the primary" (subjectively down)
Sentinel C: "I CAN reach the primary" (disagrees)

→ if quorum=2, A+B agreeing is enough to mark the primary OBJECTIVELY down
→ Sentinels then elect a LEADER among themselves (via a Raft-like protocol)
→ the leader Sentinel performs the actual failover: promote the replica
```

## 3. How It Really Works (Internals)

Failure detection has two stages: a Sentinel marks the primary **subjectively down**
(SDOWN) based on its own missed heartbeats, then queries other Sentinels for their
view — if enough Sentinels (the configured `quorum`) also report SDOWN, the primary is
marked **objectively down** (ODOWN), and *then* Sentinels run their own leader-election
protocol (similar in spirit to Day 4's Raft lesson, though Sentinel's specific protocol
predates and differs in detail from Raft) to pick which single Sentinel actually
executes the failover — ensuring only one Sentinel promotes a replica, not several
racing each other.

This two-stage design (subjective → objective, and then leader election before
acting) directly guards against exactly the false-positive scenario above: a network
partition isolating *one* Sentinel from the primary shouldn't be enough, on its own, to
trigger a failover that would be entirely unnecessary and disruptive.

## 4. Architecture & Design Pattern Spotlight

**Pattern: quorum-based leader election for failure detection and action — a simpler,
more narrowly-scoped relative of the full Raft/Paxos consensus family (Week 1, Day
4).** Sentinel doesn't need to replicate an arbitrary log the way Kafka KRaft or
ClickHouse Keeper does — it only needs to agree on one specific fact ("is the primary
actually down") and coordinate one specific action (promote a replica) — a good example
of tailoring a consensus mechanism's scope to the actual problem, rather than reaching
for a full general-purpose implementation when a narrower one suffices.

## 5. Hands-On Lab

```bash
# sentinel.conf (repeat for 3 sentinel instances on different ports)
sentinel monitor mymaster 127.0.0.1 6379 2    # quorum = 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000

redis-sentinel /path/to/sentinel.conf
```
Start 1 primary, 1 replica, and 3 Sentinels configured as above. Confirm via
`redis-cli -p <sentinel-port> SENTINEL master mymaster` that Sentinel correctly
identifies the current primary. Then:
```bash
kill -9 $(pgrep -f "redis-server.*6379")   # kill the primary
```
Watch the Sentinel logs — you should see SDOWN reports, then ODOWN once quorum is
reached, then a failover promoting the replica. Confirm with `SENTINEL master
mymaster` again that the replica is now recognized as the new primary.

## 6. Real-World Product Comparison

- Sentinel's quorum-based failure detection is the same underlying discipline as
  **Kafka KRaft's** and **ClickHouse Keeper's** Raft-based quorums (Week 1, Days 4-5) —
  narrower in scope (one decision: promote or not) but built on the identical insight
  that a single node's view of "is X down" is not trustworthy enough to act on alone.
- Many teams **migrate from Sentinel to Redis Cluster** (Day 10) specifically because
  Cluster provides both sharding *and* built-in failover in one system — Sentinel
  requires pairing separately with a sharding strategy if you need both.

## 7. Common Production Pitfalls

- Setting `quorum` too low (e.g., 1) — reintroduces the false-positive-failover risk
  Sentinel's design is specifically meant to prevent.
- Running fewer than 3 Sentinels — with only 2, a single Sentinel failure makes
  reaching any meaningful quorum impossible, defeating the purpose.
- Not testing the actual failover path before relying on it in production — Sentinel
  configuration has enough moving parts (quorum, timeouts, network topology) that an
  untested setup can fail to fail over correctly exactly when it's needed most.

## 8. Review Questions
1. Why isn't a single Sentinel's "primary is down" report enough to trigger failover?
2. What's the difference between subjectively down (SDOWN) and objectively down
   (ODOWN)?
3. Why must quorum be at least a majority of Sentinels, following the same logic as
   Raft's majority requirement?
4. When would Redis Cluster be a better fit than Sentinel + separate sharding?

## 9. Proficiency Checkpoint
If you can correctly configure Sentinel quorum/timeout settings and explain why each
value was chosen, you're at Level 3.

## Next
Day 10 covers Redis Cluster — built-in sharding via hash slots, and where failover and
partitioning are handled by the same system rather than two separate ones.
