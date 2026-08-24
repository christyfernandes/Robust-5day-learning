# Day 16 — Production & Advanced Ops, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). PySpark today directly analyzes your
real production incident with real numbers.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Memory deep-dive round 2: concrete OOM root causes — **your real bug, with real numbers** |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Reliability: unclean leader election, `min.insync.replicas` |
| 3 | Flink | [03-flink.md](03-flink.md) | Advanced fault tolerance: unaligned checkpoints |
| 4 | Redis | [04-redis.md](04-redis.md) | Memory optimization: `ziplist`/`listpack` compact encodings |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Query performance: profiling API, expensive-query traps |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Cluster tuning: HAProxy query routing, per-query resource quotas — **your own cluster's layer** |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Reliability engineering: SLIs/SLOs/error budgets, cell-based architecture |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Produce a precise, numbers-based root-cause writeup of your real PySpark
      incident (PySpark lab) — reusable for Day 21
- [ ] Define a real SLI/SLO/error-budget triple for one platform component
      (Architecture lab)

**Proficiency checkpoint for the day:** Level 3.5, with PySpark and ClickHouse
producing directly reusable production artifacts.
