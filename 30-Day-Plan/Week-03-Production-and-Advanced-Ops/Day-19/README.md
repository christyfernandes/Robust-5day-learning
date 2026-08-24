# Day 19 — Production & Advanced Ops, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). Disaster recovery and multi-region
resilience across every system.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Cost optimization: spot/preemptible instances, autoscaling, right-sizing |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | DR & multi-region: geo-replication patterns, active-passive with MM2 |
| 3 | Flink | [03-flink.md](03-flink.md) | Deployment modes: session vs. application vs. per-job, K8s Operator patterns |
| 4 | Redis | [04-redis.md](04-redis.md) | Multi-region: active-active with CRDTs (Redis Enterprise) |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Resiliency: split-brain prevention, snapshot/restore, cross-cluster replication |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Backup & DR: `clickhouse-backup`, S3/GCS strategies, replica-based DR |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Multi-region & DR: active-active vs. active-passive, RPO/RTO |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Run a real `clickhouse-backup` create/restore cycle (ClickHouse lab)
- [ ] Define measurement-grounded RPO/RTO targets for one real platform component
      (Architecture lab)

**Proficiency checkpoint for the day:** Level 3.5 — DR readiness reasoned about with
precise, measurable vocabulary rather than aspiration.
