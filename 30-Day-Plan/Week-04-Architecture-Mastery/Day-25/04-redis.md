# Day 25: Redis — Design the Actual MDO-Portal Cache-Bypass Fix

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Design the actual fix for the MDO-portal cache-bypass problem, using this
month's caching-pattern and monitoring knowledge, as a concrete deliverable.

## 2. Core Concept (basics → advanced)

Week 1, Day 6 had you sketch the MDO portal's cache hierarchy and mark a
suspected bypass point. Week 2, Day 11 gave you the specific caching-pattern
vocabulary (cache-aside, write-through) and staleness-window reasoning. Week
3, Day 17 gave you the monitoring tools (`INFO` stats, hit/miss ratios) to
*measure* whether a bypass is actually happening, rather than just suspecting
it. Today: combine all three into an actual, evidence-based fix design.

## 3. How It Really Works (Internals)

The specific diagnostic sequence worth following: first, use Week 3 Day 17's
`keyspace_hits`/`keyspace_misses` monitoring to **measure** actual cache
hit rate for the suspected bypass point — confirming or ruling out the
hypothesis with real data, not just architectural suspicion. If a bypass is
confirmed, use Week 1 Day 6's framework to identify *which specific*
mechanism is responsible (an overly-specific cache key, a missing
invalidation path, an embedded iframe's different request headers). Then
choose the correct caching pattern (Week 2, Day 11) for the fix — likely
cache-aside with corrected key design, given the read-heavy, dashboard-style
access pattern this data almost certainly has.

## 4. Architecture & Design Pattern Spotlight

**Pattern: evidence-based fix design — measure first (Week 3's monitoring),
diagnose precisely (Week 1's cache-hierarchy framework), then apply the
right pattern (Week 2's caching taxonomy) — the same "measure, diagnose, fix"
discipline from every diagnostic lesson this month, applied to your actual,
real production bug.**

## 5. Hands-On Lab

Produce the actual fix design: (1) the measured hit/miss ratio evidence for
the suspected bypass point, (2) the precise mechanism identified as
responsible, (3) the specific caching pattern and cache-key redesign chosen
as the fix, and (4) the specific monitoring you'd add going forward
(Week 3, Day 17) to confirm the fix worked and catch any regression.

## 6. Real-World Product Comparison

This is your own real production fix.

## 7. Common Production Pitfalls

- Proposing a fix based on architectural suspicion alone, without the
  measured evidence step — risking a fix for the wrong root cause.
- Fixing the bypass without adding monitoring to confirm the fix holds over
  time as the portal's query patterns evolve.

## 8. Review Questions
1. What specific evidence would confirm (or rule out) the suspected bypass
   point?
2. What's the precise mechanism responsible, once confirmed?
3. What caching pattern and cache-key redesign fixes it?
4. What ongoing monitoring confirms the fix and catches future regression?

## 9. Proficiency Checkpoint
If you've produced a real, evidence-based fix design for this actual
production issue, you're at Level 4 — a genuinely deployable deliverable.

## Next
This feeds directly into today's ClickHouse lesson's MDO portal migration
design, which addresses this same cache-bypass problem as part of the
broader architecture.
