# Product & Company Comparison Matrix

A single cross-reference for the "compare with existing top products" requirement, so
each day file can point here instead of re-deriving it. Every topic-day also has its own
comparison section relevant to that day's specific concept — this file is the
big-picture map.

---

## 1. Who Uses What (real adopters, for grounding)

| Tool | Origin | Notable adopters | What they use it for |
|------|--------|-------------------|------------------------|
| **Spark** | UC Berkeley AMPLab → Databricks | Databricks, Netflix, Airbnb, Uber | Batch ETL, ML feature pipelines, lakehouse compute |
| **Kafka** | LinkedIn | LinkedIn, Netflix (Keystone), Uber, Confluent | Event backbone, log aggregation, microservice decoupling |
| **Flink** | TU Berlin (Stratosphere) → Alibaba/Ververica | Alibaba (Blink), Uber, Netflix, Stripe | True streaming, real-time fraud/analytics, CEP |
| **Redis** | Salvatore Sanfilippo | Twitter, GitHub, Stack Overflow | Caching, session store, leaderboards, rate limiting |
| **Elasticsearch** | Shay Banon (built on Lucene) | GitHub (historically), Wikipedia (CirrusSearch), Uber (logging) | Full-text search, log/metric analytics |
| **ClickHouse** | Yandex | Cloudflare, Uber, eBay | Real-time OLAP analytics at very large scale |

---

## 2. Direct Alternative Comparisons (use these when a day says "compare against")

### Batch/Distributed Compute
| | Spark | Trino/Presto | DuckDB/Polars | ClickHouse |
|---|---|---|---|---|
| Model | Distributed, lazy DAG | Distributed, interactive SQL | Single-node, columnar | Distributed, columnar OLAP |
| Best for | Large ETL, ML pipelines | Federated interactive queries | Single-machine analytics | Real-time aggregation at scale |
| Weakness | Latency floor, JVM ops overhead | Not for heavy ETL/ML | No horizontal scaling | Not for OLTP or heavy JOINs |

### Event Streaming
| | Kafka | Pulsar | Redpanda | Cloud-native (Kinesis/PubSub/Event Hubs) |
|---|---|---|---|---|
| Model | Log-structured, JVM, (K)Raft | Segmented log, separate compute/storage | C++ rewrite, Kafka-API-compatible | Fully managed |
| Best for | General-purpose event backbone | Multi-tenant, geo-replicated | Lower ops overhead, no JVM/ZK | No ops burden at all |
| Weakness | Ops burden self-managed | Operational complexity (BookKeeper) | Smaller ecosystem | Vendor lock-in, less control |

### Stream Processing
| | Flink | Spark Structured Streaming | Kafka Streams | ksqlDB |
|---|---|---|---|---|
| Model | True per-record streaming | Micro-batch | Embedded library | SQL over Kafka Streams |
| Latency | Sub-second, lowest | Seconds (micro-batch) | Sub-second | Sub-second |
| Best for | Complex stateful streaming, CEP | Teams already on Spark | Simple embedded transforms | SQL-first teams |
| Weakness | Steeper learning curve, JVM ops | Not true streaming | Limited to JVM apps | Less flexible than raw API |

### Caching / In-Memory
| | Redis | Memcached | DragonflyDB | Valkey |
|---|---|---|---|---|
| Model | Single-threaded event loop, rich types | Multi-threaded, simple KV | Multi-threaded, Redis-API-compatible | Redis fork (Linux Foundation) |
| Best for | Rich data structures, pub/sub, streams | Pure cache, max simplicity | Higher throughput on multi-core boxes | Open-license drop-in replacement |
| Weakness | Single-threaded ceiling per instance | No advanced data structures | Newer, smaller track record | Ecosystem still catching up |

### Search / Analytics on Text & Logs
| | Elasticsearch | OpenSearch | Typesense/Meilisearch | Algolia |
|---|---|---|---|---|
| Model | Lucene-based, distributed | Elasticsearch fork (AWS-led) | Lightweight, developer-first | Fully hosted SaaS |
| Best for | Full-text + log analytics at scale | Same, open-license concerns | Simple, fast typo-tolerant search | Zero-ops hosted search |
| Weakness | Licensing history, ops overhead | Smaller ecosystem than ES | Less mature at massive scale | Cost at scale, less control |

### OLAP / Analytics Warehouse
| | ClickHouse | BigQuery | Snowflake | Druid |
|---|---|---|---|---|
| Model | Self-hosted (or Cloud), columnar MergeTree | Serverless, pay-per-byte-scanned | Cloud warehouse, compute/storage separated | Real-time OLAP, segment-based |
| Best for | Cost control at scale, sub-second dashboards | Zero ops, ad hoc analyst queries | Enterprise data warehousing | Real-time ingestion + sub-second slice-and-dice |
| Weakness | Ops burden self-hosted, JOIN caution | Cost can spiral with scan volume | Cost, less low-level control | Narrower use case, ops-heavy |

**This last row is your live decision** — the ClickHouse POC vs. BigQuery/Looker Pro.
Days 20–21 and 25 in the curriculum build the actual cost/performance comparison
artifacts for it.

---

## 3. The Recurring Meta-Pattern

Notice the same three tensions show up in every row above:

1. **Self-hosted control vs. managed simplicity** (ClickHouse vs. BigQuery, Kafka vs.
   MSK, Redis vs. ElastiCache).
2. **General-purpose vs. purpose-built** (Spark vs. ClickHouse for analytics, Kafka vs.
   a simple queue for basic pub/sub).
3. **Ecosystem maturity vs. newer/leaner rewrites** (Kafka vs. Redpanda, Elasticsearch
   vs. OpenSearch, Redis vs. DragonflyDB).

Every "when NOT to use X" section in Week 4 comes back to these three tensions — once
you can articulate them for one tool, you can basically transfer the reasoning to any
new tool you meet after this course.
