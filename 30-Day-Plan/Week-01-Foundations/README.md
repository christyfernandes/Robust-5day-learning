# Week 1 — Foundations
### Target exit proficiency: Level 2 on all 7 tracks

Goal for this week: solid architecture mental model + first working code for each of
the 7 tracks. This is the "get the basics right, but don't stop there" week — every day
still includes a pattern spotlight and product comparison, because even foundational
concepts are more useful once you can name the underlying pattern and see who else
uses it.

## Days with full lesson files
- **[Day 1](Day-01/)** — first-principles architecture for all 7 tracks
- **[Day 2](Day-02/)** — one level deeper into each track's core API/engine

## Days 3–7 — Full Briefs
(Complete lesson files not yet written — each brief below has everything needed to
either self-author or ask Claude to expand it; see `../HOW_TO_CONTINUE.md`.)

---

### Day 3

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Spark architecture: driver, cluster manager, executors, tasks/stages/shuffle | Master-worker | Spark-on-YARN vs Spark-on-K8s vs Databricks Photon | `spark-submit --master local[4]`, open Spark UI, identify stage/shuffle boundaries |
| **Kafka** | Consumer groups, partition assignment (range/round-robin/sticky/cooperative-sticky), rebalancing | Partitioned work distribution | vs. RabbitMQ's competing-consumers model (different delivery guarantees) | Start 2 consumers in one group, add a 3rd, watch the rebalance in logs |
| **Flink** | Event time vs processing time vs ingestion time; watermarks; late data | Watermark propagation | vs. Spark Structured Streaming's simpler trigger-based model | Feed out-of-order events into a windowed job, tune allowed lateness |
| **Redis** | RDB snapshot vs AOF, fork()-based copy-on-write, fsync policy | Log-structured durability vs point-in-time snapshot | vs. Postgres WAL durability guarantees | Configure RDB+AOF together, `kill -9` the process, compare what's recovered |
| **Elasticsearch** | Query DSL: match/term/bool/range; query vs filter context; BM25 scoring | Probabilistic relevance ranking | BM25 (ES/Lucene) vs Algolia's typo-tolerant ranking | Index sample docs, write a `bool` query mixing must/should/filter, inspect scores |
| **ClickHouse** | Primary key & sparse index vs classic B-tree | Sparse index + granule scanning | vs. Postgres B-tree philosophy, vs. BigQuery's partition/column pruning (no traditional index at all) | Create a table with a poor `ORDER BY` key vs a good one, compare query latency |
| **Architecture** | Partitioning/sharding: range vs hash vs consistent hashing, rebalancing cost | Consistent hashing | Ties Kafka partitions + Redis Cluster slots + ClickHouse sharding into one idea | Map how each of the three chose its partitioning approach, and why |

---

### Day 4

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Joins: broadcast / shuffle-hash / sort-merge; skew & salting | Broadcast pattern vs partitioned shuffle | BigQuery's join strategies; direct parallel to your ClickHouse fan-out issue | Join a small dim table + large fact table, force each join strategy via hints, compare plans |
| **Kafka** | Broker internals: log segments, indexes, ISR, leader election | Leader-follower replication + quorum ack | vs. Postgres synchronous replication | Kill the partition leader broker in a 3-broker cluster, watch ISR shrink and re-election |
| **Flink** | Windowing: tumbling/sliding/session; ReduceFunction vs ProcessWindowFunction | Windowed aggregation over unbounded streams | vs. Kafka Streams' simpler windowed-KTable model | Implement session windows over clickstream-like events with a gap timeout |
| **Redis** | Pub/Sub vs Redis Streams | Fire-and-forget vs durable consumer-group log (mini-Kafka) | Head-to-head: when Streams is "enough" instead of standing up Kafka | Build a Streams job queue (XADD/XREADGROUP/XACK); simulate a consumer crash + pending-entries recovery |
| **Elasticsearch** | Aggregations: metric / bucket / pipeline | Distributed rollup computation | Directly what your BigQuery/Looker dashboards do — ES aggregation model vs ClickHouse `GROUP BY` | Build a `terms` + `date_histogram` aggregation mimicking a dashboard panel |
| **ClickHouse** | Distributed tables & sharding key selection | Scatter-gather over shards | Same underlying problem as Kafka partition-key choice: even distribution + query locality | Design 2 candidate sharding keys for a sample events table, reason about skew |
| **Architecture** | Consensus: Paxos (concept), Raft in detail | The algorithm under Kafka KRaft and ClickHouse Keeper | — | Trace a Raft leader-election timeout scenario on paper |

---

### Day 5

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Caching/persistence, unified memory model (execution vs storage), GC intro | Memory pool allocation | Tungsten off-heap vs Flink's managed memory | Cache a DataFrame at different storage levels, inspect Spark UI's storage tab |
| **Kafka** | KRaft mode: Raft-based controller quorum (ZooKeeper removal) | Consensus-based metadata management | Kafka's own architecture evolution: ZK-era vs KRaft-era operations | Stand up a single-node KRaft cluster, inspect the metadata log |
| **Flink** | State: ValueState/ListState/MapState; HashMap vs RocksDB backend; state TTL | Keyed state colocated with keyed stream partitioning | RocksDB embedded state vs Redis-as-external-state | Implement a stateful dedup operator using `ValueState` with TTL |
| **Redis** | Transactions: MULTI/EXEC/WATCH (optimistic locking); Lua scripting | Optimistic concurrency control | vs. DB transaction isolation levels; Lua-as-atomic-unit as a lighter alternative to full ACID | Implement "decrement stock if available" via WATCH/MULTI, then again via Lua — compare |
| **Elasticsearch** | Cluster architecture: node roles, shards/replicas, cluster state | Master-eligible quorum + independent data sharding | vs. ClickHouse's shard+replica model (same shape, different consensus mechanism) | Sketch role assignment for a 6-node cluster given a target workload |
| **ClickHouse** | Replication: ReplicatedMergeTree + ClickHouse Keeper (**your exact cluster setup**) | Raft-coordinated metadata + async data replication | Keeper vs ZooKeeper — why ClickHouse built its own | Trace how a write propagates through Keeper metadata + replica fetch on your 3-node cluster |
| **Architecture** | Distributed transactions: 2PC, Saga, Outbox | Coordinating state without global locks | 2PC's blocking cost vs Saga's compensating actions (Kafka-backed microservices) | Sketch a Saga for a multi-step order-processing flow using Kafka events |

---

### Day 6

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Structured Streaming: micro-batch, triggers, watermarking, checkpointing | Micro-batch vs true streaming | Sets up the direct Flink comparison (Architecture Day 11's Lambda/Kappa) | Run a job with `trigger(processingTime=...)`, inspect the checkpoint directory |
| **Kafka** | Schema Registry: Avro/Protobuf, compatibility modes (backward/forward/full) | Contract-first schema evolution | vs. Protobuf/gRPC service contracts — same governance problem, different transport | Evolve a schema (add optional field), verify the compatibility check |
| **Flink** | Checkpointing: Chandy-Lamport asynchronous barrier snapshotting, savepoints | Distributed consistent snapshot algorithm | **This is the exact mechanism behind your JobManager-instability debugging** | Enable checkpointing, kill a TaskManager mid-job, verify recovery from last checkpoint |
| **Redis** | Eviction: LRU/LFU/random/noeviction, memory fragmentation | Approximate-LRU via sampling (not a true LRU list) | Same trade-off as CDN/OS page-cache eviction: accuracy vs overhead | Fill a maxmemory-limited instance with `allkeys-lru`, observe eviction |
| **Elasticsearch** | Indexing internals: segments, refresh/flush/merge, near-real-time search | LSM-style segment merging | **Direct cross-link to ClickHouse Day 6 — same storage-engine family** | Bulk-index docs, tune `refresh_interval`, observe search-visibility delay |
| **ClickHouse** | Materialized Views: normal vs **Refreshable MV** (your exact BigQuery-scheduled-query mapping task) | Incremental view maintenance vs periodic recompute | vs. BigQuery scheduled queries, vs. Snowflake dynamic tables | Build a Refreshable MV mirroring one of your real BigQuery scheduled queries |
| **Architecture** | Caching strategy at the architecture level: CDN, cache hierarchies, invalidation | "There are only two hard things in CS…" | — | Map your own MDO portal's cache layers (browser → CDN → app → DB) and mark the suspected bypass point |

---

### Day 7 — Lab + Week 1 Review (all 7 tracks)

Combine everything above into one sitting:
1. Stand up Kafka + Redis + Elasticsearch + ClickHouse locally (Docker Compose — reuse
   the pattern from `legacy-5-day-plan/FinalProject/docker-compose.yml` as a starting
   point, extended with a ClickHouse service).
2. Produce events into Kafka; write them to Redis (cache) and Elasticsearch (search)
   directly as a warm-up (Flink/Spark join the pipeline properly in Week 2).
3. Write one **ADR** (Architecture Decision Record) picking a consistency model
   (strong vs. eventual) for a hypothetical feature at work, using the Day 1 CAP/PACELC
   framing. This is your first artifact — see the ADR template referenced in
   `../Week-04-Architecture-Mastery/README.md`.
4. Fill in your Week 1 row in `../PROGRESS_TRACKER.md`.

**Checkpoint:** you should be able to draw each of the 7 systems' basic architecture
from memory and explain, out loud, one design pattern each system embodies.
