# Day 23: Kafka — Case Studies: LinkedIn, Netflix Keystone, Uber

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Extract one concrete takeaway from LinkedIn's, Netflix's, and Uber's public Kafka
usage, connecting each back to this month's specific lessons.

## 2. Core Concept (basics → advanced)

- **LinkedIn**: Kafka's birthplace — their engineering publications on Kafka's
  origin explain the founding motivation (Week 1, Day 3: many independent
  consumer groups reading the same log non-destructively) directly from the
  people who built it, a uniquely valuable primary source.
- **Netflix Keystone**: their real-time data pipeline platform, built heavily on
  Kafka, is extensively documented — a strong case study in operating Kafka at
  very large scale, including capacity planning (Week 3, Day 15) and reliability
  engineering (Week 3, Day 16) considerations.
- **Uber**: a heavy Kafka (and Flink) user for real-time pricing, ETA, and
  fraud-detection pipelines — their publications often discuss exactly-once
  semantics (Week 2, Day 9) and multi-region considerations (Week 3, Day 19) in
  concrete, production terms.

## 3. How It Really Works (Internals)

The specific translation skill: when Uber describes a real-time pricing
pipeline's requirements, can you identify which of this month's specific Kafka
mechanisms (partition-key design, Week 1 Day 3; exactly-once semantics, Week 2
Day 9; consumer-lag monitoring, Week 3 Day 17) are load-bearing for their stated
correctness/latency requirements? When LinkedIn discusses Kafka's original
motivating use case, can you connect it precisely to the consumer-group
fan-out property (Week 1, Day 3) rather than a vague "it's for messaging"
understanding?

## 4. Architecture & Design Pattern Spotlight

**Pattern: case-study literacy, applied to Kafka specifically** — the same
critical-reading skill from today's PySpark lesson, exercised on Kafka's own
origin story and two of its most demanding production users.

## 5. Hands-On Lab

Read a primary source from each: LinkedIn's original Kafka paper or a
retrospective engineering post, a Netflix Keystone architecture writeup, and an
Uber engineering post on a Kafka-based real-time pipeline. For each, write one
concrete takeaway and the specific Week 1-3 lesson it connects to most directly.

## 6. Real-World Product Comparison

This lesson *is* the comparison exercise.

## 7. Common Production Pitfalls

- Treating LinkedIn's founding use case as Kafka's *only* legitimate use case,
  missing how far its application has broadened since (event sourcing, CQRS,
  Week 4 Day 22).
- Assuming Uber-scale operational practices (extensive multi-region tooling,
  dedicated SRE teams) are the right target for a much smaller deployment.
- Reading case studies passively rather than actively connecting them back to
  specific mechanisms studied this month.

## 8. Review Questions
1. What was Kafka's original motivating use case at LinkedIn, precisely?
2. What's one specific mechanism from this month you saw referenced (even
   implicitly) in Uber's or Netflix's public accounts?
3. Why shouldn't Uber-scale practices necessarily be your own target?
4. What's the value of reading a primary source over a secondary summary?

## 9. Proficiency Checkpoint
If you can extract and precisely connect real-world takeaways to this month's
specific lessons, you're at Level 4.

## Next
Day 24 covers when NOT to use Kafka — the natural complement to today's
grounded, real-world usage study.
