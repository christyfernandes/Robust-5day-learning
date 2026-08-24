# Day 9 — Internals & Depth, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). ClickHouse today covers your live
production fan-out issue directly.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Executor sizing, dynamic allocation, YARN vs. K8s scheduling |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Exactly-once semantics: idempotent producer + transactional API + `read_committed` |
| 3 | Flink | [03-flink.md](03-flink.md) | Exactly-once sinks: two-phase commit tied to checkpoints |
| 4 | Redis | [04-redis.md](04-redis.md) | Sentinel: quorum-based automated failover |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Relevance tuning: BM25 `k1`/`b`, `function_score`, business-signal blending |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | **The JOIN fan-out problem — your live MDO portal issue** |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Event-driven patterns: notification vs. state-transfer vs. sourcing; choreography vs. orchestration |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Complete the ClickHouse fan-out reproduction — then check one real MDO portal
      query for the same risk

**Proficiency checkpoint for the day:** Level 3, with ClickHouse trending to Level 3.5 —
today's fan-out lesson is a direct rehearsal for your real investigation.
