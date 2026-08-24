# Day 20: Architecture — Cost-Aware Architecture: FinOps & Build-vs-Buy

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Write down the 3 biggest cost levers in your target architecture, ranked — a
direct, practical synthesis of this entire week's cost-related lessons.

## 2. Core Concept (basics → advanced)

**FinOps** treats cost as a first-class architectural input, on par with
performance, reliability, and security — not an afterthought calculated once a
design is already finalized. This week's lessons have each, in their own track,
demonstrated a specific **cost lever**: PySpark's spot/autoscaling choices (Day 19),
Kafka's cluster sizing and managed-vs-self-hosted decision (Days 15, 20), Redis's
licensing risk (Day 20), and ClickHouse's TCO model (today) are all instances of
the same underlying discipline — quantify the cost trade-off explicitly, rather
than defaulting to whichever option is more familiar or has better name
recognition.

**Build-vs-buy** is the recurring meta-decision underlying nearly every one of
this week's individual comparisons: self-hosted Kafka vs. Confluent Cloud/MSK,
self-hosted ClickHouse vs. BigQuery, self-managed Spark vs. Databricks — each a
specific instance of the same general question, best answered by the same
disciplined method (Day 20's PySpark and ClickHouse lessons): honestly compare
total cost including operational labor, not just the visible line-item.

## 3. How It Really Works (Internals)

The genuinely useful FinOps discipline isn't a one-time cost calculation — it's
building **cost visibility into ongoing operations**, the same way Week 3's
monitoring lessons (Day 17) built operational visibility into performance and
health. A target architecture's cost levers should be **continuously monitored**,
not calculated once at design time and forgotten — query patterns drift (Week 1
Day 4, Week 2 Day 9's fan-out risk), data volume grows (Day 15's capacity-planning
lessons), and a cost model built today can silently become wrong within months
without ongoing attention.

## 4. Architecture & Design Pattern Spotlight

**Pattern: total-cost framing as a first-class design input — the unifying theme
connecting every system-specific cost lesson this week (PySpark's managed/self-
hosted TCO, Kafka's alternatives, Redis's licensing risk, ClickHouse's live POC
model) into one coherent architectural discipline.** This week has been a running
theme given your actual migration decision — today's Architecture lesson is where
that theme gets named and generalized explicitly, turning a set of individual
system comparisons into a repeatable method you can apply to *any* future
build-vs-buy decision, not just this one.

## 5. Hands-On Lab

Write down the **3 biggest cost levers** in your target BigQuery→ClickHouse
architecture, ranked by actual dollar impact (using real numbers from today's
ClickHouse lesson wherever possible, not guesses):
1. For each lever, state explicitly whether it's a **genuine architectural cost
   difference** (the engine itself is more/less expensive for your pattern) or a
   **fixable inefficiency** (a query pattern, a sizing decision, an operational
   practice) that could be addressed independent of the migration decision.
2. For each lever, name the specific monitoring or review practice (from this
   week's lessons) that would catch this lever silently drifting unfavorable over
   time — e.g., "recheck actual bytes-scanned-per-query monthly" or "recheck
   ClickHouse operational labor hours quarterly."

This ranked list, with its architectural-vs-fixable distinction, is a genuinely
useful artifact to bring into your stakeholder conversation directly.

## 6. Real-World Product Comparison

- **Netflix and other large-scale cloud-native organizations** run dedicated
  FinOps functions specifically because cost, at scale, requires the same
  continuous-monitoring discipline as performance or security — a one-time
  cost review is treated as insufficient on its own, the same principle as
  today's lab.
- The **FinOps Foundation** (an industry body) formalizes exactly this
  "cost as an ongoing, cross-functional practice" discipline — worth knowing the
  term exists as a broader professional practice area beyond this specific
  migration decision.

## 7. Common Production Pitfalls

- Treating a cost/TCO analysis as a one-time gate to pass before a decision,
  rather than an ongoing practice — the same pitfall as building a monitoring
  dashboard and never looking at it again after initial setup.
- Conflating "this alternative is more expensive" with "our current usage of this
  alternative is inefficient" — exactly the distinction Day 20's ClickHouse
  lesson's three-way comparison exists to avoid.
- Making a build-vs-buy decision based on a single point-in-time comparison
  without considering how the comparison changes as scale grows — a decision
  correct today at current volume may not remain correct at 5x volume.

## 8. Review Questions
1. Why should cost be treated as a first-class architectural input rather than an
   afterthought?
2. Why does a cost model need ongoing monitoring, not just a one-time
   calculation?
3. Why is separating "architectural cost difference" from "fixable inefficiency"
   the key analytical move across nearly every comparison this week?
4. What are your own top 3 ranked cost levers, and which are architectural vs.
   fixable?

## 9. Proficiency Checkpoint
If you've produced a ranked, honestly-categorized list of your real architecture's
biggest cost levers with a monitoring plan for each, you're at Level 4 — a
genuinely boardroom-ready artifact synthesizing this entire week's work.

## Next
Day 21 is this week's integrated lab and review — turning this week's individual
artifacts (incident postmortems, cost models, security maps) into final,
polished deliverables.
