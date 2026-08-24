# Day 25: ClickHouse — Design the Actual MDO Portal Migration

## Time: ~45 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Design the actual MDO portal migration end to end: schema, caching layer,
Looker native connector, and a direct fix for the fan-out and cache-bypass
problems — as a real, presentable deliverable.

## 2. Core Concept (basics → advanced)

This is the day every ClickHouse lesson this month has been building toward.
The design has five concrete components, each backed by a specific lesson:

1. **Schema design**: OBT vs. star-schema vs. dictionary decision per table
   (Day 22), informed by actual dimension update-frequency and cardinality for
   your real MDO portal tables.
2. **Sharding key**: chosen per Week 1, Day 4's reasoning, validated against
   your actual query patterns (which dashboards filter by which dimension
   most often).
3. **Storage tiering**: hot/cold TTL policy (Week 2, Day 10) matching your
   actual query-recency distribution.
4. **Fan-out fix**: every dashboard query identified in Week 2, Day 9/11's
   investigation, fixed via aggregate-before-join or dictionary conversion.
5. **Looker native connector + caching layer**: addressing Week 1, Day 6's
   cache-bypass investigation and Day 25's Redis-lesson fix design directly,
   ensuring the BI layer's own caching doesn't reintroduce the exact problem
   you're migrating away from.

## 3. How It Really Works (Internals)

The design's coherence comes from every component being **derived from
evidence gathered this month**, not from generic best practices applied
in the abstract: the sharding key should be the one Week 1 Day 4's cardinality
analysis actually supports for your real org/tenant distribution; the fan-out
fixes should be the specific queries Week 2 Day 9's investigation actually
found; the tiering policy should reflect Week 2 Day 10's actual query-recency
findings. This is what makes the difference between a generic "here's how you'd
design a ClickHouse migration" document and a genuinely useful, specific
artifact for your own team.

## 4. Architecture & Design Pattern Spotlight

**Pattern: evidence-derived design — every architectural decision traceable to
specific evidence gathered across this month's investigations, not generic
best practice applied blindly.** This is the single most important discipline
distinguishing a genuinely useful migration design from a template exercise.

## 5. Hands-On Lab

Produce the actual design document, with five sections matching the
components above. For each, cite the specific evidence (which lesson, which
investigation, which measured number) that drove the decision. This document
is explicitly meant to be shared with your team — write it at that level of
polish, not as a personal study note.

## 6. Real-World Product Comparison

This is your own real migration design — the "comparison" is against your
current BigQuery/Looker Pro architecture, quantified via Day 20's cost model.

## 7. Common Production Pitfalls

- Producing a generic migration design that could apply to any organization,
  rather than one grounded in your own specific evidence and constraints.
- Not explicitly addressing the fan-out and cache-bypass problems as part of
  the *new* design (rather than assuming they simply won't recur) — the new
  architecture needs deliberate safeguards (dictionaries where appropriate,
  disciplined cache-key design), not just a hope that a new engine avoids old
  mistakes automatically.

## 8. Review Questions
1. What are the five components of this migration design?
2. What specific evidence (from this month) drives each one?
3. How does the design explicitly prevent the fan-out and cache-bypass
   problems from recurring?
4. Is this document ready to actually share with your team?

## 9. Proficiency Checkpoint
If you've produced a genuinely complete, evidence-grounded migration design
document, you're at Level 4 — this is the literal capstone deliverable of the
entire curriculum's ClickHouse track.

## Next
Today's Architecture lesson assembles this alongside every other track's
real-work output into the full end-to-end capstone design.
