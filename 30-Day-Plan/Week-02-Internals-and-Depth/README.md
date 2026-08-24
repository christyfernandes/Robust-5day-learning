# Week 2 — Internals & Depth
### Target exit proficiency: Level 3 on all 7 tracks

This week is where "I can use the API" turns into "I know what the API is doing
underneath." Three of these days are deliberately built around your own real
production issues (PySpark memory/GC, Flink bounded-source, ClickHouse JOIN fan-out) —
treat those labs as double duty: study *and* incident investigation.

No full lesson files exist yet for Week 2 — every day below is a complete brief
(objective + pattern + product comparison + lab). See `../HOW_TO_CONTINUE.md` to expand
any day into a full lesson in the Day 1/2 style.

---

### Day 8

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Catalyst + Tungsten: whole-stage codegen, columnar/vectorized execution | JIT-compiled, batch-of-rows processing | Direct cross-link to ClickHouse's vectorized engine (Day 1) — same idea, different system | Compare `.explain(mode="codegen")` output for a simple filter+aggregate job |
| **Kafka** | Kafka Streams / ksqlDB: KStream/KTable duality | Stream-table duality (a stream is a table's changelog, and vice versa) | Embedded (Kafka Streams) vs. managed cluster (ksqlDB/Flink) | Build a running word-count as a KTable using Kafka Streams' DSL |
| **Flink** | Flink SQL & Table API: dynamic tables, changelog streams, temporal joins | Dynamic tables over unbounded streams | vs. Kafka Streams' KTable — Flink's Table API is the SQL-first equivalent | Write a temporal join (order stream + point-in-time exchange-rate table) in Flink SQL |
| **Redis** | Replication internals: replication backlog, PSYNC2 partial resync | Replication log + partial-resync optimization | vs. Kafka's replica fetch protocol — same "catch up from a log" idea | Disconnect a replica briefly, reconnect, confirm PSYNC2 partial (not full) resync in logs |
| **Elasticsearch** | Distributed search internals: query-then-fetch, scatter-gather | Scatter-gather distributed query execution | vs. ClickHouse's distributed table query routing (same shape, different engine) | Run a query against a multi-shard index, inspect the `_search` profile API's per-shard timing |
| **ClickHouse** | Query execution internals: the vectorized engine, one level deeper | SIMD/batch-of-columns processing | vs. Spark's Tungsten codegen — two different routes to the same "avoid row-at-a-time" goal | Use `EXPLAIN PIPELINE` to see the vectorized execution stages of a query |
| **Architecture** | Architectural styles: monolith vs. microservices vs. modular monolith | Bounded contexts (DDD) | — | Sketch your own data platform's service boundaries as they exist today |

---

### Day 9

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Executor sizing, dynamic allocation, YARN vs. K8s scheduling | Resource pooling / bin-packing | Kubernetes scheduler vs. YARN capacity scheduler | Calculate correct executor-memory + overhead for a given node's RAM (directly relevant to your shared single-node setup) |
| **Kafka** | Exactly-once semantics (EOS): idempotent producer + transactional API + `read_committed` | Two-phase-commit-style transactional writes | vs. database transactions — Kafka's transaction coordinator plays an analogous role | Wrap a produce-to-two-topics operation in a Kafka transaction, verify atomicity |
| **Flink** | Connectors: Kafka source/sink with two-phase commit sink | Two-phase commit for exactly-once sinks | vs. Kafka's own transactional producer (Day 9, Kafka column) — same underlying idea, applied at the sink | Configure a Flink Kafka sink for exactly-once delivery, verify no duplicates after a forced restart |
| **Redis** | Sentinel: quorum-based automated failover | Quorum-based leader election (a real-world Raft-like use case) | vs. Kafka KRaft / ClickHouse Keeper's Raft — same election idea, simpler protocol | Set up 3 Sentinels + 1 primary + 1 replica, kill the primary, watch Sentinel promote the replica |
| **Elasticsearch** | Relevance tuning: BM25 `k1`/`b` parameters, `function_score`, synonyms | Tunable probabilistic ranking | vs. Algolia's more opinionated, less-tunable default ranking | Adjust `k1`/`b` on a test index and observe how score ordering shifts |
| **ClickHouse** | **The JOIN fan-out problem** — your live MDO-portal issue | Row multiplication before aggregation | Why this bites columnar/denormalized-first engines specifically — contrast with a normalized OLTP join | Reproduce a fan-out bug with a fact + dimension table, observe an inflated `SUM()`, fix the query order |
| **Architecture** | Event-driven patterns: event notification vs. event-carried state transfer vs. event sourcing | Choreography vs. orchestration | — | Classify your own Sunbird telemetry pipeline's event style against these three patterns |

---

### Day 10

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Shuffle internals: sort-based shuffle, external spill to disk | External merge sort | Directly relevant to your production disk-space-at-87% concern | Force a large shuffle with a low `spark.sql.shuffle.partitions`, watch spill metrics in Spark UI |
| **Kafka** | Log compaction; tiered storage to object storage | Compacted log = "latest value per key," retained forever | Direct parallel to your ClickHouse hot/cold TTL-to-GCS setup | Create a compacted topic, write multiple values for the same key, confirm only the latest survives after compaction |
| **Flink** | **Bounded vs. unbounded sources — your live JobManager-instability issue** | Source boundedness detection | How this differs from Spark's batch-vs-streaming API split | Deliberately misconfigure a source as bounded on a job meant to run forever; watch it reach FINISHED; fix it |
| **Redis** | Redis Cluster: hash slots (16384), gossip protocol | Consistent-hashing-adjacent (fixed slot count instead of a hash ring) | vs. Kafka partitions / ClickHouse sharding — same "distribute the keyspace" problem, different mechanism | Stand up a 3-node Cluster, insert keys, observe slot distribution via `CLUSTER KEYSLOT` |
| **Elasticsearch** | Data modeling: nested vs. object vs. parent-child (`join` field) | Denormalization trade-offs for search | — | Model the same one-to-many relationship 3 ways, compare query complexity and index size |
| **ClickHouse** | Hot/cold tiering: `TTL ... TO VOLUME/DISK`, `storage_policy` (your exact setup) | Tiered storage by access recency | — | Configure a 2-tier storage policy (hot NVMe / cold GCS-backed) and a TTL moving old parts to cold |
| **Architecture** | CQRS in depth: command/query separation, read-model projections | Read/write model separation | Direct link to Elasticsearch as a CQRS read-model, fed by Kafka events (ties 3 tracks together) | Sketch a CQRS design for a feature where reads and writes have very different scaling needs |

---

### Day 11

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Adaptive Query Execution (AQE): dynamic coalescing, dynamic join-strategy switching | Self-tuning/adaptive execution | BigQuery's automatic slot allocation, Snowflake's auto-clustering — self-tuning warehouses vs. self-managed Spark | Run the same skewed join with AQE on vs. off, compare plans and runtime |
| **Kafka** | Performance tuning: broker/producer/consumer configs | Throughput vs. latency knobs | — | Run `kafka-producer-perf-test`, vary `batch.size`/`linger.ms`, chart throughput |
| **Flink** | Backpressure: credit-based flow control | Flow control to prevent unbounded buffering | — | Introduce a slow sink, observe backpressure indicators in the Flink Web UI |
| **Redis** | Caching patterns: cache-aside, read-through, write-through, write-behind | Cache consistency strategies | Directly relevant to your MDO-portal cache-bypass investigation | Implement cache-aside and write-through for the same data, compare staleness windows |
| **Elasticsearch** | Index Lifecycle Management (ILM): hot-warm-cold-frozen | Tiered storage by access recency | Direct cross-link to ClickHouse's TTL tiering (Day 10) — same idea, different engine | Define an ILM policy that rolls over and moves an index through hot→warm→cold |
| **ClickHouse** | Dictionaries: fast lookups as a JOIN alternative | External dictionary lookup instead of a JOIN | Solves Day 9's fan-out problem directly | Replace a small dimension-table JOIN with a `dictGet()` call, compare query plan and correctness |
| **Architecture** | Lambda vs. Kappa vs. Kappa+ architectures | Batch+speed layer vs. stream-only | Direct link to your own S6 benchmark work | Classify your own current pipeline (BigQuery-based) and target pipeline (ClickHouse-based) by this framework |

---

### Day 12

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | File formats: Parquet internals, row groups, predicate/column pushdown | Columnar file format with embedded statistics | Parquet+Spark vs. ClickHouse's native MergeTree columnar format | Inspect a Parquet file's row-group metadata (min/max stats) with `parquet-tools`/`pyarrow` |
| **Kafka** | Multi-cluster: MirrorMaker 2, active-active vs. active-passive replication | Geo-replication for DR | — | Sketch a MirrorMaker 2 topology for a 2-region setup |
| **Flink** | Complex Event Processing (CEP) | Pattern-matching over event sequences | — | Write a CEP pattern detecting 3 failed logins within 1 minute |
| **Redis** | Redis as primary store vs. cache-only trade-offs | Durability trade-offs of an in-memory system-of-record | Twitter's historical use of Redis for parts of the timeline as near-primary storage | List what you'd need to add (persistence config, backup strategy) to trust Redis as a primary store for one real use case |
| **Elasticsearch** | Percolator & reverse-search / alerting patterns | "Store the query, match incoming documents against it" (inverted from normal search) | — | Register a percolator query, index a document, confirm it matches |
| **ClickHouse** | Codecs & compression: `LZ4`, `ZSTD`, `Delta`, `DoubleDelta`, `Gorilla` | Column-aware compression, chosen per data pattern | Direct relevance to your cost-reduction mission — compression ratio = storage cost | Apply `Delta` codec to a monotonic timestamp column, compare compressed size vs. default |
| **Architecture** | Data mesh vs. data lake vs. lakehouse vs. data warehouse | Architectural philosophy, not just technology | Directly relevant: you're navigating a warehouse (BigQuery) → lakehouse-ish (ClickHouse) shift right now | Classify your team's current setup and your target setup using this framework |

---

### Day 13

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Lakehouse: Delta Lake / Iceberg / Hudi — ACID on a data lake, time travel, schema evolution | Transactional log pattern (same family as Kafka's log!) | Databricks Lakehouse vs. Snowflake vs. BigQuery vs. your own S6 benchmark (which used Iceberg) | Create an Iceberg/Delta table, perform a `MERGE`, then time-travel query an earlier version |
| **Kafka** | Kafka Connect: CDC via Debezium | Change-data-capture as a connector pattern | — | Stand up Debezium against a sample Postgres table, watch row changes flow into a Kafka topic |
| **Flink** | Scaling: parallelism vs. slots, reactive mode / Kubernetes Operator autoscaling | Elastic scaling of a stateful stream job | — | Rescale a running job from a savepoint at a different parallelism |
| **Redis** | Modern alternatives: DragonflyDB, Valkey, KeyDB | Multi-threaded, API-compatible reimplementations | **Directly relevant** — DragonflyDB is already on your radar for the cost/perf work | Benchmark the same workload against Redis and DragonflyDB with `redis-benchmark` |
| **Elasticsearch** | Vector search / kNN, HNSW basics | Approximate nearest-neighbor search | Modern semantic-search use cases (embeddings) vs. classic keyword search | Index a few documents with a `dense_vector` field, run a `knn` query |
| **ClickHouse** | ClickHouse + Kafka table engine: direct ingestion | Native streaming ingestion (log to OLAP table) | — | Create a `Kafka` engine table + Materialized View to land events directly into a MergeTree table |
| **Architecture** | Resilience patterns: circuit breaker, bulkhead, retry with backoff+jitter | Fault isolation and graceful degradation | — | Sketch a circuit breaker for a call from your pipeline to an external/flaky dependency |

---

### Day 14 — Lab + Week 2 Review (all 7 tracks)

This is the week's most directly work-relevant lab day:
1. **PySpark**: reproduce the executor/driver memory-over-allocation + GC-overhead
   error on a constrained local setup; write root-cause notes.
2. **Kafka**: diagnose a simulated consumer-lag scenario using `kafka-consumer-groups
   --describe`; build the Debezium CDC demo end to end.
3. **Flink**: reproduce the bounded-source misconfiguration end to end; fix it; write
   root-cause notes (this maps directly onto your real incident).
4. **Redis**: fail a node in your 3-node Cluster; separately, benchmark DragonflyDB vs.
   Redis on the same workload.
5. **Elasticsearch**: implement an ILM hot-warm-cold policy; compare its shape to
   ClickHouse's TTL tiering from Day 10.
6. **ClickHouse**: reproduce and fix a real fan-out bug using a dictionary or
   pre-aggregation, and write it up — this is directly reusable at work.
7. **Architecture**: diagram your BigQuery→ClickHouse target-state architecture using
   the Lambda/Kappa and data-mesh/lakehouse framings from this week.

**Checkpoint:** update `../PROGRESS_TRACKER.md` — you should be Level 3 on most tracks,
likely already Level 3.5+ on ClickHouse and Architecture given how much of this week
maps to your live work.
