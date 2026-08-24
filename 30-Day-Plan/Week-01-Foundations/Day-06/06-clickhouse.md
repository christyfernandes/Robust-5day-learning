# Day 6: ClickHouse — Materialized Views (Normal vs. Refreshable)

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Build a Refreshable Materialized View that mirrors one of your own real BigQuery
scheduled queries, and explain the difference between incremental and periodic-recompute
view maintenance.

## 2. Core Concept (basics → advanced)

ClickHouse has two genuinely different kinds of Materialized View, easy to conflate but
solving different problems:

- **Normal Materialized View**: attached to a source table as a **trigger** — every
  time a new block of rows is inserted into the source table, the MV's query runs
  *only against that new block* (not the whole table), and the result is appended to the
  MV's own target table. This is **incremental**, but only in the narrow sense of
  "processes new inserts as they arrive" — it cannot express queries needing a full
  table scan or a join against the complete dataset each time, since it only ever sees
  the incoming block.
- **Refreshable Materialized View**: runs its *entire* query against the *entire*
  underlying data on a schedule (e.g., every 5 minutes), fully replacing its target
  table's contents each time — conceptually much closer to a **BigQuery scheduled
  query** or a dbt scheduled model than to the "trigger on insert" normal MV.

```
Normal MV:            INSERT (new block) ──▶ MV's query runs on JUST this block ──▶ appended to target
                       (efficient, but query must be expressible incrementally,
                        block-by-block, with no dependency on the full existing dataset)

Refreshable MV:        [scheduled interval] ──▶ MV's query runs against the FULL dataset ──▶ 
                                                  fully replaces target table contents
                       (matches BigQuery scheduled query semantics almost exactly)
```

## 3. How It Really Works (Internals)

The reason normal MVs are block-scoped rather than query-scoped is architectural: a
normal MV is implemented as an insert trigger, and re-running an arbitrary query against
the *entire* table on every single insert would be prohibitively expensive at any real
insert rate. This means a normal MV works well for simple, associative rollups (a
running `SUM`/`COUNT`/`AVG` via `AggregatingMergeTree` — Day 2's MergeTree variants) but
cannot correctly express, say, "top 10 products this month" (a query needing the whole
month's data, re-evaluated, not just the newest block).

**Refreshable MVs** solve exactly this gap by giving up "instant, per-insert" freshness
in exchange for "arbitrary query, correctly re-evaluated periodically" — which is
precisely the shape of a BigQuery scheduled query (run a full query on a cron schedule,
materialize the result) and therefore the natural ClickHouse target for migrating your
actual BigQuery scheduled-query workload.

## 4. Architecture & Design Pattern Spotlight

**Pattern: incremental view maintenance (normal MV) vs. periodic full recompute
(Refreshable MV) — the same trade-off Day 1's ClickHouse MergeTree-variant lesson
touched on (merge-time vs. insert-time), applied one layer up at the view level.**
Recognizing which category a given BigQuery scheduled query falls into (simple
associative rollup vs. genuinely needs the whole dataset re-evaluated) is the exact
judgment call this week's stakeholder-facing migration task requires.

## 5. Hands-On Lab

```sql
-- pick one of your actual BigQuery scheduled queries — say, a daily
-- "top orgs by event volume" report — and mirror it:

CREATE MATERIALIZED VIEW top_orgs_daily
REFRESH EVERY 1 DAY
ENGINE = MergeTree ORDER BY event_date
AS
SELECT
    toDate(event_time) AS event_date,
    org_id,
    count() AS event_count
FROM events
GROUP BY event_date, org_id
ORDER BY event_count DESC
LIMIT 100;
```
Check `system.view_refreshes` to confirm the schedule and see the last/next refresh
time. Manually trigger one with `SYSTEM REFRESH VIEW top_orgs_daily`, and compare its
output + execution time against how long the equivalent BigQuery scheduled query
actually takes today — this comparison is a real deliverable for this week's work.

## 6. Real-World Product Comparison

- This is a direct, close mapping to **BigQuery scheduled queries** — same underlying
  idea (periodic full re-evaluation, materialized), different execution engine and
  cost model (per-byte-scanned vs. self-hosted compute).
- **Snowflake's dynamic tables** solve a similar problem with a target-lag-based
  refresh model (declare acceptable staleness, let Snowflake decide refresh cadence)
  rather than ClickHouse's explicit `REFRESH EVERY` schedule — a different knob for a
  similar goal.

## 7. Common Production Pitfalls

- Trying to force a genuinely full-recompute query (e.g., anything with `GROUP BY`
  across the whole table, window functions over history, or a self-join) into a normal
  MV — it will either fail or silently produce wrong results, since it only ever sees
  the newest inserted block.
- Setting a Refreshable MV's schedule far more frequent than the underlying query
  actually needs — each refresh re-scans the full source data, so cost scales with
  refresh frequency × query cost, not just query cost.
- Not accounting for the gap between "data inserted" and "next scheduled refresh" when
  a downstream consumer expects fresher data than the MV's schedule actually provides.

## 8. Review Questions
1. Why can't a normal Materialized View correctly express "top 10 products this month"?
2. What's the precise architectural reason normal MVs are limited to block-scoped
   queries?
3. How does a Refreshable MV's semantics map onto a BigQuery scheduled query?
4. What's the cost trade-off of setting a Refreshable MV's schedule too frequent?

## 9. Proficiency Checkpoint
If you can correctly classify a given BigQuery scheduled query as "normal-MV-shaped" or
"Refreshable-MV-shaped," and build the Refreshable MV version, you're at a genuine
Level 3 on this specific, immediately job-relevant skill.

## Next
Day 7 combines this week's concepts into one lab session, including your first ADR.
