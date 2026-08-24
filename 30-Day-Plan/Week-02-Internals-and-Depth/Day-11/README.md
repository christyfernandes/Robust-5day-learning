# Day 11 — Internals & Depth, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min).

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Adaptive Query Execution: dynamic coalescing, dynamic join-strategy switching, skew handling |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Performance tuning: `batch.size`/`linger.ms`, compression, fetch tuning |
| 3 | Flink | [03-flink.md](03-flink.md) | Backpressure: credit-based flow control |
| 4 | Redis | [04-redis.md](04-redis.md) | Caching patterns: cache-aside, read-through, write-through, write-behind |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Index Lifecycle Management: hot-warm-cold-frozen |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Dictionaries — the structural fix for Day 9's JOIN fan-out problem |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Lambda vs. Kappa vs. Kappa+ — applied to your S6 benchmark |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Convert one real fan-out-prone dashboard query to a dictionary-based lookup
      (ClickHouse lab)
- [ ] Classify your current and target pipelines via Lambda/Kappa/Kappa+ (Architecture lab)

**Proficiency checkpoint for the day:** Level 3, with ClickHouse and Architecture
directly informing this week's real production and migration work.
