# Day 1 — Foundations, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). Read in any order — Architecture is
written to reference the other 6, so it can work well either first (as a framing lens)
or last (as a synthesis).

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Why Spark exists; RDD/DataFrame/Dataset; driver/executor/stage/task |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Log not a queue; partitions, keys, ordering; producer/consumer/broker |
| 3 | Flink | [03-flink.md](03-flink.md) | True streaming vs. micro-batch; JobManager/TaskManager/task slots |
| 4 | Redis | [04-redis.md](04-redis.md) | Single-threaded reactor model; core data structures; TTL/atomicity |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Inverted index; index/document/mapping; text vs. keyword |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Columnar storage + vectorized execution; MergeTree basics |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | CAP theorem, PACELC, consistency models — the lens for everything else |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab (Docker services: Kafka, Elasticsearch, ClickHouse; `pip install pyspark apache-flink redis kafka-python`)
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Complete the Architecture lab: one CAP/PACELC sentence per other track

**Proficiency checkpoint for the day:** Level 2 across all 7 — see
`../../PROFICIENCY_RUBRIC.md` for exactly what that means.
