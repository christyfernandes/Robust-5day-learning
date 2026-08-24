# Day 15 — Production & Advanced Ops, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). Week 3 begins: tuning playbooks across
every system studied so far.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Tuning playbook: partition sizing, shuffle minimization, broadcast threshold |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Cluster sizing & capacity planning: throughput + retention math |
| 3 | Flink | [03-flink.md](03-flink.md) | Perf tuning: RocksDB state-backend config, serialization overhead (POJO/Avro/Kryo) |
| 4 | Redis | [04-redis.md](04-redis.md) | Pipelining vs. Lua, slow-log, hot/big-key detection |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Shard sizing rules, refresh-interval tuning, force merge |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Query profiling: `EXPLAIN`, `system.query_log`, too-many-parts issues |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Scalability patterns: load-balancing algorithms, stateless service design |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Classify your own platform's components as stateless/stateful (Architecture lab)

**Proficiency checkpoint for the day:** Level 3.5 — Week 3 moves from "understand the
internals" to "operate this confidently in production."
