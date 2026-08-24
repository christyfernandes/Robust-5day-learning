# Day 2 — One Level Deeper, All 7 Tracks

**Total time: ~3 hours.** Today pushes each track's core API/engine one notch past
"basic CRUD" — this is where yesterday's architecture pictures start turning into
mechanisms you can reason about.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Catalyst's 4-phase optimization pipeline; DataFrame API = SQL under the hood |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | `acks`, idempotent producer, batching/`linger.ms`, compression |
| 3 | Flink | [03-flink.md](03-flink.md) | Core transformations, operator chaining, parallelism, `key_by()` |
| 4 | Redis | [04-redis.md](04-redis.md) | Sorted sets (skip lists), HyperLogLog, bitmaps, geospatial |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Analyzers as a 3-stage pipeline; multi-field mappings |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | MergeTree variants: Replacing/Summing/Aggregating/Collapsing |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Leader-follower vs. multi-leader vs. leaderless replication |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Complete the Architecture lab: classify Kafka/Redis/ClickHouse/Elasticsearch by
      replication strategy, in your own words

**Proficiency checkpoint for the day:** solidly Level 2, several tracks (especially
ClickHouse, given your live cluster) likely edging into Level 3 already.
