# Day 19: Architecture — Multi-Region & DR: RPO/RTO Framing

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Define concrete RPO/RTO targets for one real component of your platform, grounded
in actual measured behavior rather than aspiration.

## 2. Core Concept (basics → advanced)

Two precise, distinct metrics for reasoning about disaster recovery, both
introduced informally in today's Kafka lesson but worth defining exactly:

- **RPO (Recovery Point Objective)**: how much data you can afford to lose,
  measured in time — "an RPO of 5 minutes" means you can tolerate losing up to 5
  minutes' worth of data in a disaster, no more.
- **RTO (Recovery Time Objective)**: how long you can afford to be down — "an RTO of
  1 hour" means recovery (getting the system back to serving traffic, even if not
  fully caught up) must complete within 1 hour.

```
Timeline of a disaster:

  ...normal operation...  [DISASTER STRIKES]  ...recovery in progress...  [RECOVERED]
                                │                                              │
                                │◄──────────── RTO ─────────────────────────►│
                                                                              
  Data written in this window ◄─┤ RPO
  is potentially LOST
```

**Active-active vs. active-passive** (touched on in Kafka's Day 12 and Day 19
lessons, and Redis's CRDT lesson today) is fundamentally a trade between RPO/RTO
tightness and cost/complexity — active-active can offer near-zero RTO (both
regions always serving) but requires either CRDTs (today's Redis lesson) or
application-level conflict resolution; active-passive is simpler to reason about
but has a real RTO cost (failover takes time) and an RPO bounded by replication lag.

## 3. How It Really Works (Internals)

The crucial discipline: **RPO/RTO targets must be grounded in what your actual
infrastructure can deliver, not aspirational numbers chosen independently of
measured reality.** An RPO target tighter than your actual observed replication lag
(Kafka's MM2 lag, Day 19; Redis replication lag, Week 2 Day 8) is not a real target
— it's a number that will be violated the first time it's tested against an actual
disaster, unless you invest in tightening the underlying replication mechanism to
actually support it (e.g., synchronous rather than asynchronous replication for
specific critical data, at a real performance cost).

## 4. Architecture & Design Pattern Spotlight

**Pattern: recovery objective framing — RPO/RTO as the precise vocabulary for a
trade-off studied all week in system-specific terms (Kafka replication lag, Redis
CRDTs, Elasticsearch snapshots, ClickHouse backup).** This is the unifying
cross-system framework that lets you compare DR readiness across genuinely
different systems using one consistent measure, rather than each system's DR
story living in its own isolated vocabulary.

## 5. Hands-On Lab

For one real component of your platform (the ClickHouse cluster, the Kafka
pipeline, or the whole MDO portal end to end), define:
- A concrete RPO target, grounded in an actual measurement of current replication/
  backup lag for that component — not an aspirational number.
- A concrete RTO target, grounded in an actual (or realistically estimated) failover
  procedure duration — including detection time, decision time, and execution time,
  not just "how fast could the technical failover step complete in an ideal world."
- Identify the single biggest gap between your stated target and current measured
  reality, and what concrete investment (synchronous replication for specific data?
  a tested, documented failover runbook? more frequent backups?) would close it.

## 6. Real-World Product Comparison

- **Financial services and healthcare** industries often have regulatory RPO/RTO
  requirements that directly drive infrastructure investment decisions (e.g.,
  mandating synchronous cross-region replication for specific transaction data
  despite its cost) — a concrete example of RPO/RTO targets driving real
  architectural decisions, not just documentation exercises.
- Most cloud providers' own DR reference architectures (AWS, GCP) are explicitly
  organized around RPO/RTO tiers, from "backup and restore" (cheapest, loosest
  targets) through "pilot light," "warm standby," to "multi-site active-active"
  (most expensive, tightest targets) — a useful mental model for where your own
  target architecture sits on this spectrum.

## 7. Common Production Pitfalls

- Stating RPO/RTO targets that sound reassuring but were never validated against
  actual measured system behavior — a false sense of DR readiness.
- Choosing a DR tier (active-active, warm standby, backup-and-restore) without
  explicitly connecting the choice to a stated RPO/RTO requirement — the tier
  should be *derived from* the requirement, not chosen first and rationalized after.
- Not periodically re-validating RPO/RTO targets as the underlying system's actual
  behavior changes (e.g., replication lag increasing as data volume grows) —
  targets that were once realistic can silently become aspirational again.

## 8. Review Questions
1. What's the precise distinction between RPO and RTO?
2. Why must RPO/RTO targets be grounded in measured reality, not aspiration?
3. How does the active-active/active-passive choice map onto RPO/RTO trade-offs?
4. Where does your own platform sit on the backup-and-restore-to-active-active
   spectrum, and is that the right place given actual business requirements?

## 9. Proficiency Checkpoint
If you can define real, measurement-grounded RPO/RTO targets for an actual platform
component and identify the gap to current reality, you're at Level 3.5 — directly
useful for your ongoing platform hardening work.

## Next
Day 20 covers cost-aware architecture broadly — FinOps and build-vs-buy — the final
major theme before Day 21's integrated review.
