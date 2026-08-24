# Day 27 — Interview-Readiness & Mock Review

## Time: ~3-4 hours | Proficiency target: Level 4 confirmed across all 7 tracks

Today has two parts: answering staff/architect-level design questions out loud,
unaided (simulating a real interview or design review), and a structured mock
Principal Architect review of your actual Day 25 capstone design. Both are
meant to be genuinely uncomfortable — that discomfort is the point.

## Part 1 — Staff/Architect-Level Design Questions (~2 hours)

For each question, give yourself 15-20 minutes to answer **out loud, unaided** —
no notes, no re-reading this month's lessons mid-answer. Then compare your
answer against the "what a strong answer covers" checklist, and note any gaps.

### PySpark: "Design a batch ETL platform for 50TB/day with strict SLAs."
**A strong answer covers:** cluster sizing and capacity planning reasoning
(Week 3, Day 15), executor/memory configuration with overhead accounted for
(Week 2, Day 9), shuffle-partition tuning at this data volume (Week 2, Day 10;
Week 3, Day 15), a Medallion-style layered pipeline (Day 22), SLA framing via
SLIs/SLOs and error budgets (Week 3, Day 16), and cost-awareness (spot
instances/autoscaling, Week 3 Day 19; managed-vs-self-hosted TCO, Week 3 Day
20).

### Kafka: "Design an event backbone for a multi-region e-commerce platform."
**A strong answer covers:** partition/topic design for the relevant entities
(Week 1, Day 3), replication and `min.insync.replicas` durability choices
(Week 1, Day 4), exactly-once semantics where correctness demands it (Week 2,
Day 9), multi-region topology (active-active vs. active-passive, with the
CRDT vs. manual-conflict-resolution trade-off, Week 3 Day 19), and concrete
RPO/RTO targets (Week 3, Day 19).

### Flink: "Design a real-time fraud-detection pipeline with sub-second latency."
**A strong answer covers:** true streaming vs. micro-batch justification
(Week 1, Day 1), event-time/watermark correctness (Week 1, Day 3), CEP for
sequence-pattern detection (Week 2, Day 12), exactly-once sink guarantees
where needed (Week 2, Day 9), backpressure/scaling considerations (Week 2,
Day 11; Week 2, Day 13), and JobManager HA (Week 3, Day 18).

### Redis: "Design a distributed cache for a read-heavy social feed."
**A strong answer covers:** cache-aside vs. read-through pattern choice
(Week 2, Day 11), key design avoiding hot/big keys (Week 3, Day 15), Cluster
sharding for horizontal scale (Week 2, Day 10), Sentinel/Cluster failover
(Week 2, Day 9-10), and an explicit staleness-tolerance statement.

### Elasticsearch: "Design a search platform for a marketplace with faceted filters."
**A strong answer covers:** mapping design (nested vs. object vs. parent-
child, Week 2, Day 10), aggregation-based faceting (Week 1, Day 4), relevance
tuning (BM25 parameters, Week 2, Day 9), cluster/shard sizing (Week 3, Day
15), and — critically — an explicit justification for *why* Elasticsearch
rather than ClickHouse fits this specific use case (Week 4, Day 24's
decision framework, applied correctly in the direction that favors ES here).

### ClickHouse: "Design a real-time analytics platform to replace a BigQuery-based one."
**A strong answer covers:** sharding key selection with cardinality reasoning
(Week 1, Day 4), OBT/star-schema/dictionary schema decisions (Week 4, Day
22), hot/cold tiering (Week 2, Day 10), the fan-out risk and its structural
fix (Week 2, Day 9/11), native Kafka ingestion (Week 2, Day 13), and — this
is your own real answer — the actual TCO comparison (Week 3, Day 20).

### Architecture: Mock Principal Architect Review (~90 min)

Present your actual Day 25 MDO portal migration design (or have a colleague,
or an AI in a role-play capacity, act as a skeptical Principal Architect
reviewer) and defend against at least these challenges:

1. **"Why not just optimize your existing BigQuery queries instead of
   migrating at all?"** — defend using Day 20's three-way cost comparison
   (current / corrected / migrated), showing the migration's benefit beyond
   what query optimization alone would capture.
2. **"Why ClickHouse and not Druid or Pinot?"** — defend using Day 24's
   comparison framework and your own workload's specific characteristics
   (query patterns, team familiarity, ecosystem fit).
3. **"What happens if your sharding key choice turns out to be wrong once
   real production traffic hits it?"** — defend using Week 1 Day 4's
   sharding-key reasoning and describe a concrete remediation path (the
   actual operational cost of correcting a sharding-key mistake).
4. **Pick one more challenge yourself** — ideally the question you're most
   worried about being asked, since that's the one worth rehearsing most.

For each challenge, a strong defense doesn't just assert an answer — it
cites the specific evidence (a measured number, a specific lesson's
reasoning) that makes the answer credible, exactly the evidence-grounded
discipline Day 25's lessons emphasized throughout.

## Self-Assessment

Update your Week 4 row (and, if not already done, your final overall
assessment) in [`../PROGRESS_TRACKER.md`](../PROGRESS_TRACKER.md). You should
be at Level 4 across all 7 tracks — not just able to explain concepts, but able
to design, defend, and know when *not* to use each system.

**Checkpoint:** if you can answer all seven design questions unaided and
defend your real capstone design against genuine, skeptical challenges, you've
completed the core proficiency arc this 30-day curriculum was built around.

## Next
The Capstone (Days 28-30) is a single integrated build/document/assess project
— apply everything from this month in one final, hands-on undertaking.
