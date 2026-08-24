# Day 22: Flink — Design Patterns: Kappa Architecture & Stateful Functions

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Redraw your Lambda-ish current setup as a Kappa alternative, and identify
specifically what you'd drop.

## 2. Core Concept (basics → advanced)

Week 2, Day 11 introduced Kappa architecture conceptually — today's lab makes it
concrete against your own real pipeline. In a **Kappa** design, Flink is the
**sole** processing layer: no separate batch codepath at all (Week 2, Day 11's
Lambda-duplication cost) — all processing, including what would traditionally be
"batch" work, flows through the same streaming pipeline, with historical
reprocessing achieved by replaying the log (Kafka's retention/compaction, Week 2
Day 10) through that same pipeline.

**Stateful Functions** (Statefun) extends Flink beyond the DataStream/Table API
model into a more general **actor-like** programming model — individual stateful
"functions" (conceptually similar to actors) communicate via messages, each
maintaining its own state, useful for modeling business entities with complex,
long-lived state and interaction patterns (e.g., a single user's or order's
lifecycle) that don't map naturally onto DataStream's window/aggregate-oriented
API.

## 3. How It Really Works (Internals)

The concrete question Kappa forces you to answer for your own pipeline: which of
your current batch (PySpark) computations could genuinely be re-expressed as a
Flink streaming job, and which genuinely need batch semantics (a large, one-time
historical recomputation that doesn't fit a continuous streaming model well)? This
isn't a purely theoretical question — Week 2, Day 11's **Kappa+** pragmatic hybrid
exists precisely because this honest assessment, for most real pipelines, finds at
least *some* computations that genuinely don't translate cleanly to streaming,
making pure Kappa aspirational rather than immediately achievable for most
organizations.

## 4. Architecture & Design Pattern Spotlight

**Pattern: stream-only architecture — eliminating Lambda's dual-codepath
maintenance cost, at the cost of requiring your streaming engine to handle
everything, including what used to be "batch-shaped" work.** This is the direct,
concrete application of Week 2 Day 11's Lambda/Kappa framework to your own actual
architecture, rather than an abstract comparison.

## 5. Hands-On Lab

Redraw your current pipeline (whatever mix of PySpark batch jobs and Flink
streaming jobs you actually run) as a pure Kappa alternative. For each current
batch job, answer explicitly: could this become a Flink streaming job
(continuous, incremental), or does it genuinely require batch semantics (a
large historical recompute better suited to Spark)? Which specific components
would you drop entirely in this redesign, and which would need to move from
PySpark to Flink?

## 6. Real-World Product Comparison

- **LinkedIn** has publicly discussed moving significant portions of its
  pipeline toward Kappa-style architectures over time, specifically to eliminate
  Lambda's duplication cost — but even LinkedIn's own public accounts acknowledge
  retaining some batch processing for specific use cases, a real-world Kappa+
  example.
- **Stateful Functions** is used at companies with genuinely complex,
  long-lived entity state (e.g., modeling an individual customer's or order's
  full lifecycle) where DataStream's window-oriented model would be an awkward fit.

## 7. Common Production Pitfalls

- Attempting a "pure Kappa" migration dogmatically, forcing genuinely
  batch-shaped computations into a streaming model at significant engineering
  cost for no real benefit.
- Choosing Stateful Functions for problems that DataStream's standard keyed-state
  model (Week 1, Day 5) already handles well — an unnecessary complexity increase.
- Not honestly assessing which parts of your own pipeline are genuinely
  streaming-shaped versus genuinely batch-shaped before committing to a Kappa
  redesign.

## 8. Review Questions
1. What does Kappa architecture eliminate that Lambda requires?
2. Why is "pure Kappa" often aspirational rather than immediately achievable for
   real pipelines?
3. When would Stateful Functions be a better fit than the standard DataStream API?
4. Which parts of your own real pipeline would and wouldn't translate cleanly to
   Kappa?

## 9. Proficiency Checkpoint
If you can honestly redesign your own pipeline as Kappa/Kappa+ and justify each
retained batch component, you're at Level 4.

## Next
Day 23 covers Flink case studies — Alibaba, Uber, Stripe.
