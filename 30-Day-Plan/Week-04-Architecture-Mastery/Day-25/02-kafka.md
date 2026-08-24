# Day 25: Kafka — Redesign the Sunbird Telemetry Backbone

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Redesign the Sunbird telemetry backbone using this month's exactly-once
semantics, tiered storage, and Connect/CDC knowledge.

## 2. Core Concept (basics → advanced)

Your Sunbird telemetry pipeline (Kafka routing, Flink processing, Redis
dedup, Druid storage — documented in your Confluence work) predates this
month's deep dive into exactly-once semantics (Week 2, Day 9), tiered storage
(Week 2, Day 10), and Kafka Connect/CDC (Week 2, Day 13). Worth an honest
redesign pass: does the current pipeline have any at-least-once (rather than
exactly-once) semantics where duplicate telemetry events could skew downstream
analytics? Is retention/tiering configured deliberately (Week 2, Day 10), or
default? Would any part of the pipeline benefit from CDC (Week 2, Day 13)
rather than application-level event emission?

## 3. How It Really Works (Internals)

The Redis-based deduplication step in your existing pipeline is itself a signal
worth examining closely: if Kafka's own idempotent producer and exactly-once
semantics (Week 2, Day 9) were correctly configured end to end, would the
Redis dedup step become unnecessary, or does it serve a genuinely distinct
purpose (e.g., deduplicating across a boundary EOS doesn't cover, like
client-side retry duplicates from before events even reach Kafka)? This is
exactly the kind of question this month's depth now equips you to answer
precisely rather than leave as an inherited design assumption.

## 4. Architecture & Design Pattern Spotlight

**Pattern: redesigning a real, currently-running pipeline with newly-acquired
depth — the same audit discipline as today's PySpark lesson, applied to
Kafka's specific role in your telemetry backbone.**

## 5. Hands-On Lab

Diagram your current Sunbird Kafka topology (topics, partition counts,
retention settings, producer/consumer configuration) and, for each component,
write down: does this reflect Week 2's exactly-once, tiering, and CDC
knowledge, or was it configured before this depth was available? Specifically
assess whether the Redis dedup step's job could be partially or fully absorbed
by correctly-configured Kafka EOS, and what would change if so.

## 6. Real-World Product Comparison

This is your own real pipeline — informed by this month's material.

## 7. Common Production Pitfalls

- Treating an inherited architectural decision (like the Redis dedup step) as
  permanently necessary without periodically re-examining whether newer
  knowledge changes the calculus.
- Redesigning without validating the change against the pipeline's actual
  current behavior — propose the change, but plan to verify it, not just
  assume it.

## 8. Review Questions
1. Does your Redis dedup step serve a purpose EOS wouldn't cover?
2. Is your retention/tiering configuration deliberate or default?
3. Where might CDC (Week 2, Day 13) simplify a current event-emission
   mechanism?
4. What's the single highest-value redesign change you'd prioritize first?

## 9. Proficiency Checkpoint
If you've produced a specific, evidence-based redesign proposal for a real
pipeline component, you're at Level 4.

## Next
This feeds into the Flink lesson's redesign of the Sunbird Flink jobs
themselves.
