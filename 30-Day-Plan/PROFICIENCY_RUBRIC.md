# Proficiency Rubric — What "Level 4/5" Actually Means

Self-assessment only works if the levels are concrete. Use this to score yourself
honestly at the end of each week (`PROGRESS_TRACKER.md` has a scoring table), not just
at Day 30.

## The 5 Levels (apply to any of the 7 tracks)

| Level | Name | What you can do |
|-------|------|------------------|
| **1** | Aware | You know the tool exists and roughly what problem it solves. Can't operate it unsupervised. |
| **2** | Beginner | You can install it, run the basic API/CLI, and complete tutorial-shaped tasks. You know the 6–8 core vocabulary terms (e.g., for Kafka: topic, partition, broker, offset, consumer group). This is where the **original 5-day plan** topped out. |
| **3** | Working proficiency | You can build a real (if small) feature with it without copy-pasting blindly, explain the architecture diagram from memory, and debug the top 3–4 common errors. You know roughly how it works internally, even if you couldn't rebuild it. |
| **4** | **Advanced / production-capable** | You can **design** a solution using the tool for a given business constraint, **tune** it for a known bottleneck, **diagnose production incidents** without a runbook, and articulate **when the tool is the wrong choice**. You can compare it credibly against 2–3 alternatives with specific trade-offs (not just "it's faster"). You could onboard a teammate. |
| **5** | Expert / specialist | You've hit non-obvious edge cases in production, could contribute to the project's internals or write a conference talk on it, and are the person your org escalates to. This usually takes **months of production scars**, not 30 days — treat it as the target for 1–2 tracks you specialize in *after* this month, not all 7. |

**The 30-day target is Level 4 across all seven tracks**, with the Capstone (Days
28–30) pushing you to 4–4.5 by forcing you to integrate, document, and defend the whole
system rather than one tool in isolation. Level 5 is explicitly out of scope for a
30-day plan — see the "Path to Level 5" section in the Capstone README for what
comes after.

---

## Per-Track Level 4 Checklist

Use these as the literal exit bar for Week 4 / the Capstone. If you can't do most of
these unaided, you're at Level 3, not 4 yet — that's fine, note it and keep practicing
that track a bit longer before moving on.

### PySpark — Level 4 means you can:
- [ ] Explain a Spark UI DAG/stage graph for a job you didn't write, and identify the shuffle
- [ ] Diagnose an executor OOM or GC-overhead error from logs/metrics alone
- [ ] Choose join strategy (broadcast/shuffle-hash/sort-merge) and justify it
- [ ] Decide Spark vs. Trino vs. DuckDB/Polars vs. ClickHouse for a given workload

### Kafka — Level 4 means you can:
- [ ] Explain ISR, leader election, and what `min.insync.replicas` actually protects against
- [ ] Diagnose consumer lag and rebalancing storms from metrics
- [ ] Design a topic/partition layout for a given throughput + ordering requirement
- [ ] Decide Kafka vs. Pulsar vs. Redpanda vs. a cloud queue for a given use case

### Flink — Level 4 means you can:
- [ ] Explain checkpointing/barriers well enough to diagnose a stuck or endlessly-restarting job
- [ ] Distinguish a legitimate job completion from a bounded-source misconfiguration
- [ ] Tune state backend and parallelism for a known backpressure symptom
- [ ] Decide Flink vs. Spark Structured Streaming vs. Kafka Streams for a given latency need

### Redis — Level 4 means you can:
- [ ] Pick the right caching pattern (aside/through/behind) for a given consistency need
- [ ] Explain Cluster resharding and Sentinel failover well enough to run a live failover
- [ ] Diagnose a hot-key or memory-fragmentation problem
- [ ] Decide Redis vs. Memcached vs. DragonflyDB vs. an embedded cache

### Elasticsearch — Level 4 means you can:
- [ ] Design an ILM hot-warm-cold policy for a time-series/log dataset
- [ ] Diagnose a slow query using the profiling API and fix the mapping/query
- [ ] Explain BM25 well enough to tune relevance for a real search problem
- [ ] Decide Elasticsearch vs. OpenSearch vs. ClickHouse vs. a hosted search service

### ClickHouse — Level 4 means you can:
- [ ] Design a sharding key and choose the right MergeTree variant for a workload
- [ ] Diagnose and fix a JOIN fan-out / row-multiplication bug
- [ ] Build a Refreshable Materialized View that correctly replaces a scheduled query
- [ ] Produce a defensible cost/performance comparison vs. BigQuery/Snowflake/Druid

### Architecture & System Design — Level 4 means you can:
- [ ] Pick a consistency model and defend it against CAP/PACELC trade-offs
- [ ] Write a one-page ADR for a real infrastructure decision with alternatives considered
- [ ] Draw and explain a Lambda/Kappa architecture and know which one you're actually running
- [ ] Lead a design review and respond to "why not just use X" challenges credibly

---

## How to Self-Score

At the end of each week, in `PROGRESS_TRACKER.md`, give yourself an honest 1–5 per
track. Two rules:

1. **Score against the checklist above, not against how much you read.** Reading about
   ISR is Level 2 evidence; diagnosing a real rebalancing storm is Level 4 evidence.
2. **It's fine to be uneven.** You'll likely hit Level 4 on ClickHouse and Architecture
   faster (they map to your live work) than on, say, Elasticsearch if you touch it less
   day to day. Note the gap and decide whether to spend an extra day there before the
   Capstone.
