# Day 26 — Architecture Mastery: Integration Day, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25-30 min). Verifying every pairwise
system interaction in your Day 25 capstone design.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Spark+Kafka (Structured Streaming), Spark+ClickHouse (JDBC), Spark+Redis (feature store) |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Kafka+Flink (exactly-once), Kafka+ClickHouse (table engine), Kafka+Redis (invalidation events) |
| 3 | Flink | [03-flink.md](03-flink.md) | Flink+ClickHouse sink (**exactly-once caveats**), Flink+Redis (lookups), Flink+ES sink |
| 4 | Redis | [04-redis.md](04-redis.md) | Redis+Kafka (invalidation), Redis as hot-tier cache in front of ClickHouse |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | ES+Kafka/Flink ingestion; finalized ES vs. ClickHouse decision |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | The full integration set — Kafka, Spark, Redis, from ClickHouse's side |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | **One component-interaction diagram** tying all 7 tracks' integrations into a single picture |

## Checklist
- [ ] Read all 7 lessons
- [ ] Verify your Day 25 capstone design against each integration caveat
      identified today (especially the Flink→ClickHouse exactly-once caveat)
- [ ] Produce the single, fully-labeled component-interaction diagram
      (Architecture lab)

**Proficiency checkpoint for the day:** Level 4 — every integration in your
real architecture explicitly verified, not assumed.
