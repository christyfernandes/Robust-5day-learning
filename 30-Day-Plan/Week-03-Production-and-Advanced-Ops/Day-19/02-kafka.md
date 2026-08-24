# Day 19: Kafka — DR & Multi-Region: Geo-Replication Patterns

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Sketch an active-passive disaster-recovery topology using MirrorMaker 2, and define
what "recovered" actually means for it.

## 2. Core Concept (basics → advanced)

Building on Week 2 Day 12's MirrorMaker 2 lesson, today focuses specifically on the
**disaster recovery** use case: an **active-passive** topology where a secondary
region's cluster continuously mirrors the primary, existing purely as a failover
target — not for regional read latency, but purely so that a full regional outage of
the primary doesn't mean total data loss or extended unavailability.

```
Normal operation:                    Primary region DOWN (disaster):

Region A (PRIMARY)                   Region A: DOWN
  all production writes                        │
  │ MM2 replicates                             ▼
  ▼                                   Region B (was passive) PROMOTED
Region B (PASSIVE)                     — becomes new primary
  mirror only, no production            — clients redirected here
  writes land here directly              — some recent data MAY be lost
                                          (whatever hadn't replicated yet)
```

## 3. How It Really Works (Internals)

The critical operational question for DR is **replication lag at the moment of
failure** — since MM2 replication is asynchronous, any data written to the primary
but not yet replicated to the passive region at the exact moment of a disaster is
lost in the failover. This directly connects to Day 19's Architecture lesson's
RPO (Recovery Point Objective) framing: your actual RPO for this topology is bounded
below by your typical replication lag, not by an arbitrary target — if MM2 typically
lags by 30 seconds under normal load, your realistic RPO is "up to 30 seconds of
data loss," and any stated target tighter than that requires either reducing
replication lag or accepting the gap explicitly.

Failover itself isn't automatic with plain MM2 — promoting the passive region to
active (redirecting producers/consumers, ensuring consumer group offsets translate
sensibly, Week 2 Day 12) is typically a deliberate, orchestrated operational
procedure, not something that happens without explicit action, which matters
directly for your actual Recovery Time Objective (RTO) — how long the *procedure*
itself takes is part of your real RTO, not just detecting the outage.

## 4. Architecture & Design Pattern Spotlight

**Pattern: cross-region durability via active-passive geo-replication — the same
trade-off spectrum (async lag vs. synchronous cost) studied throughout this
curriculum's replication lessons (Kafka ISR, Week 1 Day 4; Redis replication, Week 2
Day 8), now applied at whole-region scale rather than within a single cluster.**

## 5. Hands-On Lab

Sketch an active-passive DR topology for a hypothetical 2-region deployment,
specifying explicitly:
- What's your realistic RPO, given typical MM2 replication lag under normal
  production load (estimate based on your own cluster's observed throughput and
  network characteristics)?
- What's your actual failover procedure — the concrete steps someone would follow
  to promote the passive region, and how long would that realistically take (your
  RTO)?
- Which specific topics, if any, have a tighter RPO requirement than your typical
  replication lag provides, and what would need to change (e.g., synchronous
  cross-region replication for just those topics, at a real latency cost) to meet it?

## 6. Real-World Product Comparison

- **Confluent's** multi-region Kafka reference architectures explicitly document
  this RPO/RTO framing for MM2-based DR topologies — a standard way the industry
  reasons about geo-replication trade-offs, not a bespoke framework.
- Financial services and other regulated industries often have explicit,
  contractually-required RPO/RTO targets that directly drive whether async MM2-based
  DR is sufficient or whether a more expensive synchronous cross-region approach is
  required for specific data categories.

## 7. Common Production Pitfalls

- Stating an RPO target without measuring actual typical replication lag — an
  aspirational RPO that your real infrastructure can't actually meet under
  normal conditions.
- Not having (or not testing) an actual documented failover procedure — discovering
  the real RTO only during an actual disaster, when it's too late to improve it.
- Assuming DR readiness is "done" once MM2 is configured, without periodic failover
  drills to confirm the procedure still works as infrastructure and topic
  configurations evolve over time.

## 8. Review Questions
1. Why is your realistic RPO bounded below by typical replication lag, not an
   arbitrary target?
2. What does RTO actually measure, beyond just "how long until we notice the
   outage"?
3. Why might different topics reasonably have different RPO requirements within the
   same cluster?
4. Why is periodic failover testing necessary even after DR is initially configured?

## 9. Proficiency Checkpoint
If you can define realistic RPO/RTO targets for a real topology and identify the gap
between aspiration and actual measured capability, you're at Level 3.5.

## Next
Day 20 covers Kafka's managed alternatives — Confluent Cloud, MSK, Redpanda,
Pulsar — for teams weighing self-hosted DR complexity against a managed offering.
