# Day 5 — Foundations, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min).

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Unified memory model (execution vs. storage), `persist()` storage levels, GC pressure |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | KRaft mode: Raft-based controller quorum, replacing ZooKeeper |
| 3 | Flink | [03-flink.md](03-flink.md) | State: `ValueState`/`ListState`/`MapState`; HashMap vs. RocksDB backend; TTL |
| 4 | Redis | [04-redis.md](04-redis.md) | Transactions: `MULTI`/`EXEC`/`WATCH` (optimistic concurrency) vs. Lua scripting |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Cluster architecture: node roles, shard/replica placement, cluster-state consensus |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Replication: `ReplicatedMergeTree` + Keeper — **your exact cluster's architecture** |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Distributed transactions: 2PC, Saga, Outbox |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Complete the Saga design exercise (Architecture lab)

**Proficiency checkpoint for the day:** Level 2, trending toward Level 3 — the
ClickHouse lesson today traces your own live production cluster's replication mechanism.
