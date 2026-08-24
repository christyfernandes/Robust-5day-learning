# Day 23: ClickHouse — Case Studies: Cloudflare, Uber, eBay

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Extract one concrete takeaway from Cloudflare's, Uber's, and eBay's public
ClickHouse usage — with particular attention to Cloudflare's analytics scale.

## 2. Core Concept (basics → advanced)

- **Cloudflare**: one of the most-cited large-scale ClickHouse deployments
  publicly documented, used for network/traffic analytics at enormous
  ingestion volume — their public engineering accounts discuss sharding-key
  design (Week 1, Day 4), codec/compression choices (Week 2, Day 12), and
  cluster-scaling decisions in concrete, quantified terms.
- **Uber**: uses ClickHouse for specific high-volume analytical workloads
  alongside their broader data platform — a useful case study in how
  ClickHouse fits *alongside* other systems (Kafka, Flink — Uber uses all
  three) rather than in isolation.
- **eBay**: has published on ClickHouse adoption for real-time analytics,
  including migration considerations directly comparable to your own
  BigQuery→ClickHouse decision.

## 3. How It Really Works (Internals)

Cloudflare's case is worth close attention specifically because their publicly
documented engineering decisions (sharding strategy, codec selection, storage
tiering) are exactly the categories of decision your own POC has been working
through this month — reading their reasoning for *why* they made specific
choices (not just what they chose) is a direct, applicable input to your own
migration's decision-making, from a team operating at a scale that stress-tests
these decisions far beyond what most deployments (including likely your own)
will ever need to handle.

## 4. Architecture & Design Pattern Spotlight

**Pattern: case-study literacy, applied to ClickHouse — with Cloudflare's
publicly documented decisions serving as a direct, concrete reference point
for your own migration's sharding, codec, and tiering choices.**

## 5. Hands-On Lab

Read Cloudflare's public engineering posts on their ClickHouse deployment
(their engineering blog has documented this extensively over time) alongside
one each from Uber and eBay. For Cloudflare specifically, identify: one
sharding-key or codec decision they made, and whether the same reasoning
(cardinality, query pattern, Week 1 Day 4 and Week 2 Day 12) applies to your own
schema decisions from Day 22's lab.

## 6. Real-World Product Comparison

This lesson *is* the comparison exercise — a direct input to your own migration
decisions.

## 7. Common Production Pitfalls

- Assuming Cloudflare-scale decisions transfer directly without adjusting for
  your own, likely much smaller, actual data volume and query pattern.
- Reading case studies for the specific technology choice without extracting
  the underlying *reasoning*, which is what's actually transferable.
- Not comparing eBay's migration considerations specifically against your own
  stated migration rationale — this is the single most directly comparable case
  study to your actual situation.

## 8. Review Questions
1. What sharding or codec decision did Cloudflare make, and does the same
   reasoning apply to your schema?
2. How does ClickHouse fit alongside Kafka and Flink in Uber's broader
   platform?
3. What migration considerations does eBay's case study share with your own
   situation?
4. What's the most directly transferable lesson from these three case studies
   to your own work?

## 9. Proficiency Checkpoint
If you can extract a specific, applicable lesson from Cloudflare's or eBay's
case study and apply it to your own migration decisions, you're at Level 4.

## Next
Day 24 covers when NOT to use ClickHouse — the necessary counterbalance to
today's case studies.
