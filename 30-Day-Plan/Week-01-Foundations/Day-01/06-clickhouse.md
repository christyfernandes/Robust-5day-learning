# Day 1: ClickHouse — Columnar OLAP Foundations

## Time: ~30 min | Track proficiency target for this day: Level 2
*(Given your live POC, expect to move through Week 1 on this track faster than the
others — treat these first few days as formalizing intuition you've already built.)*

## 1. Learning Objective
Explain columnar storage well enough to predict which queries it accelerates (and
which it doesn't help), and create a first `MergeTree` table with a sensible primary
key.

## 2. Core Concept (basics → advanced)

**Start here if ClickHouse is genuinely new to you.** ClickHouse is a database
purpose-built for **analytical** queries — questions like "what's the average order
value this month, broken down by region" over potentially billions of rows — rather
than for quickly reading or updating one specific row at a time the way a typical
application database does. This distinction (analytical vs. transactional workloads)
is important enough that it has standard names, worth knowing: **OLAP** (Online
Analytical Processing — ClickHouse's world) vs. **OLTP** (Online Transactional
Processing — Postgres/MySQL's world).

**OLTP vs. OLAP, mechanically.** A row-store (Postgres, MySQL) keeps all columns of one
row physically together on disk — great for "fetch/update this one order" (read one
small chunk, get every column of it in one place), bad for "average the `amount`
column across 500M orders," because to read just that one column you still have to
physically read through every *other* column of every row too, since they're all
interleaved together on disk. A **column-store** (ClickHouse) keeps each column
physically separate on disk — "average this one column across 500M rows" only reads
that column's bytes, often with a much smaller footprint due to compression on
similarly-typed, similarly-valued data sitting next to each other (e.g., a column of
timestamps that increase steadily compresses far better sitting next to other similar
timestamps than it would interleaved with unrelated string and float columns).

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

`MergeTree` is the foundational table engine family (Day 2 covers its variants) — think
of "engine" here as ClickHouse's term for "which specific storage/indexing strategy
this table uses," a concept most row-stores don't expose to you at all, since they
generally only offer one. The `ORDER BY` clause is not just a sort hint the way it
would be at the end of a `SELECT` — here, on a `CREATE TABLE`, it defines the
**physical sort order the data is actually stored in on disk**, which is also what the
primary index is built from (Day 3 goes deep on this).

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

### Sample Output

`clickhouse-client`'s default pretty-printed table format for that final query:

```
┌─event_type─┬─count()─┬─sum(amount)─┐
│ purchase   │       2 │      149.98 │
│ refund     │       1 │      -49.99 │
└────────────┴─────────┴─────────────┘

2 rows in set. Elapsed: 0.003 sec.
```

Reading this piece by piece:
- **Two output rows**, one per distinct `event_type` — exactly what `GROUP BY
  event_type` promises: one summarized row per distinct group, not one row per input
  row (there were 3 input rows, but only 2 distinct `event_type` values).
- **`count()` is 2 for `purchase`** — it counted the two purchase rows you inserted
  (49.99 and 99.99), and **1 for `refund`** — just the single refund row. This is the
  count of *input rows that fell into each group*, not a running total of anything.
- **`sum(amount)` for `purchase` is `149.98`** — that's `49.99 + 99.99`, added
  correctly. **`sum(amount)` for `refund` is `-49.99`** — the refund's negative amount
  passed through the sum exactly as stored, which is worth noticing: ClickHouse (like
  most databases) doesn't "know" a negative number means "refund" semantically — it's
  just summing whatever numeric value is in that column, so if your data modeling
  intends refunds to *subtract* from a purchase total elsewhere, that has to be
  designed into the query, not assumed from the column's sign alone.
- **Column widths in the table auto-size to fit the widest value in that column**
  (including the header) — this is purely a terminal-formatting detail, not a fact
  about the data, but it's worth recognizing so you're not confused when column widths
  differ between two different query outputs.
- **`2 rows in set. Elapsed: 0.003 sec.`** — the footer always tells you exactly how
  many rows came back and how long the query took server-side; for a toy 3-row table
  this is meaningless (a few milliseconds either way), but this exact footer is what
  you'll actually watch closely once you're running this against your real,
  billion-row production tables later this month.

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
<details><summary>Show answer</summary>

`AVG(amount)` only ever needs one column's values — a columnar layout lets ClickHouse
read exactly (and only) that column's bytes off disk, skipping every other column
entirely. `SELECT * WHERE order_id = 42` needs *every* column for the one matching row
— with data split across separate column files, fetching "everything about one row"
now means opening and reading from every column file just to reassemble that single
row, which is strictly more scattered I/O than a row-store (where all of that row's
data already sits together in one place). This is exactly why columnar engines are a
poor fit for row-lookup-heavy (OLTP-style) workloads.

</details>

2. What does vectorized execution mean, separate from "columnar storage"?
<details><summary>Show answer</summary>

Columnar storage is about how data sits on disk (grouped by column, not by row).
Vectorized execution is about how the query engine *processes* data once it's been
read — operating on a batch of many values from one column at once (e.g., 4096 values
at a time) rather than looping through one row at a time. You could, in principle,
have columnar storage with a row-at-a-time execution engine (slower than it needs to
be) — ClickHouse specifically combines both, which is why the two ideas are worth
holding separately rather than treating "columnar" as a single all-in-one concept.

</details>

3. What does `ORDER BY` actually control in a MergeTree table, beyond sort order?
<details><summary>Show answer</summary>

It defines the actual physical order data is written to disk in, and that physical
order is what the table's primary index (a sparse index, covered Day 3) is built
from. This makes `ORDER BY` a storage-layout decision, not just a display/sort
preference the way it would be at the end of a normal `SELECT` — choosing it well (or
poorly) directly determines whether future queries filtering on those columns can
skip large chunks of data efficiently or have to scan everything.

</details>

4. Name one workload ClickHouse is a poor fit for.
<details><summary>Show answer</summary>

High-frequency point lookups by primary key (e.g., "fetch this one user's profile by
ID, thousands of times per second") — exactly the OLTP-shaped access pattern
described in question 1's answer. A proper key-value store (Redis) or OLTP database
(Postgres) fits that pattern far better than a columnar engine built around scanning
and aggregating large volumes.

</details>

## 9. Proficiency Checkpoint

**Quick Recap:**
- **OLTP** (Postgres/MySQL): optimized for reading/updating individual rows fast.
  **OLAP** (ClickHouse): optimized for scanning and aggregating huge volumes of a few
  columns at a time.
- **Row-store**: one row's columns stored together — fast row lookup, slow single-
  column scans across many rows. **Column-store**: each column stored separately —
  fast single-column scans, slower full-row lookups.
- **Columnar storage** (where data sits) and **vectorized execution** (how it's
  processed, in batches per column) are two separate, complementary design choices —
  not one idea.
- **`ORDER BY` on `CREATE TABLE`** = the actual physical on-disk sort order, and the
  basis of the primary index — a storage decision, not a display preference.
- **Parts**: each insert creates a new immutable part; a background merge process
  combines them over time — same design family as Elasticsearch segments / an
  LSM-tree.

If you can explain columnar storage and vectorized execution as two separate ideas, and
justify a table's `ORDER BY` choice by its expected query patterns, you're at Level 2 —
likely already partway to Level 3 given your live cluster experience.

## Next
Day 2 covers the `MergeTree` engine family in depth — when to reach for
`ReplacingMergeTree`, `SummingMergeTree`, `AggregatingMergeTree`, or
`CollapsingMergeTree` instead of plain `MergeTree`.
