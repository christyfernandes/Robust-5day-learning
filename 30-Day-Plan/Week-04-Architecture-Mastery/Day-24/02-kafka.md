# Day 24: Kafka — When NOT to Use It

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Write the one sentence you'd say in a design review when someone proposes Kafka
for the wrong job.

## 2. Core Concept (basics → advanced)

Kafka's architecture (Week 1, Day 1) — a durable, replicated, partitioned log —
is genuinely over-engineered for:
- **Simple task queues**: if you need "process this job exactly once, then
  discard it," a purpose-built task queue (or even a simpler broker like
  RabbitMQ, Week 1 Day 3's comparison) is a better structural fit than Kafka's
  log-retention model, which is solving a fundamentally different problem
  (durable, replayable history for potentially many independent consumers) than
  simple work distribution.
- **Latency-sensitive synchronous RPC**: Kafka is built for asynchronous,
  eventually-processed event flow — using it as a substitute for direct
  service-to-service RPC (where a caller needs an immediate, synchronous
  response) forces an awkward request/response pattern onto infrastructure not
  designed for it.

## 3. How It Really Works (Internals)

The correct mental test: **do you need durable replay for multiple independent
consumers, or just reliable one-time work distribution?** If it's genuinely the
latter, Kafka's replication (Week 1, Day 4), retention, and consumer-group
machinery (Week 1, Day 3) are solving problems you don't have, at real
operational cost (Week 3's cluster-sizing, monitoring, and security lessons all
become overhead for a use case simple enough not to need them).

## 4. Architecture & Design Pattern Spotlight

**Pattern: matching tool architecture to actual problem shape — recognizing
when Kafka's specific strengths (durable replay, fan-out to independent
consumers) aren't actually needed, versus when they genuinely are.**

## 5. Hands-On Lab

Write the one sentence you'd say in a design review when someone proposes
Kafka purely as a task queue with no genuine need for durable replay or
multi-consumer fan-out.

## 6. Real-World Product Comparison

- A **cloud-native managed queue** (SQS-style) is simpler and cheaper for pure
  work-distribution use cases with no replay/fan-out requirement.
- **Redpanda/Pulsar** (Week 3, Day 20) are still Kafka-shaped tools for
  Kafka-shaped problems — the "when NOT to use it" question here is really
  about whether you need this *category* of tool at all, not which specific
  implementation within it.

## 7. Common Production Pitfalls

- Standing up Kafka (and its full operational burden — Week 3's monitoring/
  security/DR lessons) for a use case a much simpler queue would serve just as
  well.
- Using Kafka for synchronous RPC, fighting its asynchronous design the whole
  way.

## 8. Review Questions
1. What's the structural difference between a task queue's needs and Kafka's
   design?
2. Why is Kafka a poor fit for synchronous RPC?
3. What's your one-sentence design-review pushback?
4. What would you propose instead for a simple, no-replay work-distribution use
   case?

## 9. Proficiency Checkpoint
If you have a real, specific pushback ready, you're at Level 4.

## Next
Day 25 applies this judgment to your own real Sunbird telemetry pipeline.
