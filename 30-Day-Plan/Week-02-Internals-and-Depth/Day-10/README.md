# Day 10 — Internals & Depth, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). Flink and ClickHouse today map directly
onto your live production concerns.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Shuffle internals: sort-based shuffle, external spill to disk — **your disk-space concern** |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Log compaction; tiered storage to object storage |
| 3 | Flink | [03-flink.md](03-flink.md) | **Bounded vs. unbounded sources — your live JobManager-instability issue** |
| 4 | Redis | [04-redis.md](04-redis.md) | Redis Cluster: hash slots (16384), gossip protocol |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Data modeling: nested vs. object vs. parent-child |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Hot/cold tiering: `TTL ... TO VOLUME/DISK` — **your exact production setup** |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | CQRS in depth: read/write model separation |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Trace your production ClickHouse cluster's storage policy end to end
      (ClickHouse lab)

**Proficiency checkpoint for the day:** Level 3, with Flink and ClickHouse trending to
Level 3.5+ — both map directly onto live production systems you operate.
