# Day 26: PySpark — Integrations: Kafka, ClickHouse, Redis

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Sketch three concrete PySpark integration points: Structured Streaming from
Kafka, JDBC writes to ClickHouse, and Redis feature-store lookups.

## 2. Core Concept (basics → advanced)

- **Spark + Kafka**: Structured Streaming (Week 1, Day 6) reading directly
  from a Kafka source — the micro-batch model consuming Kafka partitions
  (Week 1, Day 3), with offsets tracked via Structured Streaming's own
  checkpoint mechanism rather than Kafka consumer-group offsets directly.
- **Spark + ClickHouse**: writing Spark DataFrame output to ClickHouse via its
  JDBC driver — worth noting this is a batch-oriented write path, not a
  substitute for the native Kafka table engine ingestion (Week 2, Day 13) when
  genuine streaming ingestion is the actual requirement.
- **Spark + Redis**: a common feature-store pattern — a Spark batch job
  computes features (e.g., aggregated user statistics) and writes them to
  Redis for low-latency serving lookups by an online system, a batch-compute/
  low-latency-serve split similar in spirit to Week 2 Day 10's CQRS pattern.

## 3. How It Really Works (Internals)

The genuinely important integration detail for the Spark-to-ClickHouse JDBC
path: batch JDBC writes don't automatically benefit from ClickHouse's bulk-
insert optimizations the way native ingestion methods (the Kafka table engine,
or ClickHouse's native bulk-insert protocols) do — for high-volume writes,
worth explicitly checking whether the JDBC path's batch size and insert
pattern are tuned appropriately, or whether a native ClickHouse client
library would perform meaningfully better for your actual write volume.

## 4. Architecture & Design Pattern Spotlight

**Pattern: integration-point-specific tuning — each of these three pairings
has its own specific configuration considerations, distinct from either
system's standalone tuning (Weeks 1-3).**

## 5. Hands-On Lab

Sketch (or, if relevant to your real architecture, actually configure) each
of the three integrations for a hypothetical or real use case: a Structured
Streaming job consuming Sunbird-shaped events from Kafka, a batch job writing
aggregated results to ClickHouse via JDBC, and a feature-computation job
writing to Redis for serving. For the ClickHouse write specifically, note
what batch size/insert pattern you'd tune and why.

## 6. Real-World Product Comparison

This directly informs your own migration's ingestion-pipeline design choices.

## 7. Common Production Pitfalls

- Using naive, small-batch JDBC writes to ClickHouse for high-volume data,
  missing much better native ingestion performance.
- Not distinguishing Structured Streaming's own checkpoint-based offset
  tracking from Kafka's native consumer-group offset tracking when reasoning
  about exactly-once behavior across a restart.

## 8. Review Questions
1. Why might native ClickHouse ingestion outperform a naive JDBC write path?
2. How does Structured Streaming track offsets, relative to Kafka consumer
   groups directly?
3. What's the batch-compute/low-latency-serve split in the Spark+Redis
   feature-store pattern?
4. Which of these three integrations is most relevant to your own real
   pipeline?

## 9. Proficiency Checkpoint
If you can specify tuned, integration-specific configuration for all three
pairings, you're at Level 4.

## Next
Day 27 is your final interview-readiness and mock-review day.
