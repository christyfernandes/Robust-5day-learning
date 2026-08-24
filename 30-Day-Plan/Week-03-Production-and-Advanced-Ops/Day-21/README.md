# Day 21 — Lab + Week 3 Review

## Time: ~4-5 hours | Proficiency target: Level 3.5-4 confirmed across all 7 tracks

This is the most directly work-relevant day in the entire curriculum so far — every
deliverable below is meant to be handed to your team, not filed away as a learning
exercise. Use the templates as starting structures; adapt freely to your team's own
documentation conventions.

## 1. PySpark — Incident Postmortem

Using Day 16's precise root-cause numbers, write a formal postmortem:
```markdown
# Postmortem: PySpark Executor/Driver Memory Over-Allocation

## Summary
[1-2 sentences: what happened, user/business impact]

## Timeline
[When detected, when mitigated, when resolved]

## Root Cause
[The precise accounting from Day 16: which memory term was missing/under-estimated,
 against the node's actual RAM]

## Fix Applied
[Corrected spark.executor.memory / memoryOverhead / pyspark.memory values]

## Prevention
- [ ] Standard executor-sizing template updated for this node class
- [ ] Monitoring alert added for [specific leading indicator]
- [ ] Runbook updated with this failure signature
```

## 2. Kafka — Consumer-Lag Incident Runbook

```markdown
# Runbook: Consumer Lag Incident

## Detection
- Alert threshold: [from Day 17 — throughput-normalized lag threshold]
- Dashboard: [link/location]

## Triage
1. `kafka-consumer-groups.sh --describe --group <group>` — which partitions, how much lag?
2. Is the consumer process alive? Check for rebalance loops (Week 1, Day 3) in logs.
3. Is this a genuine processing slowdown, or a Day 10/Week 2 bounded-source-style
   "job stopped consuming" situation?

## Remediation
- [Specific steps per likely cause: restart consumer, scale consumer group,
  investigate downstream slowness]

## Postmortem trigger
File a postmortem if lag exceeded [threshold] for longer than [duration].
```

## 3. Flink — JobManager Instability Postmortem

Using Week 2 Day 10's bounded-source root cause (or whatever your actual investigation
found), write the formal postmortem using the same template as #1 above, explicitly
citing: which source configuration caused bounded behavior, how consumer lag
symptoms connected to job state, and the specific fix + prevention (config review
checklist, monitoring per Day 17).

## 4. Redis — MDO Portal Caching-Strategy Decision Doc

```markdown
# Decision: Caching Strategy for MDO Portal

## Current state
[Cache hierarchy from Week 1 Day 6's sketch — layers, suspected bypass point]

## Options considered
- Cache-aside (current?) — staleness window: [from Day 11's lab measurement]
- Write-through — staleness window: [near-zero, at what latency cost?]

## Decision
[Which pattern, for which specific data/dashboard, and why]

## TTLs and invalidation
[Specific TTL values and invalidation triggers per cache layer]
```

## 5. Elasticsearch — Slow Query Diagnosis + Sharding Strategy Doc

Diagnose one real or representative slow query using the `_search` profile API
(Day 16), documenting which phase/cause was responsible. Then write a sharding
strategy doc for a hypothetical log-analytics use case, specifying: shard count
and sizing rationale (Day 15), ILM policy (Week 2 Day 11), and node-role
topology (Week 1 Day 5).

## 6. ClickHouse — Cost/Performance Comparison Report

Formalize Day 20's cost model into a stakeholder-ready report: the three-way
comparison (current BigQuery, corrected BigQuery, self-hosted ClickHouse),
including the fan-out-driven cost inefficiencies identified in Week 2 Day 9, and
a clear recommendation.

## 7. Architecture — ADR: Self-Hosted ClickHouse vs. BigQuery/Looker Pro

Using the ADR template from Week 1, Day 7, and the alternatives-considered format:
```markdown
# ADR: ClickHouse Cluster vs. BigQuery/Looker Pro

## Status
Proposed / Accepted

## Context
[The cost/performance drivers from this week, the fan-out investigation from
 Week 2, the actual POC results]

## Alternatives Considered
1. Status quo (BigQuery/Looker Pro) — [cost, pros/cons]
2. Self-hosted ClickHouse (the POC) — [cost, pros/cons]
3. [Any managed alternative considered, e.g., ClickHouse Cloud]

## Decision
[Recommendation, with the specific evidence from Day 20's cost model]

## Consequences
[Operational burden taken on — Week 3's security/monitoring/DR lessons — and
 what would trigger revisiting this decision]
```

## Self-Assessment

Update your Week 3 row in [`../PROGRESS_TRACKER.md`](../PROGRESS_TRACKER.md). You
should be at Level 3.5-4 on most tracks — the ClickHouse and Architecture documents
from today are meant to be handed to your actual team.

**Checkpoint:** you now have seven real, reusable production artifacts from this
single day — two formal incident postmortems, an incident runbook, a caching
decision doc, a sharding strategy doc, a cost/performance report, and a formal ADR.
This is the tangible output of three weeks of depth-first study.

## Next
Week 4 — Architecture Mastery — synthesizes everything into design patterns, case
studies, "when NOT to use X" decision frameworks, and a capstone built directly on
your own real work.
