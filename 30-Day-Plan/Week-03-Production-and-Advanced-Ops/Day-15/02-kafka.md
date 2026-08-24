# Day 15: Kafka — Cluster Sizing & Capacity Planning

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Given a target events/sec and retention window, calculate the required partition
count and disk capacity for a Kafka cluster.

## 2. Core Concept (basics → advanced)

Capacity planning for Kafka comes down to two connected calculations:

**Partition count**, driven by required *parallelism* (how many consumers can work in
parallel, Week 1 Day 3) and *per-partition throughput ceiling* (a single partition has
a practical throughput limit, commonly in the tens of MB/sec range depending on
hardware) — you need enough partitions that your target throughput divided across
them stays comfortably under that per-partition ceiling, **and** enough partitions to
support your target consumer parallelism.

**Disk capacity**, driven directly by retention: `disk_needed = bytes_per_second ×
retention_seconds × replication_factor` — replication factor multiplies storage
requirement because every replica (Week 1, Day 4) needs its own full copy of the data.

```
Target: 50,000 events/sec, 1KB avg size, 7-day retention, replication factor 3

Throughput: 50,000 × 1KB = ~50 MB/sec
Disk needed: 50 MB/sec × (7 × 86400 sec) × 3 replicas ≈ 90 TB total cluster disk

Partition count: if one partition handles ~10MB/sec comfortably,
  need at least 50MB/sec ÷ 10MB/sec = 5 partitions for throughput alone —
  but also check target consumer parallelism (Week 1, Day 3) and round up further
```

## 3. How It Really Works (Internals)

This calculation must also account for **tiered storage** (Week 2, Day 10) if
configured — hot-tier disk sizing only needs to cover the hot retention window, with
the remainder living in cheaper object storage, meaningfully changing the "disk
needed" calculation's practical cost even though the *logical* retention period is
unchanged. It's also worth explicitly sizing for **headroom against traffic
spikes**, not just steady-state average throughput — a cluster sized exactly to
average load has no buffer for the burst traffic that real production systems
regularly experience, and Kafka's per-partition throughput ceiling means a burst
that exceeds provisioned capacity manifests as growing producer-side latency or
buffering, not a clean, obvious failure.

## 4. Architecture & Design Pattern Spotlight

**Pattern: capacity planning from first-principles throughput + retention math,
validated against real per-partition/per-broker ceilings.** This is the same kind of
grounded, formula-driven estimation as the PySpark executor-sizing calculation
(Week 2, Day 9) — deriving a concrete number from stated requirements and known
system constraints, rather than guessing or copying another team's configuration.

## 5. Hands-On Lab

Given: target throughput of 20,000 events/sec at 2KB average size, a 14-day retention
requirement, and a replication factor of 3, calculate:
- Total bytes/sec, and total disk capacity needed across the cluster.
- A reasonable partition count, given an assumed ~15MB/sec practical per-partition
  ceiling, plus a target consumer-group parallelism of at least 12.
- If tiered storage moves data older than 3 days to object storage, recalculate the
  *hot-tier* disk requirement specifically, and compare it to the full 14-day figure.

## 6. Real-World Product Comparison

- **Confluent's** and **AWS MSK's** sizing calculators formalize exactly this kind of
  math into a guided tool — useful as a sanity check, but understanding the
  underlying formula (rather than treating the calculator as a black box) is what lets
  you reason about edge cases the calculator's defaults might not cover.
- This same throughput/retention/replication calculation shape recurs directly in
  **ClickHouse cluster sizing** (Day 20) and generally in any system where "how much
  storage do I need" depends on ingest rate × retention × redundancy factor.

## 7. Common Production Pitfalls

- Sizing for average throughput without headroom for realistic traffic bursts.
- Under-provisioning partition count for target consumer parallelism, discovering
  the ceiling only once trying to scale consumers past the partition count allows.
- Forgetting that replication factor multiplies storage cost directly — a
  seemingly small increase from `replication.factor=2` to `3` is a 50% storage cost
  increase, not a rounding error.

## 8. Review Questions
1. What are the two separate calculations capacity planning combines?
2. Why does tiered storage change the practical disk-sizing calculation?
3. Why must sizing account for burst traffic, not just steady-state average?
4. Why does replication factor directly multiply total storage cost?

## 9. Proficiency Checkpoint
If you can derive partition count and disk sizing from stated throughput/retention/
replication requirements, you're at Level 3.5.

## Next
Day 16 covers reliability configuration in depth — unclean leader election and
`min.insync.replicas` — the durability side of the capacity/reliability trade-off.
