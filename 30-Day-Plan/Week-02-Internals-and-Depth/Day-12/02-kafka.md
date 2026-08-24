# Day 12: Kafka — Multi-Cluster: MirrorMaker 2

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Sketch a MirrorMaker 2 topology for a 2-region setup, and explain the difference
between active-active and active-passive replication.

## 2. Core Concept (basics → advanced)

**MirrorMaker 2 (MM2)** replicates topics between Kafka clusters — commonly across
geographic regions, for disaster recovery or to serve regional consumers with local
low-latency reads. Two topology philosophies:

- **Active-passive**: one region's cluster is the primary (all production writes go
  there); a secondary region's cluster mirrors it purely for failover readiness — under
  normal operation, the secondary is read-only from an application's point of view.
- **Active-active**: both regions' clusters accept production writes independently,
  and MM2 replicates each region's topics to the other — genuinely more available
  (either region can serve writes at any time) but introduces a real conflict question:
  what happens when the *same logical entity* is written to in both regions nearly
  simultaneously?

```
Active-passive:      Active-active:

Region A (primary)   Region A ◄──MM2──► Region B
   │  writes            (both write, both replicate to each other —
   ▼ MM2                 conflict resolution becomes YOUR problem to solve,
Region B (standby,        not Kafka's, if the same key is written in both)
 read-only until
 failover)
```

## 3. How It Really Works (Internals)

MM2 is itself built on **Kafka Connect** (Day 13's topic) — it runs as a set of
Connect connectors (a source connector reading from the origin cluster, a sink-like
mechanism writing to the destination), and it automatically handles topic renaming
(commonly prefixing mirrored topics with the source cluster's name, to avoid naming
collisions in active-active setups), offset translation (since a consumer's committed
offset in the source cluster doesn't automatically make sense in the destination
cluster's copy of the same data), and consumer-group state replication (so a consumer
group failing over from Region A to Region B can resume from approximately the correct
position rather than starting over).

The active-active conflict question has no generic Kafka-level answer — MM2 faithfully
replicates whatever was written in each region, but if both regions accept an update to
"the same logical record" independently, resolving that conflict (last-write-wins by
timestamp, an application-level merge rule, or preventing the conflict from being
possible in the first place via key-based regional partitioning) is an application
architecture decision, not something MM2 solves for you.

## 4. Architecture & Design Pattern Spotlight

**Pattern: geo-replication for disaster recovery, with a real consistency trade-off
in the active-active case.** This is architecturally the same class of decision as
choosing eventual vs. strong consistency (Week 1, Day 7's ADR exercise) — active-
active gives you better availability and lower regional latency at the cost of needing
an explicit conflict-resolution strategy; active-passive avoids that complexity by
accepting that only one region is ever the source of truth at a time.

## 5. Hands-On Lab

No code today — sketch a topology. For a hypothetical 2-region (US, EU) deployment
with a requirement that "if either region's Kafka cluster fails entirely, consumers
should be able to fail over within minutes, and writes from users physically in each
region should have reasonably low latency to their local cluster," decide:
- Active-active or active-passive, and why?
- If active-active, which specific keys/entities (if any) are safe to allow
  independent writes to in both regions, and which need to be pinned to a single
  region's cluster to avoid conflicts entirely?
- What does your consumer failover plan look like given MM2's offset translation
  behavior?

## 6. Real-World Product Comparison

- **Confluent's** commercial multi-region Kafka offerings build additional tooling on
  top of MM2 specifically to handle the active-active conflict problem more gracefully
  for common use cases (e.g., regionally-partitioned keys that never actually conflict
  by design).
- Many companies with global user bases (similar in spirit to how a global streaming
  or social platform operates) explicitly pin specific entity types (e.g., "this
  user's account lives in exactly one home region") to sidestep the active-active
  conflict problem structurally, rather than solving it generically.

## 7. Common Production Pitfalls

- Choosing active-active without a concrete plan for conflict resolution, discovering
  the problem only when a real conflict occurs in production.
- Not testing consumer group failover in advance — offset translation approximations
  can mean a failed-over consumer either reprocesses some messages or skips some,
  depending on configuration; know which, and whether your consumers can tolerate it.
- Underestimating replication lag during a regional network degradation — MM2
  replication is asynchronous, and lag can grow silently during partial network
  issues well before a full regional outage makes the problem obvious.

## 8. Review Questions
1. What's the fundamental trade-off between active-active and active-passive
   topologies?
2. Why does active-active introduce a conflict-resolution problem that Kafka itself
   doesn't solve?
3. What does MM2's offset translation approximate, and why is it only approximate?
4. What's one way to structurally avoid the active-active conflict problem rather
   than solving it generically?

## 9. Proficiency Checkpoint
If you can design a multi-region topology for a stated availability/latency
requirement and correctly identify its conflict-resolution needs, you're at Level 3.

## Next
Day 13 covers Kafka Connect and Debezium CDC — the connector framework MM2 itself is
built on, applied to change-data-capture from a database instead of cluster-to-cluster
replication.
