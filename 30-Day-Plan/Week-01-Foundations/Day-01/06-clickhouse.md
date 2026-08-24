# Day 1: ClickHouse — Columnar OLAP Foundations

## Time: ~25 min | Track proficiency target for this day: Level 2
*(Given your live POC, expect to move through Week 1 on this track faster than the
others — treat these first few days as formalizing intuition you've already built.)*

## 1. Learning Objective
Explain columnar storage well enough to predict which queries it accelerates (and
which it doesn't help), and create a first `MergeTree` table with a sensible primary
key.

## 2. Core Concept (basics → advanced)

**OLTP vs. OLAP, mechanically.** A row-store (Postgres, MySQL) keeps all columns of one
row physically together — great for "fetch/update this one order," bad for "average
the `amount` column across 500M orders," because you must read every column of every
row just to touch one column. A **column-store** (ClickHouse) keeps each column
physically separate on disk — "average this one column across 500M rows" only reads
that column's bytes, often with a much smaller footprint due to compression on
similarly-typed, similarly-valued data sitting next to each other.

```
Row-store layout (Postgres):                 Column-store layout (ClickHouse):
[order_id, customer, amount, ts]             order_id:  [1, 2, 3, 4, ...]
[1, "alice", 99.99, ...]                     customer:  ["alice", "bob", ...]
[2, "bob", 49.99, ...]                       amount:    [99.99, 49.99, ...]
[3, "carol", 199.99, ...]                    ts:        [...]

SELECT AVG(amount) FROM orders               SELECT AVG(amount) FROM orders
→ must read every column of every row        → reads only the `amount` column
```

**A first table:**
```sql
CREATE TABLE events (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    amount Float64
)
ENGINE = MergeTree
ORDER BY (event_type, event_time);
```

`MergeTree` is the foundational table engine family (Day 2 covers its variants). The
`ORDER BY` clause is not just a sort hint — it defines the **physical sort order on
disk**, which is also what the primary index is built from (Day 3 goes deep on this).

## 3. How It Really Works (Internals)

ClickHouse's query engine is **vectorized**: instead of processing one row at a time
through the expression tree (the traditional "Volcano model" used by many row-stores),
it processes a **batch of values from one column** at a time through each operation,
taking advantage of CPU SIMD instructions and dramatically better cache locality. This
single design choice explains a large share of ClickHouse's raw scan speed compared to
row-at-a-time engines, independent of columnar storage itself.

```
Row-at-a-time (Volcano model):        Vectorized (ClickHouse):
for each row:                          for each column-batch (e.g. 4096 values):
    apply filter                            apply filter to the whole batch at once
    apply expression                        apply expression to the whole batch at once
    → next row                              → next batch
```

Data is physically organized into **parts** — each insert creates a new part (a
self-contained directory of column files), and a background **merge** process combines
smaller parts into larger ones over time. If this sounds like Elasticsearch's segments
or an LSM-tree, that's exactly right — same family of design, different domain.

## 4. Architecture & Design Pattern Spotlight

**Pattern: columnar storage + vectorized execution**, the two independent-but-
complementary ideas that define modern OLAP engines (BigQuery, Snowflake, Druid, and
ClickHouse all share this pair, with different trade-offs in how they're implemented
and operated). Recognizing these as two separate ideas — not one — will help you reason
about why, say, a row-store with columnar *extensions* still isn't the same thing.

## 5. Hands-On Lab
```bash
docker run -d --name clickhouse -p 8123:8123 -p 9000:9000 clickhouse/clickhouse-server
```
```sql
-- via clickhouse-client or the HTTP interface on 8123
CREATE TABLE events (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    amount Float64
) ENGINE = MergeTree ORDER BY (event_type, event_time);

INSERT INTO events VALUES
    ('2026-08-01 10:00:00', 1, 'purchase', 49.99),
    ('2026-08-01 10:05:00', 2, 'purchase', 99.99),
    ('2026-08-01 10:10:00', 1, 'refund', -49.99);

SELECT event_type, count(), sum(amount) FROM events GROUP BY event_type;
```
Compare the mental model to a BigQuery scheduled query you already know from work —
same aggregation shape, very different engine underneath.

## 6. Real-World Product Comparison

- **Cloudflare** runs one of the largest known ClickHouse deployments, powering
  real-time HTTP traffic analytics across a massive, high-cardinality dataset —
  effectively the workload class your MDO portal dashboards belong to.
- **Uber and eBay** both use ClickHouse for large-scale internal analytics where
  query latency and cost-per-query at high query volume matter more than the
  flexibility of a general-purpose warehouse.
- Contrast with **BigQuery**: serverless, pay-per-byte-scanned, zero ops — excellent
  for ad hoc analyst queries and unpredictable workloads, but costs scale directly with
  bytes scanned, which is exactly the tension your cost-reduction POC is testing.
  ClickHouse trades "someone else runs it" for "you control cost via
  hardware/architecture," at the price of operational responsibility (the exact 3-node
  Keeper+HAProxy cluster you're already running).

## 7. Common Production Pitfalls
- Choosing an `ORDER BY` key that doesn't match your actual query filters — since it
  defines the physical sort and primary index, a mismatched key means ClickHouse can't
  skip data efficiently, and you lose most of the performance advantage (Day 3 goes
  deep here).
- Expecting `MergeTree` to behave like a transactional table for frequent
  updates/deletes — mutations exist but are heavyweight background operations, not
  cheap in-place row updates.
- Treating JOINs the same way you would in Postgres/BigQuery — this is your current
  real issue, and gets a dedicated deep-dive on Day 9 of Week 2.

## 8. Review Questions
1. Concretely, why does a columnar layout speed up `AVG(amount)` but not help (or even
   hurt) `SELECT * WHERE order_id = 42`?
2. What does vectorized execution mean, separate from "columnar storage"?
3. What does `ORDER BY` actually control in a MergeTree table, beyond sort order?
4. Name one workload ClickHouse is a poor fit for.

## 9. Proficiency Checkpoint
If you can explain columnar storage and vectorized execution as two separate ideas, and
justify a table's `ORDER BY` choice by its expected query patterns, you're at Level 2 —
likely already partway to Level 3 given your live cluster experience.

## Next
Day 2 covers the `MergeTree` engine family in depth — when to reach for
`ReplacingMergeTree`, `SummingMergeTree`, `AggregatingMergeTree`, or
`CollapsingMergeTree` instead of plain `MergeTree`.
