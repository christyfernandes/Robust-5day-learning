# Day 22: Kafka — Design Patterns: The Durable Log Underneath Four Patterns

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Pick one of event sourcing, CQRS, Transactional Outbox, or Saga, and sketch it
using a topic you actually have — recognizing Kafka's log as the common
foundation beneath all four.

## 2. Core Concept (basics → advanced)

Four architectural patterns studied at various points this month, unified today by
one observation: **all four are built on the same underlying primitive — Kafka's
durable, ordered, replayable log** (Week 1, Day 1):

- **Event sourcing** (Week 2, Day 9): the log *is* the system of record; state is
  derived by replaying it.
- **CQRS** (Week 2, Day 10): the log is what synchronizes the write model with one
  or more read-model projections.
- **Transactional Outbox** (Week 1, Day 5): the log is what reliably carries "this
  local transaction happened" out of a database and into the wider system.
- **Saga** (Week 1, Day 5): the log is what carries each step's completion (or
  failure) to trigger the next step or a compensating action.

## 3. How It Really Works (Internals)

What makes Kafka specifically well-suited as the shared foundation for all four
patterns is precisely its combination of **durability** (Week 1, Day 4's
replication), **ordering** (within a partition), and **replayability** (configurable
retention, or infinite via compaction, Week 2 Day 10) — event sourcing needs
durable, ordered, replayable history; CQRS needs a reliable way to propagate write-
side changes to read models; Outbox needs guaranteed, at-least-once delivery of "this
happened" events; Saga needs ordered, reliable delivery of step-completion signals.
No single property alone would suffice for all four — it's the *combination* that
makes Kafka a natural fit as the shared backbone.

## 4. Architecture & Design Pattern Spotlight

**Pattern: Kafka as the durable log underneath multiple architectural patterns —
recognizing that "which pattern am I using" and "what's my event backbone" are
separate questions, with Kafka frequently serving as the answer to the second
regardless of the answer to the first.** This reframes patterns studied
individually earlier this month as variations built on one shared foundational
capability, rather than four unrelated techniques.

## 5. Hands-On Lab

Pick one topic you actually have (or a realistic one from your Sunbird pipeline)
and sketch how it would need to change (if at all) to fully support one of the
four patterns above — e.g., if you picked event sourcing, would your current topic
need infinite retention/compaction to serve as a genuine system of record? If CQRS,
what read-model projection would consume it, and via what mechanism (a
Materialized View, Week 1 Day 6; an Elasticsearch index, today's Elasticsearch
lesson)?

## 6. Real-World Product Comparison

- **Uber's** and **Netflix's** internal architectures use Kafka as the shared
  backbone across multiple of these patterns simultaneously within the same
  organization — different teams building event-sourced services, CQRS read
  models, and Saga-based workflows, all on the same underlying Kafka
  infrastructure.
- This is directly the shape of your own **Sunbird telemetry pipeline** — worth
  explicitly identifying which of these four patterns (if any) it currently
  resembles, and whether a different one would serve its actual requirements
  better.

## 7. Common Production Pitfalls

- Treating these four patterns as requiring four separate messaging
  infrastructures, when a well-designed shared Kafka backbone can support all of
  them (with appropriate per-topic configuration).
- Choosing event sourcing (the heaviest commitment, Week 2 Day 9) when Outbox or
  simple event notification would have sufficed for the actual requirement.
- Not clearly documenting which pattern a given topic is meant to serve —
  ambiguity here leads to topics being used inconsistently by different consumers
  with different assumptions.

## 8. Review Questions
1. What three Kafka properties combine to make it suitable as the shared
   foundation for all four patterns?
2. Why is "which pattern" a separate question from "what's my event backbone"?
3. Which of these four patterns most closely resembles your own Sunbird pipeline
   today?
4. What would need to change to make it a better fit for a different pattern?

## 9. Proficiency Checkpoint
If you can pick the right pattern for a stated requirement and sketch its Kafka-
backed implementation, you're at Level 4.

## Next
Day 23 covers Kafka case studies — LinkedIn, Netflix Keystone, Uber.
