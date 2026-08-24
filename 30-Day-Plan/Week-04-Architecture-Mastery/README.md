# Week 4 — Architecture Mastery
### Target exit proficiency: Level 4 on all 7 tracks

Week 4 is where the pieces from Weeks 1–3 turn into judgment: naming design patterns
you've now used hands-on, knowing real companies' choices well enough to reason from
them (not just cite them), and — critically — knowing when *not* to reach for each
tool. Day 25 turns this straight into your actual live work: the MDO portal migration
design. Day 27 is a dry run for defending it in a real review.

No full lesson files exist yet for Week 4 — every day below is a complete brief. See
`../HOW_TO_CONTINUE.md` to expand any day into a full lesson.

---

### Day 22 — Design Patterns

| Track | Focus | Pattern spotlight | Product comparison angle | Lab |
|---|---|---|---|---|
| **PySpark** | Lambda batch layer, Medallion architecture (bronze/silver/gold), `MERGE`-based upserts | Layered data refinement | — | Sketch a Medallion pipeline for one of your real datasets |
| **Kafka** | Event sourcing, CQRS backbone, Transactional Outbox, Saga | Kafka as the durable log underneath 4 different patterns | — | Pick one pattern and sketch it using a topic you already have |
| **Flink** | Kappa architecture (Flink as the sole processing layer), Stateful Functions | Stream-only architecture | — | Redraw your Lambda-ish current setup as a Kappa alternative — what would you drop? |
| **Redis** | Redlock distributed locking (**and Martin Kleppmann's critique of it** — a genuinely important nuance), rate-limiting patterns | Distributed mutual exclusion, contested | — | Read a summary of the Redlock safety debate and form your own view on when it's "good enough" |
| **Elasticsearch** | CQRS read-model (ES as the query side, fed by Kafka events), search-as-a-service facade | Read/write model separation, applied | Ties Kafka + Elasticsearch + CQRS (Week 2 Day 10) into one concrete design | Sketch a CQRS design with Kafka as the write path and ES as the read model |
| **ClickHouse** | Lambda/Kappa serving layer, "one big table" (OBT) denormalization vs. star schema | Serving-layer design for OLAP | Directly relevant to your MDO portal schema decisions | Compare an OBT design vs. a star-schema design for one of your real dashboards |
| **Architecture** | **Reference architecture: your real target stack, end to end** | Ingest → stream process → OLAP store → BI layer | — | Draw the full Kafka→Flink→ClickHouse→Redis/ES reference architecture as one diagram |

---

### Day 23 — Case Studies

| Track | Focus | Lab |
|---|---|---|
| **PySpark** | Databricks, Netflix, Airbnb | Read one public engineering blog post from each; note one architectural choice you didn't expect |
| **Kafka** | LinkedIn (origin), Netflix Keystone, Uber | Same exercise — one concrete takeaway per company |
| **Flink** | Alibaba (Blink), Uber, Stripe | Same |
| **Redis** | Twitter timelines, GitHub, Stack Overflow | Same — Stack Overflow's famously small server footprint is a good one to dig into |
| **Elasticsearch** | GitHub's historical code search, Uber logging, Wikipedia's CirrusSearch | Same |
| **ClickHouse** | Cloudflare, Uber, eBay | Same — Cloudflare's analytics scale is a strong anchor case study |
| **Architecture** | Netflix, Uber, Cloudflare, and LinkedIn's overall **data platforms** (not just one tool) | Synthesize: what's structurally similar across all 4 companies' platforms? |

---

### Day 24 — When NOT to Use It

| Track | Focus | Decision framework |
|---|---|---|
| **PySpark** | Latency floor, small-data overkill | Spark vs. Trino vs. DuckDB/Polars vs. ClickHouse |
| **Kafka** | Simple task queues, latency-sensitive RPC | Kafka vs. Pulsar vs. Redpanda vs. a cloud-native queue |
| **Flink** | Overhead for simple embedded transforms, batch-only workloads | Flink vs. Spark Streaming vs. Kafka Streams vs. ksqlDB |
| **Redis** | Durability-critical primary storage, datasets far exceeding RAM economics | Redis vs. Memcached vs. DragonflyDB vs. an embedded cache |
| **Elasticsearch** | **ES vs. ClickHouse for aggregation-heavy dashboards — directly relevant to your work** | When search-engine aggregations lose to purpose-built OLAP |
| **ClickHouse** | High-concurrency point lookups, frequent updates/deletes, small datasets | ClickHouse vs. Druid vs. Pinot vs. BigQuery vs. Snowflake |
| **Architecture** | Trade-off frameworks: build vs. buy, the "boring technology" principle | Apply the framework to one real upcoming decision at work |

**Lab (all tracks):** for each tool, write the one sentence you'd say in a design review
when someone proposes it for the wrong job — this is the actual Level 4 skill.

---

### Day 25 — Your Real Work, As a Case Study

| Track | Focus |
|---|---|
| **PySpark** | Revisit your own S6 lakehouse benchmark with this month's deeper Spark/Iceberg knowledge — what would you change? |
| **Kafka** | Redesign the Sunbird telemetry backbone with what you now know about EOS, tiered storage, and Connect/CDC |
| **Flink** | Redesign your Sunbird Flink jobs with proper bounded/unbounded source handling and checkpointing discipline |
| **Redis** | Design the actual MDO-portal cache-bypass fix, using Week 2/3's caching-pattern and monitoring knowledge |
| **Elasticsearch** | Honestly assess: could ClickHouse replace this ES workload? Write the comparison, not just the conclusion |
| **ClickHouse** | **Design the actual MDO portal migration**: schema, caching layer, Looker native connector, addressing the fan-out/cache-bypass problem directly |
| **Architecture** | **Full capstone design**: Tarento's BigQuery/Looker Pro → ClickHouse/Looker target-state architecture, end to end |

This is the day the whole month has been building toward — treat today's output as a
draft you could genuinely bring to your team.

---

### Day 26 — Integration Day

| Track | Integrations to build/sketch |
|---|---|
| **PySpark** | Spark+Kafka (structured streaming source), Spark+ClickHouse (JDBC writes), Spark+Redis (feature-store lookups) |
| **Kafka** | Kafka+Flink (exactly-once), Kafka+ClickHouse (Kafka table engine), Kafka+Redis (cache-invalidation events) |
| **Flink** | Flink+ClickHouse sink (exactly-once caveats — ClickHouse isn't transactional the same way), Flink+Redis (state lookups), Flink+ES sink |
| **Redis** | Redis+Kafka (invalidation events), Redis as a hot-tier cache in front of ClickHouse for point lookups |
| **Elasticsearch** | ES+Kafka/Flink ingestion, **ES vs. ClickHouse head-to-head** for your actual workload |
| **ClickHouse** | ClickHouse+Kafka, +Spark, +Redis — the full set, from the ClickHouse side |
| **Architecture** | **One component-interaction diagram** tying all 7 tracks' integrations above into a single picture |

---

### Day 27 — Interview-Readiness & Mock Review

Each track gets a staff/architect-level design question to answer out loud, unaided:
- **PySpark**: "Design a batch ETL platform for 50TB/day with strict SLAs."
- **Kafka**: "Design an event backbone for a multi-region e-commerce platform."
- **Flink**: "Design a real-time fraud-detection pipeline with sub-second latency."
- **Redis**: "Design a distributed cache for a read-heavy social feed."
- **Elasticsearch**: "Design a search platform for a marketplace with faceted filters."
- **ClickHouse**: "Design a real-time analytics platform to replace a BigQuery-based one."
- **Architecture**: **Mock Principal Architect review** — present your Day 25 MDO
  portal migration design to a skeptical "reviewer" (a colleague, or role-play with an
  AI) and defend at least 3 "why not just use X instead" challenges.

**Checkpoint:** update `../PROGRESS_TRACKER.md` — target Level 4 across all 7 tracks
before moving into the Capstone.
