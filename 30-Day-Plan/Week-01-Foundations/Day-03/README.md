# Day 3 — Foundations, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min).

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Cluster architecture: driver, cluster manager, executors; stages, tasks, and what a shuffle actually is |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Consumer groups, partition assignment strategies, rebalancing (eager vs. cooperative-sticky) |
| 3 | Flink | [03-flink.md](03-flink.md) | Event time vs. processing time vs. ingestion time; watermarks; late data |
| 4 | Redis | [04-redis.md](04-redis.md) | Persistence: RDB snapshotting (fork + copy-on-write) vs. AOF; fsync policy |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Query DSL: query vs. filter context; BM25 scoring internals |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Primary key & sparse index vs. a classic B-tree; `ORDER BY` as a physical decision |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Partitioning: range vs. hash vs. consistent hashing; rebalancing cost |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Complete the Architecture mapping exercise (Kafka / Redis Cluster / ClickHouse
      partitioning, side by side)

**Proficiency checkpoint for the day:** Level 2, trending toward Level 3 on the tracks
that already map to your production experience (ClickHouse, Architecture).
