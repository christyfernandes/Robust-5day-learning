# Day 4 — Foundations, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min).

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Join strategies (broadcast / shuffle-hash / sort-merge) and data skew + salting |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Broker internals: log segments, ISR, `min.insync.replicas`, leader election |
| 3 | Flink | [03-flink.md](03-flink.md) | Windowing: tumbling, sliding, session; `ReduceFunction` vs. `ProcessWindowFunction` |
| 4 | Redis | [04-redis.md](04-redis.md) | Pub/Sub vs. Streams; consumer groups, Pending Entries List, `XCLAIM` |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Aggregations: metric / bucket / pipeline; scatter-gather and the `terms` accuracy caveat |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Distributed tables & sharding key selection; write skew vs. query fan-out |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Consensus: Paxos (concept) and Raft in detail |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Complete the Raft leader-election paper trace (Architecture lab)

**Proficiency checkpoint for the day:** Level 2, trending toward Level 3 — today's
PySpark/ClickHouse content maps directly onto your live fan-out and sharding-key work.
