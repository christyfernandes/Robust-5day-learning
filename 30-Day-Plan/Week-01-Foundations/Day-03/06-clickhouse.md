# Day 3: ClickHouse — Primary Key & Sparse Index

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain why ClickHouse's primary key index is sparse rather than a classic B-tree, and
choose an `ORDER BY` key that actually speeds up your real queries.

## 2. Core Concept (basics → advanced)

In Postgres/MySQL, a B-tree index maps (roughly) one index entry per row, letting you
jump directly to a specific row. ClickHouse does something deliberately coarser: data is
physically stored sorted by the table's `ORDER BY` key (which doubles as its primary
key), split into fixed-size chunks called **granules** (default 8,192 rows), and the
**sparse primary index** stores only *one entry per granule* — the value of the first
row in that granule.

```
B-tree (Postgres):  one index entry PER ROW → precise row lookup, more index storage

ClickHouse sparse index: one entry PER GRANULE (e.g., every 8192 rows)

  Granule 0: rows 1-8192,     index entry → first row's ORDER BY value
  Granule 1: rows 8193-16384, index entry → first row's ORDER BY value
  Granule 2: rows 16385-...,  index entry → first row's ORDER BY value

Query for ORDER BY value X → binary search the sparse index → find the ONE granule
that could contain X → scan just that granule (8192 rows), not the whole table.
```

This trades exact-row precision for a dramatically smaller, cheaply-cached index — and
it's the right trade for ClickHouse's actual workload: analytical queries scanning
millions/billions of rows, where "narrow it down to the right few-thousand-row granule"
is just as effective as row-exact lookup, at a fraction of the index size and
maintenance cost.

## 3. How It Really Works (Internals)

The critical operational consequence: **the `ORDER BY` key determines which queries can
skip data, and which can't.** A query filtering on a column that's a *prefix* of the
`ORDER BY` key can use the sparse index to skip entire granules. A query filtering on a
column that's *not* in the `ORDER BY` key (or not a prefix of it) forces a full-column
scan across every granule — because the sparse index gives you no information about
where that column's values are physically located.

```sql
-- table: ORDER BY (org_id, event_time)

SELECT ... WHERE org_id = 42                          -- ✅ can skip granules (prefix match)
SELECT ... WHERE org_id = 42 AND event_time > '2026-01-01'  -- ✅ can skip granules (full prefix)
SELECT ... WHERE event_time > '2026-01-01'            -- ❌ event_time is NOT a prefix
                                                       --    (org_id comes first) — full scan
```
This is why `ORDER BY` selection is arguably the single highest-leverage design decision
in a ClickHouse schema — get it wrong, and every query on the "wrong" column pays for a
full table scan regardless of how much RAM or how many cores you throw at it.

## 4. Architecture & Design Pattern Spotlight

**Pattern: sparse index + granule scanning.** This is the same underlying idea (accept a
coarser index for a massively smaller footprint) as an LSM-tree's block index in
Cassandra/RocksDB, or a data lake's partition-pruning + column statistics (min/max per
row-group) in Parquet — "skip whole chunks using cheap coarse metadata" is a recurring
pattern across every large-scale storage engine you'll study this month.

## 5. Hands-On Lab

```sql
CREATE TABLE events_bad (
    event_time DateTime,
    org_id UInt32,
    event_type String
) ENGINE = MergeTree()
ORDER BY event_time;     -- org_id is NOT a prefix

CREATE TABLE events_good (
    event_time DateTime,
    org_id UInt32,
    event_type String
) ENGINE = MergeTree()
ORDER BY (org_id, event_time);   -- org_id IS a prefix

-- insert the same ~5M synthetic rows into both, then compare:
SELECT count() FROM events_bad  WHERE org_id = 42;
SELECT count() FROM events_good WHERE org_id = 42;
```
Run both with `EXPLAIN indexes = 1` prefixed, and compare how many granules each query
actually reads (`rows_read` in the query log) — this is the sparse index doing its job,
made visible.

## 6. Real-World Product Comparison

- **Postgres's B-tree** philosophy optimizes for "find this one row fast" (OLTP);
  ClickHouse's sparse index optimizes for "skip 99% of the table fast" (OLAP) — different
  index philosophies for genuinely different query shapes, not one being objectively better.
- **BigQuery** has no traditional index at all — it relies entirely on partition pruning
  (usually by date) and per-column min/max block statistics for pruning, conceptually
  similar to ClickHouse's granule skipping but automatic rather than a schema decision
  you make explicitly via `ORDER BY`.

## 7. Common Production Pitfalls

- Choosing `ORDER BY` based on "what's the most unique column" instead of "what will
  every query actually filter on" — cardinality is a secondary concern to filter-prefix
  match.
- Adding columns to `ORDER BY` "just in case" — every additional key column costs
  compression efficiency (data is less locally sorted on any single column) for a
  benefit you may never use.
- Forgetting that changing `ORDER BY` on an existing table requires recreating it (via
  `ALTER TABLE ... MODIFY ORDER BY` has real limitations) — this is a decision that's
  expensive to reverse, unlike adding a Postgres index after the fact.

## 8. Review Questions
1. Why is one sparse index entry per granule enough to make range queries fast?
2. What makes a `WHERE` clause "prefix-eligible" for the sparse index?
3. Why does query performance degrade to a full scan when filtering on a non-prefix
   column, regardless of hardware?
4. Why is `ORDER BY` choice higher-stakes in ClickHouse than adding an index in Postgres?

## 9. Proficiency Checkpoint
If you can look at a table's `ORDER BY` and a candidate query and correctly predict
"granule skip" vs. "full scan" before running it, you're at Level 2 and ready for
distributed sharding (Day 4).

## Next
Day 4 moves from single-node indexing to distributed tables and sharding key selection —
the same "which column decides locality" question, at cluster scale.
