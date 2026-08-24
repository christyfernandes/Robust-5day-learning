# Day 24: Flink — When NOT to Use It

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Write the one sentence you'd say in a design review when someone proposes
Flink for the wrong job.

## 2. Core Concept (basics → advanced)

Flink's architecture — a full distributed streaming engine with checkpointing
(Week 1, Day 6), state backends (Week 1, Day 5), and a JobManager/TaskManager
cluster topology (Week 1, Day 1) — is genuine overhead for:
- **Simple, embedded transforms**: if your actual need is "transform each
  message as it arrives, no cross-event state, no windowing," a lightweight
  in-process transformation (or even Kafka Streams' embedded model, Week 2 Day
  8) avoids standing up and operating a whole separate cluster for logic that
  doesn't need Flink's distributed-state machinery at all.
- **Batch-only workloads**: if there's genuinely no streaming requirement (a
  nightly recompute with no low-latency need), Spark's batch model (or even
  simpler tools) fits the actual requirement better than forcing a
  streaming-shaped tool onto a batch-shaped problem.

## 3. How It Really Works (Internals)

The correct mental test: **does this job need continuous, low-latency,
stateful processing over an unbounded stream — the specific problem Flink's
architecture is built for** — or would a simpler embedded transform, Kafka
Streams (Week 2, Day 8), or a scheduled batch job serve the actual requirement
with less operational overhead (no separate cluster, no JobManager HA to
maintain, Week 3 Day 18)?

## 4. Architecture & Design Pattern Spotlight

**Pattern: matching tool architecture to actual problem shape — recognizing
that Flink's distributed streaming machinery is a real, deliberate investment
that should be reserved for problems that genuinely need it.**

## 5. Hands-On Lab

Write the one sentence you'd say in a design review when someone proposes a
full Flink deployment for a workload that's really a simple, stateless,
embedded transformation.

## 6. Real-World Product Comparison

- **Kafka Streams** (Week 2, Day 8) is the right-sized tool for
  embedded, application-coupled stream processing without a separate cluster.
- **ksqlDB** offers a lighter-weight managed alternative for teams wanting
  SQL-based stream processing without Flink's full operational surface area.

## 7. Common Production Pitfalls

- Standing up and operating a full Flink cluster (with all of Week 3's
  associated operational burden) for logic simple enough for an embedded
  transform.
- Using Flink for a genuinely batch-only workload out of habit or team
  familiarity, missing a simpler-fitting tool.

## 8. Review Questions
1. What specific Flink machinery is unnecessary overhead for a simple,
   stateless embedded transform?
2. When would Kafka Streams be the better-fitting choice?
3. What's your one-sentence design-review pushback?
4. What would make a workload genuinely need Flink, versus a simpler
   alternative?

## 9. Proficiency Checkpoint
If you have a real, specific pushback ready, you're at Level 4.

## Next
Day 25 applies this judgment to redesigning your own real Sunbird Flink jobs.
