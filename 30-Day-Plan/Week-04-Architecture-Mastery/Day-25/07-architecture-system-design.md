# Day 25: Architecture — Full Capstone Design: BigQuery/Looker Pro → ClickHouse/Looker

## Time: ~45 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Produce the full, end-to-end target-state architecture design — the single
document this entire month has been building toward — treating today's output
as a genuine draft you could bring to your team.

## 2. Core Concept (basics → advanced)

Today's document assembles every other track's Day 25 output into one
coherent whole, using Day 22's reference-architecture template as its
structural skeleton:

```
[Sunbird/production sources] ──▶ Kafka (redesigned per today's Kafka lesson:
                                          EOS, tiering, CDC where appropriate)
                                     │
                                     ▼
                                 Flink (redesigned per today's Flink lesson:
                                        audited bounded/unbounded config,
                                        proper checkpointing discipline)
                                     │
                                     ├──▶ ClickHouse (today's ClickHouse
                                     │    lesson's full migration design:
                                     │    schema, sharding, tiering, fan-out
                                     │    fixes)
                                     │
                                     ├──▶ Redis (today's Redis lesson's
                                     │    cache-bypass fix: corrected
                                     │    cache-aside pattern + monitoring)
                                     │
                                     └──▶ [ES workload: migrated or retained,
                                           per today's Elasticsearch lesson's
                                           honest assessment]
                                     │
                                     ▼
                             Looker (native ClickHouse connector,
                                     caching layer NOT reintroducing the
                                     original bypass problem)
```

## 3. How It Really Works (Internals)

The document's actual value to your team depends on it doing something a
generic architecture diagram cannot: **explicitly connecting each design
decision back to the specific evidence and lesson that produced it** —
exactly Day 25's ClickHouse lesson's discipline, applied here at the
whole-architecture level. A reviewer (Day 27's mock review) should be able to
ask "why did you choose this sharding key" and receive an answer citing
specific cardinality data from Week 1 Day 4's investigation, not a general
appeal to best practice.

## 4. Architecture & Design Pattern Spotlight

**Pattern: the complete reference architecture (Day 22) instantiated with
real, evidence-derived decisions across every component — the single
synthesis artifact this entire 30-day curriculum has been building toward.**

## 5. Hands-On Lab

Assemble the full document: the end-to-end diagram above, populated with
your actual real components and decisions, plus a written section per major
component citing the specific evidence/lesson driving each decision, plus an
explicit "risks and open questions" section (anything from today's individual
tracks you weren't fully able to resolve). This is the document Day 27's mock
review will stress-test.

## 6. Real-World Product Comparison

This is your own real target-state architecture — informed by, and directly
comparable to, the case studies from Day 23.

## 7. Common Production Pitfalls

- Producing a polished-looking diagram without the underlying evidence-
  citation discipline, making it look complete while actually being
  under-justified.
- Not including an honest "risks and open questions" section — a document
  that claims perfect confidence in every decision is less credible, and less
  useful, than one that's honest about genuine remaining uncertainty.
- Treating this as a final document rather than a living draft — expect Day
  27's mock review to surface changes worth making before this goes to actual
  stakeholders.

## 8. Review Questions
1. What's the specific evidence behind your three most important
   architectural decisions in this document?
2. What genuine risks or open questions remain?
3. Is this document ready for a real stakeholder audience, or does it need
   another revision pass?
4. How would you defend your sharding-key choice if directly challenged?

## 9. Proficiency Checkpoint
If you've produced this complete, evidence-grounded capstone document, you're
at Level 4 — this is the tangible output of the entire month's work, ready
for Day 26's integration check and Day 27's mock review.

## Next
Day 26 is integration day — verifying every pairwise system interaction in
this design actually works as intended.
