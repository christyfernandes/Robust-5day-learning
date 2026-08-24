# Day 18 — Production & Advanced Ops, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). Security across every system —
ClickHouse today is directly relevant to expanding analytics-team access on your
cluster.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Security & multi-tenancy: resource queues/pools, fair-share scheduling |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Security: SASL/SSL, ACLs — authentication + authorization layers |
| 3 | Flink | [03-flink.md](03-flink.md) | High availability: JobManager HA, standby JMs, failover mechanics |
| 4 | Redis | [04-redis.md](04-redis.md) | Security: AUTH/ACLs (v6+ fine-grained permissions), TLS |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Security: RBAC, field/document-level security |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Security: RBAC, row-level security policies — **relevant for multi-tenant analytics access on your cluster** |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Security architecture: zero trust basics, defense in depth, secrets management |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Map your own platform's real trust boundaries (Architecture lab)
- [ ] Configure and verify a real ClickHouse row policy (ClickHouse lab) — directly
      reusable for your migration's access-expansion plan

**Proficiency checkpoint for the day:** Level 3.5 — a consistent security posture
across every system, unified by the zero-trust/defense-in-depth framing.
