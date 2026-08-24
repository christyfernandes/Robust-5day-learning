# Day 12 — Internals & Depth, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min).

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | File formats: Parquet internals, row groups, predicate/column pushdown |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Multi-cluster: MirrorMaker 2, active-active vs. active-passive replication |
| 3 | Flink | [03-flink.md](03-flink.md) | Complex Event Processing (CEP): pattern matching over event sequences |
| 4 | Redis | [04-redis.md](04-redis.md) | Redis as primary store vs. cache-only trade-offs |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Percolator & reverse-search / alerting patterns |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Codecs & compression: `LZ4`, `ZSTD`, `Delta`, `DoubleDelta`, `Gorilla` |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Data mesh vs. data lake vs. lakehouse vs. data warehouse |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Measure real compression improvement from `Delta`/`Gorilla` codecs on your own
      schema's monotonic/time-series columns (ClickHouse lab)
- [ ] Classify your current/target setup on both the technology and organizational
      axes (Architecture lab)

**Proficiency checkpoint for the day:** Level 3, with ClickHouse codec analysis
directly reusable in your cost-reduction work.
