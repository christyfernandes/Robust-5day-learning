# Day 17 — Production & Advanced Ops, All 7 Tracks

**Total time: ~3 hours** (7 tracks × ~25 min). Monitoring across every system —
Flink today directly supports your ongoing JobManager-debugging practice.

| # | Track | File | Focus |
|---|-------|------|-------|
| 1 | PySpark | [01-pyspark.md](01-pyspark.md) | Monitoring: Spark UI, History Server, straggler detection |
| 2 | Kafka | [02-kafka.md](02-kafka.md) | Monitoring: JMX metrics, consumer-lag alerting, Cruise Control |
| 3 | Flink | [03-flink.md](03-flink.md) | Monitoring: Flink Web UI, checkpoint/backpressure metrics — **directly relevant to your JobManager debugging** |
| 4 | Redis | [04-redis.md](04-redis.md) | Monitoring: `INFO` deep-dive, `LATENCY HISTORY`, Redis Insight |
| 5 | Elasticsearch | [05-elasticsearch.md](05-elasticsearch.md) | Monitoring: cluster health API, hot threads API, Elastic APM basics |
| 6 | ClickHouse | [06-clickhouse.md](06-clickhouse.md) | Monitoring: `system.parts`/`system.merges`/`system.replicas`, Grafana dashboards |
| 7 | Architecture/System Design | [07-architecture-system-design.md](07-architecture-system-design.md) | Observability architecture: metrics/logs/traces, distributed tracing, correlation IDs |

## Checklist
- [ ] Read all 7 lessons
- [ ] Complete each hands-on lab
- [ ] Answer the review questions in each file, out loud, without notes
- [ ] Sketch a real correlation-ID flow through your own multi-system pipeline
      (Architecture lab)

**Proficiency checkpoint for the day:** Level 3.5 — converting this month's reactive
diagnostic skills into proactive, standing monitoring practice.
