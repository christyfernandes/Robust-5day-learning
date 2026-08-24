# Day 14 — Lab + Week 2 Review

## Time: ~4 hours | Proficiency target: Level 3 confirmed across all 7 tracks

This is the week's most directly work-relevant lab day — every exercise below maps
onto a real production system you operate. Work through each track, producing an
actual written artifact (root-cause notes, a fix, a diagram) you could hand to a
teammate.

## 1. PySpark — Reproduce the Memory Over-Allocation Incident

Using Day 9's executor-sizing calculation, deliberately misconfigure a local job to
reproduce the shape of your real GC-overhead/executor-OOM incident:
```python
# deliberately leave no room for memoryOverhead, matching the incident's shape
spark.conf.set("spark.executor.memory", "8g")       # consumes the FULL per-executor budget
spark.conf.set("spark.executor.memoryOverhead", "0.5g")  # too little headroom
```
Run a job that caches several large DataFrames (Week 1, Day 5) on a memory-constrained
setup and trigger the GC-overhead error. Write root-cause notes: which specific
memory budget was under-allocated, and what the corrected `spark.executor.memory` /
`spark.executor.memoryOverhead` values should be for your actual node's real RAM.

## 2. Kafka — Diagnose Consumer Lag + Build the Debezium CDC Demo

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group your-consumer-group
```
Simulate a lagging consumer (a deliberately slow consumer loop) and use this command's
output (`LAG` column per partition) to identify which partitions are falling behind and
by how much. Separately, complete Day 13's Debezium CDC lab end to end against a real
Postgres table if you haven't already — this is a reusable pattern for any future
database-to-Kafka integration work.

## 3. Flink — Reproduce the Bounded-Source Bug End to End

Using Day 10's exact lab, reproduce the bounded-source misconfiguration (a job that
reaches `FINISHED` when it should run forever), confirm consumer lag climbing as a
result, then apply the fix. **Write root-cause notes mapping this directly onto your
real incident**: which specific configuration value in your production job caused the
same behavior, and what change actually fixed it.

## 4. Redis — Fail a Cluster Node + Benchmark DragonflyDB

Using Day 10's 3-node Cluster setup, kill one node and confirm Cluster's automatic
handling (or lack thereof, if you didn't configure replicas — try both configurations
and compare). Separately, if you haven't completed Day 13's DragonflyDB benchmark yet,
do it now — this is a concrete deliverable for your team's ongoing cost/performance
evaluation.

## 5. Elasticsearch — Implement Hot-Warm-Cold ILM

Complete Day 11's ILM policy lab if you haven't, then explicitly compare its
phase/threshold structure side-by-side against your ClickHouse cluster's TTL-to-volume
configuration from Day 10 — write down the mapping (ILM phase ↔ ClickHouse
TTL/volume) as a reference for anyone on your team evaluating either system's
tiering approach.

## 6. ClickHouse — Fix a Real Fan-Out Bug

Take one actual MDO portal dashboard query currently suspected of the fan-out problem
(Day 9), determine its true join cardinality using `system.query_log` or `EXPLAIN`,
and apply the appropriate fix — aggregate-before-join, or convert to a dictionary
(Day 11) if the "dimension" side is genuinely a lookup. **Write this up formally** —
this is directly reusable as evidence in your BigQuery/ClickHouse migration
decision-making.

## 7. Architecture — Diagram Your Target-State Architecture

Using this week's frameworks (Lambda/Kappa/Kappa+, Day 11; data mesh/lake/lakehouse/
warehouse, Day 12; CQRS, Day 10), diagram your BigQuery→ClickHouse target-state
architecture end to end: ingestion (Flink/Kafka), storage (ClickHouse cluster,
tiered), and serving (Looker Pro or its replacement) — explicitly labeling which
architectural pattern each stage represents.

## Self-Assessment

Update your Week 2 row in [`../PROGRESS_TRACKER.md`](../PROGRESS_TRACKER.md). You
should be solidly at Level 3 across all 7 tracks, with ClickHouse and Flink likely at
Level 3.5+ given how directly this week mapped onto your live production work.

**Checkpoint:** you should now have three concrete, reusable artifacts from this
single day: root-cause notes for two real incidents (PySpark memory, Flink bounded-
source), and a fixed/documented ClickHouse fan-out query — all directly usable at
work, not just for your own learning record.

## Next
Week 3 — Production & Advanced Ops — covers tuning playbooks, monitoring,
observability, security, disaster recovery, and cost/TCO analysis across all 7 tracks.
