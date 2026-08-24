# Day 24 — Architecture Mastery: When NOT to Use It, All 7 Tracks

**Total time: ~3.5 hours** (7 tracks × ~25-30 min). Elasticsearch today is
directly relevant to your own work — the ES-vs-ClickHouse dashboard question.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Latency floor, small-data overkill — Spark vs. Trino vs. DuckDB/Polars vs. ClickHouse |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Simple task queues, latency-sensitive RPC — Kafka vs. Pulsar vs. Redpanda vs. a cloud-native queue |
| 3 | Flink | [03-flink.md](03-flink.md) | Overhead for simple embedded transforms, batch-only workloads |
| 4 | Redis | [04-redis.md](04-redis.md) | Durability-critical primary storage, datasets far exceeding RAM economics |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | **ES vs. ClickHouse for aggregation-heavy dashboards — directly relevant to your work** |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | High-concurrency point lookups, frequent updates/deletes, small datasets |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Trade-off frameworks: build vs. buy, the "boring technology" principle |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Write the one-sentence design-review pushback for each track — this is
      the actual Level 4 skill this day builds
- [ ] Apply the build-vs-buy/innovation-token framework to one real decision
      at your work (Architecture lab)

**Proficiency checkpoint for the day:** Level 4 — knowing when *not* to reach
for a tool is as important as knowing how to use it.
