# Week 3 — Production & Advanced Ops
### Target exit proficiency: Level 3.5–4 on all 7 tracks

This week is about the parts of running these systems that only show up once
something is live: tuning under real load, staying up during failures, knowing what's
happening via monitoring, securing access, and — increasingly relevant to your own
POC — understanding the real cost trade-offs of managed vs. self-hosted. Day 21's lab
is deliberately structured so you produce real incident/decision documents, not just
study notes.

No full lesson files exist yet for Week 3 — every day below is a complete brief. See
`../HOW_TO_CONTINUE.md` to expand any day into a full lesson.

---

### Day 15

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Tuning playbook: partition sizing, shuffle minimization, broadcast threshold | Rules-of-thumb codified from Catalyst's cost model | — | Tune `spark.sql.shuffle.partitions` and broadcast threshold for a real join, measure before/after |
| **Kafka** | Cluster sizing & capacity planning | Capacity planning from throughput + retention math | — | Given a target events/sec + retention window, calculate required partitions and disk |
| **Flink** | Perf tuning: RocksDB state-backend config, serialization overhead (POJO vs. Avro vs. Kryo) | Serialization format trade-offs | — | Swap a job's state backend/serializer, measure checkpoint size and duration change |
| **Redis** | Pipelining vs. Lua, slow-log, hot/big-key detection | Round-trip reduction techniques | — | Use `redis-cli --bigkeys` and `SLOWLOG GET` on a populated instance |
| **Elasticsearch** | Shard sizing rules (avoid over-sharding), refresh-interval tuning, force merge | Right-sizing distributed storage units | — | Compare indexing throughput at `refresh_interval=1s` vs. `30s` on a bulk load |
| **ClickHouse** | Query profiling: `EXPLAIN`, `system.query_log`, too-many-parts issues | Query-plan-driven tuning | — | Profile a slow query with `EXPLAIN PIPELINE` + `system.query_log`, identify the bottleneck |
| **Architecture** | Scalability patterns: load-balancing algorithms, stateless service design | Horizontal scaling prerequisites | — | Identify which of your platform's components are stateless vs. stateful, and what that implies for scaling each |

---

### Day 16

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Memory deep-dive round 2: concrete OOM root causes (**your real bug**) | Unified memory model exhaustion patterns | — | Given your real executor/driver config numbers, calculate where the over-allocation against node RAM occurred |
| **Kafka** | Reliability: unclean leader election, `min.insync.replicas` | Consistency-vs-availability knob, made concrete | — | Simulate an unclean leader election scenario (all ISR members down) and observe the config that would have prevented data loss |
| **Flink** | Advanced fault tolerance: unaligned checkpoints | Checkpoint barrier handling under backpressure | Relevant if your JobManager issue ever coincided with backpressure | Enable unaligned checkpoints on a backpressured job, compare checkpoint duration |
| **Redis** | Memory optimization: `ziplist`/`listpack` compact encodings | Small-collection memory optimization | — | Compare `MEMORY USAGE` of a hash under/over the `hash-max-listpack-entries` threshold |
| **Elasticsearch** | Query performance: profiling API, expensive-query traps (leading wildcards, scripts) | Query cost analysis | — | Profile a wildcard query with the `_search` profile API, identify the cost |
| **ClickHouse** | Cluster tuning: HAProxy query routing, per-query resource quotas | Load-balanced query routing + resource governance | Directly your own cluster's HAProxy layer | Configure a per-user `max_memory_usage` quota and confirm it's enforced |
| **Architecture** | Reliability engineering: SLIs/SLOs/error budgets, cell-based architecture | Blast-radius reduction | — | Define one SLI/SLO pair for a real component of your platform |

---

### Day 17

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Monitoring: Spark UI, History Server, straggler detection | Task-level observability | — | Find a straggler task in a job's Spark UI stage view, hypothesize why |
| **Kafka** | Monitoring: JMX metrics, consumer-lag alerting, Cruise Control | Lag as the primary health signal | — | Set up a lag alert threshold and simulate a lag spike |
| **Flink** | Monitoring: Flink Web UI, checkpoint/backpressure metrics | **Directly relevant to your JobManager-instability debugging** | — | Identify checkpoint duration and backpressure ratio for a running job via the metrics reporter |
| **Redis** | Monitoring: `INFO` command deep-dive, `LATENCY HISTORY`, Redis Insight | Built-in self-reporting | — | Parse `INFO memory` and `INFO stats` output, identify 3 actionable fields |
| **Elasticsearch** | Monitoring: cluster health API, hot threads API, Elastic APM basics | Cluster-level health signals | — | Call `_cluster/health` and `_nodes/hot_threads` on a loaded cluster |
| **ClickHouse** | Monitoring: `system.parts`/`system.merges`/`system.replicas`, Grafana dashboards | System-table-driven observability | — | Query `system.parts` to find a table with too many active parts, a common perf symptom |
| **Architecture** | Observability architecture: metrics/logs/traces, distributed tracing, correlation IDs | The three pillars | Relevant across your multi-system pipeline (Kafka→Flink→Redis/ES/ClickHouse) | Sketch how a single correlation ID would flow through your own pipeline's 4+ systems |

---

### Day 18

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Security & multi-tenancy: resource queues/pools, quotas, data governance | Fair-share scheduling | YARN fair scheduler vs. K8s namespace quotas | Configure a fair-scheduler pool for 2 competing job classes |
| **Kafka** | Security: SASL/SSL, ACLs | Authentication + authorization layers | — | Configure a topic-level ACL restricting one principal to read-only |
| **Flink** | High availability: JobManager HA, standby JMs, failover mechanics | Standby-based failover | — | Configure JobManager HA (K8s HA services or ZooKeeper HA) and force a failover |
| **Redis** | Security: AUTH/ACLs (v6+ fine-grained permissions), TLS | Command/key-pattern-scoped permissions | — | Create an ACL user restricted to a key prefix and a command subset |
| **Elasticsearch** | Security: RBAC, field/document-level security | Fine-grained access control | — | Restrict a role to see only documents matching a filter, and hide one field |
| **ClickHouse** | Security: RBAC, row-level security policies, quotas | Row-level access control | Relevant for multi-tenant analytics team access on your cluster | Define a row policy restricting a role to one tenant's data |
| **Architecture** | Security architecture: zero trust basics, defense in depth, secrets management | Layered trust boundaries | — | Map your platform's current trust boundaries (who can reach what, directly) |

---

### Day 19

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Cost optimization: spot/preemptible instances, autoscaling, right-sizing | Elastic capacity for bursty batch load | — | Model cost difference between fixed cluster and autoscaled cluster for your actual job profile |
| **Kafka** | DR & multi-region: geo-replication patterns | Cross-region durability | — | Sketch an active-passive DR topology using MirrorMaker 2 |
| **Flink** | Deployment modes: session vs. application vs. per-job, Kubernetes Operator patterns | Deployment isolation trade-offs | — | Compare resource isolation of session mode vs. per-job mode for your job mix |
| **Redis** | Multi-region: active-active with CRDTs (Redis Enterprise) | Conflict-free replicated data types | Ties back to Day 2 (Architecture)'s multi-leader conflict-resolution discussion | Read through a CRDT counter example and explain why it merges safely across regions |
| **Elasticsearch** | Resiliency: split-brain prevention, snapshot/restore, cross-cluster replication | Quorum-based master election | — | Configure and run a snapshot to a repository, then restore it |
| **ClickHouse** | Backup & DR: `clickhouse-backup`, S3/GCS-based strategies, replica-based DR | Replica-based + snapshot-based DR combined | — | Run a `clickhouse-backup create` + `restore` cycle locally |
| **Architecture** | Multi-region & DR: active-active vs. active-passive, RPO/RTO | Recovery objective framing | — | Define RPO/RTO targets for one real component of your platform |

---

### Day 20

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Managed vs. self-hosted cost: $/TB-processed comparison | TCO modeling | Databricks/EMR/Dataproc vs. self-managed cluster | Build a simple $/TB-processed model for your own batch workload |
| **Kafka** | Alternatives: Confluent Cloud vs. Amazon MSK vs. Redpanda vs. Apache Pulsar | Managed vs. self-hosted vs. architecturally-different rewrites | — | Fill in `../PRODUCT_COMPARISON_MATRIX.md`'s Kafka row with your own workload's weighting |
| **Flink** | Alternatives: AWS Kinesis Data Analytics vs. Google Cloud Dataflow (Apache Beam) | Managed streaming, and Beam's shared dataflow-model lineage with Flink | — | Read Dataflow's model docs and note which Day 1 Flink concepts map directly |
| **Redis** | Licensing landscape: 2024 SSPL/dual-license shift, the Valkey fork, ElastiCache/Memorystore | Open-source license risk as an architectural input | — | Note which license each of Redis, Valkey, and DragonflyDB ship under today, and why it matters for your org |
| **Elasticsearch** | Alternatives: OpenSearch (AWS-led fork), Typesense/Meilisearch, Algolia | Fork dynamics after a license change (parallels the Redis/Valkey story) | — | Compare OpenSearch's and Elasticsearch's current licenses |
| **ClickHouse** | **Cost modeling: self-hosted ClickHouse vs. BigQuery TCO — your live POC** | Compute+storage-owned vs. pay-per-byte-scanned | — | Build the actual cost comparison framework: hardware/ops cost vs. projected BigQuery scan cost for your workload |
| **Architecture** | Cost-aware architecture: FinOps mindset, build-vs-buy | Total-cost framing as a first-class design input | A running theme all month, given your POC | Write down the 3 biggest cost levers in your target architecture, ranked |

---

### Day 21 — Lab + Week 3 Review (all 7 tracks)

Produce real, reusable artifacts:
1. **PySpark**: write the incident postmortem for your real executor OOM/GC-overhead
   issue (root cause, fix, prevention).
2. **Kafka**: write a consumer-lag incident runbook (detection → triage → remediation).
3. **Flink**: write the postmortem for your real JobManager-instability issue.
4. **Redis**: write a caching-strategy decision doc for the MDO portal (cache-aside vs.
   write-through, TTLs, invalidation).
5. **Elasticsearch**: diagnose a slow query using the profiling API and write a
   sharding-strategy doc for a hypothetical log-analytics use case.
6. **ClickHouse**: build the cost/performance comparison report for stakeholders
   (self-hosted vs. BigQuery).
7. **Architecture**: write a one-page ADR — "self-hosted ClickHouse cluster vs.
   BigQuery/Looker Pro" — using the alternatives-considered format.

**Checkpoint:** update `../PROGRESS_TRACKER.md`. You should be at Level 3.5–4 on most
tracks; the ClickHouse/Architecture docs from today are meant to be handed to your
actual team, not filed away.
