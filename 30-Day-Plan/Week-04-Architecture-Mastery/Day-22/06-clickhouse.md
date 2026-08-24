# Day 22: ClickHouse — Design Patterns: OBT vs. Star Schema for Serving

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Compare a "one big table" (OBT) design against a star-schema design for one of
your real dashboards, and make a reasoned recommendation.

## 2. Core Concept (basics → advanced)

Two competing serving-layer schema philosophies for OLAP:

- **One Big Table (OBT)**: aggressively denormalize — pre-join all relevant
  dimension attributes directly into the fact table at ETL time, so queries never
  need a runtime `JOIN` at all. This is ClickHouse's culturally preferred
  approach (Week 2, Day 9's fan-out lesson noted this denormalize-first culture
  explicitly) — it sidesteps join-related costs and correctness risks (fan-out)
  entirely, at the cost of data duplication (the same dimension attribute repeated
  across every fact row) and less flexibility if dimension attributes change
  (requiring a full table rewrite/backfill rather than a small dimension-table
  update).
- **Star schema**: a central fact table joined at query time to smaller dimension
  tables — more storage-efficient (dimension data stored once) and easier to
  update (change a dimension table's row once, every fact referencing it
  reflects the change immediately), at the cost of needing runtime joins (with
  the fan-out risk from Week 2, Day 9 to actively guard against).

```
OBT:            fact_row: {event_id, org_id, org_name, org_tier, event_time, amount}
                (org_name/org_tier DUPLICATED across every row for that org —
                 no JOIN needed at query time, but a LOT of repeated data)

Star schema:    fact_row: {event_id, org_id, event_time, amount}
                dim_org:  {org_id, org_name, org_tier}
                (JOIN needed at query time — less storage, easier dimension
                 updates, but real fan-out risk if cardinality isn't verified)
```

## 3. How It Really Works (Internals)

The right choice genuinely depends on your actual dimension **update frequency**
and **cardinality**: dimensions that rarely change and have low cardinality
(a small, stable list of organizations) are cheap to denormalize into OBT with
minimal storage waste and no update-flexibility cost worth worrying about.
Dimensions that change frequently, or have very high cardinality, make OBT's
"rewrite everything on a dimension change" cost much more painful, favoring star
schema (or, as a middle path, ClickHouse **dictionaries**, Week 2 Day 11 — which
give you star-schema-like separate dimension storage with OBT-like fan-out
immunity and near-zero query-time join cost, genuinely the best of both for
dimensions that fit the dictionary lookup shape).

## 4. Architecture & Design Pattern Spotlight

**Pattern: serving-layer design for OLAP — a genuine, non-obvious trade-off
between storage/join-avoidance (OBT) and normalization/update-flexibility (star
schema), with dictionaries (Week 2, Day 11) often the pragmatic middle path for
genuinely lookup-shaped dimensions.** This is directly, concretely relevant to
your own MDO portal schema decisions — not an abstract data-warehousing debate.

## 5. Hands-On Lab

Pick one real MDO portal dashboard and design both an OBT and a star-schema
version of its underlying table(s). For each, estimate: relative storage cost
(how much duplication does OBT actually introduce for this specific data's
cardinality), update cost (how often do the relevant dimensions actually change,
and what would updating them require under each design), and query-time cost/risk
(does the star-schema version need careful fan-out-cardinality verification per
Week 2, Day 9?). Make an explicit recommendation with your reasoning stated, and
consider whether a dictionary-based approach beats both pure options for this
specific case.

## 6. Real-World Product Comparison

- **Uber and eBay's** ClickHouse deployments (referenced earlier this month)
  both use OBT-style denormalization heavily for their highest-query-volume
  dashboards specifically to eliminate join cost and fan-out risk at query time,
  accepting the storage/update-flexibility trade-off deliberately.
- **BigQuery** users often maintain star-schema-like normalized tables (closer to
  traditional warehouse practice) since BigQuery's cost model and query
  optimizer handle joins differently than ClickHouse's culture assumes — worth
  noting your migration may need to actively *change* schema philosophy, not just
  port existing BigQuery schemas as-is.

## 7. Common Production Pitfalls

- Porting a BigQuery star-schema design directly into ClickHouse without
  reconsidering whether OBT or dictionaries would better fit ClickHouse's actual
  execution model — a common, easy-to-miss migration mistake.
- Choosing OBT for a dimension that actually changes frequently, incurring
  repeated, expensive full-table rewrites that a star-schema or dictionary
  approach would have avoided.
- Not verifying join cardinality (Week 2, Day 9) when choosing star schema,
  reintroducing the exact fan-out risk this month's earlier lessons addressed.

## 8. Review Questions
1. What determines whether OBT or star schema is the better fit for a specific
   dimension?
2. Why do dictionaries often represent a genuine middle path between the two?
3. Why might a direct BigQuery-to-ClickHouse schema port be the wrong approach?
4. What's your own real dashboard's recommended design, and why?

## 9. Proficiency Checkpoint
If you can make a reasoned OBT-vs-star-schema-vs-dictionary recommendation for a
real dashboard with actual cardinality/update-frequency reasoning, you're at
Level 4 — directly applicable to your migration's schema design work.

## Next
Day 23 covers ClickHouse case studies — Cloudflare, Uber, eBay.
