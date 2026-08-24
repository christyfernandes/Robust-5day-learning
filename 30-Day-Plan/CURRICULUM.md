# The 30-Day Data Engineering Curriculum
## 7 Parallel Tracks · Basics → Advanced → Architect-Level (Target: Level 4/5 in all tracks)

This is the master blueprint for the whole 30 days. Every day file, week README, and
lab is derived from this document. If a piece of content is ever missing, this is the
source of truth for what it should cover.

> **Why this exists:** the original 5-day version got you moving fast but stayed
> shallow by design (5 topics × ~40 min was never going to reach internals, failure
> modes, or "why did company X pick this" reasoning). This version trades speed for
> depth, adds the two tracks you actually use every day at work (ClickHouse,
> Architecture/System Design), and is sequenced so each week raises the ceiling:
> **Foundations → Internals → Production & Advanced Ops → Architecture Mastery → Capstone.**

---

## 1. The 7 Tracks

| # | Track | One-line role in the stack |
|---|-------|------------------------------|
| 1 | **PySpark** | Distributed batch compute & lakehouse ETL |
| 2 | **Kafka** | Durable, ordered event backbone |
| 3 | **Flink** | True (record-at-a-time) stream processing |
| 4 | **Redis** | In-memory cache / low-latency state |
| 5 | **Elasticsearch** | Full-text search & log/metric analytics |
| 6 | **ClickHouse** | Columnar OLAP / real-time analytics serving layer |
| 7 | **Architecture & System Design** | The glue: patterns, trade-offs, and how the other 6 fit together |

Tracks 1–6 are "tool" tracks. Track 7 is deliberately cross-cutting — it revisits what
you learned in the other six as reusable **patterns** (CAP theorem, consensus,
replication, sharding, CQRS, Lambda/Kappa, resilience patterns) so you stop seeing
Kafka's ISR, Redis's Sentinel, and ClickHouse Keeper as five different things and start
seeing them as **the same handful of distributed-systems ideas, reapplied**.

---

## 2. The Week Arc

| Week | Days | Theme | Target proficiency exit level |
|------|------|-------|-------------------------------|
| 1 | 1–7 | **Foundations** — architecture, core API, install, first hands-on build | Level 2 |
| 2 | 8–14 | **Internals & Depth** — how it actually works under the hood, first production-shaped bugs | Level 3 |
| 3 | 15–21 | **Production & Advanced Ops** — tuning, HA, monitoring, cost, incident writing | Level 3.5–4 |
| 4 | 22–27 | **Architecture Mastery** — design patterns, real company case studies, "when NOT to use it" | Level 4 |
| Capstone | 28–30 | **Integrated build** — all 7 tracks combined into one documented platform | Level 4–4.5, portfolio-ready |

See `PROFICIENCY_RUBRIC.md` for exactly what Level 1–5 means per track, and how to
self-score honestly.

---

## 3. Daily Time Budget

7 topics × ~25 minutes = **~3 hours/day** (vs. the original 5 × 40 min = 2–3 hrs). If
you only have an hour on a given day, do 2–3 tracks properly rather than skimming all 7
— depth over completeness, every day. The plan is designed so tracks can be read out of
order within a day.

---

## 4. Every Day File Follows the Same Template

See `DAY_TEMPLATE.md`. Each topic-day file has: **Learning Objective → Core Concept
(basics → advanced) → Internals ("how it really works") → Architecture & Design
Pattern spotlight → Hands-On Lab → Real-World Product Comparison → Common Production
Pitfalls → Review Questions → Proficiency Checkpoint.** This is what makes the
"compare with existing top products" and "architecture/design pattern" requirements
consistent across all 210 topic-days instead of a one-off aside.

---

## 5. Full 30-Day Matrix

Each cell is the day's focus for that track. Full narrative lessons exist today for
**Day 1 and Day 2** (all 7 tracks) as the depth template — see
`Week-01-Foundations/Day-01/` and `Day-02/`. Every other day below has a complete
**brief** (objective + pattern spotlight + product comparison + lab) in its week's
`README.md`, ready to expand into a full lesson file the same way (ask any time — see
`HOW_TO_CONTINUE.md`).

### Week 1 — Foundations (Level 2)

| Day | PySpark | Kafka | Flink | Redis | Elasticsearch | ClickHouse | Architecture/SysDesign |
|-----|---------|-------|-------|-------|----------------|------------|--------------------------|
| 1 | Spark vs Hadoop MR; RDD/DataFrame/Dataset; SparkSession; word count | Pub/sub vs queue; brokers/topics/partitions; produce/consume | Stream vs batch; JobManager/TaskManager; first DataStream job | Event-loop model; core data structures; TTL; basic CRUD | Lucene & inverted index; index/doc/mapping; first search | OLAP vs OLTP; columnar storage; MergeTree basics | CAP theorem & PACELC; consistency models |
| 2 | DataFrame API, Spark SQL, Catalyst basics | Producer internals: partitioning, acks, idempotence | DataStream core: map/filter/keyBy, parallelism | Sorted sets, HyperLogLog, Bitmaps, Geo | Analyzers, mapping deep-dive, multi-fields | Engine family: Replacing/Summing/AggregatingMergeTree | Replication strategies: leader-follower, multi-leader, leaderless |
| 3 | Spark architecture: driver/executor/stages/shuffle | Consumer groups, partition assignment, rebalancing | Time semantics: event vs processing time, watermarks | Persistence: RDB vs AOF, fork() COW snapshotting | Query DSL: match/term/bool/range, BM25 scoring | Primary key & sparse index vs B-tree | Partitioning/sharding: range, hash, consistent hashing |
| 4 | Joins: broadcast/shuffle-hash/sort-merge, skew & salting | Broker internals: log segments, ISR, leader election | Windowing: tumbling/sliding/session, window functions | Pub/Sub + Redis Streams (mini-Kafka comparison) | Aggregations: metric/bucket/pipeline | Distributed tables & sharding key selection | Consensus: Paxos concept, Raft in detail |
| 5 | Caching/persistence, unified memory model, GC intro | KRaft mode: Raft-based controller quorum | State: ValueState/ListState/MapState, RocksDB backend | Transactions: MULTI/EXEC/WATCH, Lua scripting | Cluster architecture: node roles, shards/replicas | Replication: ReplicatedMergeTree + ClickHouse Keeper | Distributed transactions: 2PC, Saga, Outbox |
| 6 | Structured Streaming: micro-batch, watermarks, checkpoints | Schema Registry: Avro/Protobuf, compatibility modes | Checkpointing: Chandy-Lamport barriers, exactly-once | Eviction policies: LRU/LFU, memory fragmentation | Indexing internals: segments, refresh/flush/merge | Materialized Views: normal vs **Refreshable MV** | Caching strategy at the architecture level |
| 7 | **Lab + review** | **Lab + review** | **Lab + review** | **Lab + review** | **Lab + review** | **Lab + review** | **Lab: ADR — pick a consistency model** |

### Week 2 — Internals & Depth (Level 3)

| Day | PySpark | Kafka | Flink | Redis | Elasticsearch | ClickHouse | Architecture/SysDesign |
|-----|---------|-------|-------|-------|----------------|------------|--------------------------|
| 8 | Catalyst + Tungsten: codegen, columnar/vectorized exec | Kafka Streams/ksqlDB: KStream/KTable duality | Flink SQL & Table API: dynamic tables, changelogs | Replication internals: backlog, PSYNC2 partial resync | Distributed search: query-then-fetch, scatter-gather | Query execution internals: vectorized engine | Architectural styles: monolith vs microservices vs modular monolith |
| 9 | Executor sizing, dynamic allocation, YARN vs K8s scheduling | Exactly-once semantics: idempotent producer + txn coordinator | Connectors: Kafka source/sink two-phase commit | Sentinel: quorum-based automated failover | Relevance tuning: BM25 k1/b, function_score, synonyms | **The JOIN fan-out problem** (your live issue) | Event-driven patterns: notification vs event-carried state vs event sourcing |
| 10 | Shuffle internals: sort-based shuffle, spill to disk | Log compaction, tiered storage to object store | **Bounded vs unbounded sources** (your live issue) | Redis Cluster: hash slots, gossip protocol | Data modeling: nested vs object vs parent-child (join) | Hot/cold tiering: `TTL TO VOLUME/DISK`, storage_policy | CQRS in depth: command/query split, read projections |
| 11 | Adaptive Query Execution (AQE): skew join auto-handling | Performance tuning: broker/producer/consumer configs | Backpressure: credit-based flow control | Caching patterns: aside/read-through/write-through/behind | Index Lifecycle Management (ILM): hot-warm-cold-frozen | Dictionaries: fast lookups as a JOIN alternative | Lambda vs Kappa vs Kappa+ architectures |
| 12 | File formats: Parquet internals, predicate pushdown | Multi-cluster: MirrorMaker 2, active-active/passive | Complex Event Processing (CEP) | Redis as primary store vs cache-only trade-offs | Percolator & reverse-search / alerting patterns | Codecs & compression: LZ4/ZSTD/Delta/Gorilla | Data mesh vs lake vs lakehouse vs warehouse |
| 13 | Lakehouse: Delta/Iceberg/Hudi, ACID log pattern | Kafka Connect: CDC via Debezium | Scaling: parallelism vs slots, reactive/autoscale mode | Modern alternatives: DragonflyDB, Valkey, KeyDB | Vector search / kNN, HNSW basics | ClickHouse + Kafka table engine ingestion | Resilience patterns: circuit breaker, bulkhead, backoff+jitter |
| 14 | **Lab: reproduce & fix OOM/GC** | **Lab: diagnose consumer lag + build CDC demo** | **Lab: reproduce your bounded-source bug** | **Lab: cluster failover + DragonflyDB benchmark** | **Lab: ILM policy vs ClickHouse TTL tiering** | **Lab: reproduce & fix a real fan-out bug** | **Lab: diagram your BQ→ClickHouse target state** |

### Week 3 — Production & Advanced Ops (Level 3.5–4)

| Day | PySpark | Kafka | Flink | Redis | Elasticsearch | ClickHouse | Architecture/SysDesign |
|-----|---------|-------|-------|-------|----------------|------------|--------------------------|
| 15 | Tuning playbook: partition sizing, shuffle minimization | Cluster sizing & capacity planning | Perf tuning: RocksDB config, serialization overhead | Pipelining vs Lua, slow-log, hot/big-key detection | Shard sizing rules, refresh-interval tuning, force merge | Query profiling: `EXPLAIN`, query_log, part-count issues | Scalability patterns: LB algorithms, stateless design |
| 16 | Memory deep-dive round 2: OOM root causes (your bug) | Reliability: unclean leader election, min.insync.replicas | Advanced fault tolerance: unaligned checkpoints | Memory optimization: ziplist/listpack encodings | Query performance: profiling API, expensive-query traps | Cluster tuning: HAProxy routing, per-query quotas | Reliability eng.: SLIs/SLOs/error budgets, cell-based arch |
| 17 | Monitoring: Spark UI, History Server, straggler detection | Monitoring: JMX, lag alerting, Cruise Control | Monitoring: Flink UI, checkpoint/backpressure metrics | Monitoring: `INFO`, latency history, Insight | Monitoring: cluster health, hot threads, APM | Monitoring: system tables, Grafana dashboards | Observability architecture: metrics/logs/traces, tracing |
| 18 | Security & multi-tenancy: queues, quotas, governance | Security: SASL/SSL, ACLs | High availability: JobManager HA & failover | Security: AUTH/ACLs (v6+), TLS | Security: RBAC, field/doc-level security | Security: RBAC, row-level policies, quotas | Security architecture: zero trust, defense in depth |
| 19 | Cost optimization: spot/autoscale, right-sizing | DR & multi-region: geo-replication | Deployment modes: session/app/per-job, K8s Operator | Multi-region: active-active CRDTs | Resiliency: split-brain prevention, snapshot/restore | Backup & DR: `clickhouse-backup`, replica-based DR | Multi-region & DR: active-active vs passive, RPO/RTO |
| 20 | Managed vs self-hosted cost ($/TB-processed) | Alternatives: MSK vs Confluent vs Redpanda vs Pulsar | Alternatives: Kinesis Analytics vs Dataflow (Beam) | Licensing landscape: SSPL, Valkey fork, ElastiCache | Alternatives: OpenSearch fork, Typesense, Algolia | **Cost modeling: self-hosted vs BigQuery TCO** (your POC) | Cost-aware architecture: FinOps, build-vs-buy |
| 21 | **Lab: incident postmortem for your real OOM bug** | **Lab: consumer-lag incident runbook** | **Lab: your real JobManager-instability postmortem** | **Lab: MDO-portal caching strategy doc** | **Lab: slow-query diagnosis + sharding doc** | **Lab: cost/perf comparison report for stakeholders** | **Lab: ADR — self-hosted ClickHouse vs BigQuery/Looker Pro** |

### Week 4 — Architecture Mastery (Level 4)

| Day | PySpark | Kafka | Flink | Redis | Elasticsearch | ClickHouse | Architecture/SysDesign |
|-----|---------|-------|-------|-------|----------------|------------|--------------------------|
| 22 | Patterns: Lambda batch layer, Medallion, MERGE upserts | Patterns: event sourcing, CQRS, outbox, saga | Patterns: Kappa architecture, Stateful Functions | Patterns: Redlock (+critique), rate limiting | Patterns: CQRS read-model, search-as-a-service facade | Patterns: Lambda/Kappa serving layer, OBT vs star schema | Reference architecture: your real target stack end to end |
| 23 | Case studies: Databricks, Netflix, Airbnb | Case studies: LinkedIn origin, Netflix Keystone, Uber | Case studies: Alibaba Blink, Uber, Stripe | Case studies: Twitter timelines, GitHub, StackOverflow | Case studies: GitHub search, Uber logging, Wikipedia | Case studies: Cloudflare, Uber, eBay | Case studies: Netflix, Uber, Cloudflare, LinkedIn data platforms |
| 24 | When NOT to use Spark + alternatives matrix | When NOT to use Kafka + alternatives matrix | When NOT to use Flink + alternatives matrix | When NOT to use Redis + alternatives matrix | ES vs ClickHouse for aggregation-heavy dashboards | When NOT to use ClickHouse + alternatives matrix | Trade-off frameworks: build vs buy, boring technology |
| 25 | Case study: your S6 lakehouse benchmark, revisited | Case study: Sunbird telemetry backbone, redesigned | Case study: redesigning your Sunbird Flink jobs | Case study: MDO portal cache-bypass fix | Case study: could ClickHouse replace this ES workload? | **Case study: the actual MDO portal migration design** | **Full capstone design: Tarento's BQ→ClickHouse target state** |
| 26 | Integration: Spark+Kafka/ClickHouse/Redis connectors | Integration: Kafka+Flink/ClickHouse/Redis | Integration: Flink+ClickHouse/Redis/ES sinks | Integration: Redis+Kafka/ClickHouse hot-tier cache | Integration: ES+Kafka/Flink, ES vs ClickHouse head-to-head | Integration: CH+Kafka/Spark/Redis | Integration day: one component-interaction diagram, all 7 |
| 27 | **Interview-readiness: Staff-level Spark design Qs** | **Interview-readiness: event-streaming design Qs** | **Interview-readiness: streaming-systems design Qs** | **Interview-readiness: caching system design Qs** | **Interview-readiness: search system design Qs** | **Interview-readiness: OLAP platform design Qs** | **Mock Principal Architect review — defend your design** |

### Capstone — Days 28–30 (Level 4–4.5, portfolio-ready)

| Day | Focus |
|-----|-------|
| 28 | **Build**: integrate all 7 into one "Real-Time Analytics Platform" — Kafka (ingest) → Flink (enrich) → ClickHouse (OLAP + Refreshable MVs) → Redis (hot cache) → Elasticsearch (search/log layer) → PySpark (batch backfill), one architecture diagram |
| 29 | **Document**: README, ADRs per major decision, runbooks, cost model, monitoring spec — templates you can reuse at Tarento immediately |
| 30 | **Assess**: self-score against `PROFICIENCY_RUBRIC.md`, mock architecture review, roadmap to true Level 5 |

---

## 6. How This Maps to Your Real Work

This curriculum is written so the "hands-on" isn't generic — several labs are
deliberately your actual open production issues, turned into structured practice:

- **PySpark Day 14/16/21** → your executor/driver memory over-allocation + GC overhead
  incident on the shared single-node environment.
- **Flink Day 10/14/17/21** → your JobManager-reaching-terminal-state / bounded-source
  misconfiguration issue and the resulting Kafka consumer lag.
- **ClickHouse Day 9/14/20/21/25** → your sharding-key decision, the fan-out/
  join-multiplication problem behind the MDO portal dashboards, and the BigQuery vs.
  self-hosted cost model you're building for stakeholders.
- **Architecture Day 11/12/20/21/25** → Lambda/Kappa framing for your own S6 benchmark,
  and the ADR for the BigQuery/Looker Pro → ClickHouse/Looker decision itself.

Treat these days as double duty: you're not just studying, you're producing draft
artifacts (runbooks, ADRs, cost models) you can adapt and hand to your own team.

---

## 7. Proficiency Target

By Day 30, the goal is **Level 4/5 in all seven tracks** — defined precisely in
`PROFICIENCY_RUBRIC.md`. In short: you can design, build, operate, and troubleshoot
production systems with these tools independently, explain the internals well enough to
make defensible trade-off calls, and know when *not* to reach for a given tool. Level 5
(deep specialist / contributor-level in 1–2 tools) is intentionally a "next quarter"
goal, not a 30-day one — see the roadmap in the Capstone README.
