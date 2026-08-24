# Day 2: ClickHouse — The MergeTree Engine Family

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Choose the correct `MergeTree` variant for a given data shape (append-only facts,
upserts, running sums, offsetting events) instead of defaulting to plain `MergeTree`
for everything.

## 2. Core Concept (basics → advanced)

Plain `MergeTree` is append-only: every insert becomes a new part, parts merge in the
background, nothing is ever "combined" logically at merge time beyond physical
compaction. The variants below add **logic** to what happens during a background merge
of rows sharing the same sort key — this is the whole reason they exist.

**`ReplacingMergeTree`** — keeps only the *last* row per sort key (by insertion order or
an explicit version column), during merges:
```sql
CREATE TABLE users (
    user_id UInt64, name String, updated_at DateTime
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;
-- Insert an updated row for the same user_id; the OLD row is dropped at the next merge
-- (not immediately! use FINAL or a dedup step for queries before the merge runs)
```

**`SummingMergeTree`** — merges rows with the same sort key by *summing* numeric
columns:
```sql
CREATE TABLE daily_totals (
    date Date, product_id UInt64, revenue Float64
) ENGINE = SummingMergeTree(revenue)
ORDER BY (date, product_id);
-- Multiple inserts for the same (date, product_id) get summed together at merge time
```

**`AggregatingMergeTree`** — like SummingMergeTree, but for arbitrary aggregate
functions (not just sum), typically paired with a Materialized View (Day 6) computing
`avgState()`, `uniqState()`, etc.

**`CollapsingMergeTree` / `VersionedCollapsingMergeTree`** — models updates as a pair of
rows: one with `sign = -1` (cancels a previous row) and one with `sign = +1` (the new
value); merges "collapse" matching pairs away, giving you mutable-looking data on top of
an append-only engine.

## 3. How It Really Works (Internals)

All of these still write append-only parts on insert — **the special logic only applies
during background merges**, not at insert time and not automatically at query time
either. This is the single most important, most-missed nuance: right after an insert,
you may have both the "old" and "new" version of a row physically present until the
next merge runs. Queries that need correctness *right now* must either use `FINAL`
(forces a merge-time computation at query time — real performance cost) or explicitly
aggregate (e.g., `SELECT argMax(name, updated_at) ... GROUP BY user_id` instead of
relying on `ReplacingMergeTree` to have already deduplicated).

```
INSERT row v1 (user_id=1, name="Christy")   → Part A
INSERT row v2 (user_id=1, name="Christopher")→ Part B
                    │
        (background merge runs eventually)
                    │
                    ▼
        Part A+B merged → only v2 survives (ReplacingMergeTree logic)

  Query BEFORE merge runs: SELECT * WHERE user_id=1 → could return BOTH rows!
```

## 4. Architecture & Design Pattern Spotlight

**Pattern: deferred, merge-time conflict resolution** instead of resolving conflicts
at write time (the way an upsert/`ON CONFLICT` in Postgres would). This trades
write-time cost (Postgres pays it on every write) for query-time uncertainty (ClickHouse
defers it, and you must be deliberate about handling not-yet-merged duplicates) — a
direct consequence of the log-structured, append-only storage pattern you saw on Day 1.

## 5. Hands-On Lab
```sql
CREATE TABLE user_profile (
    user_id UInt64, name String, updated_at DateTime
) ENGINE = ReplacingMergeTree(updated_at) ORDER BY user_id;

INSERT INTO user_profile VALUES (1, 'Christy', '2026-08-01 10:00:00');
INSERT INTO user_profile VALUES (1, 'Christopher', '2026-08-02 10:00:00');

SELECT * FROM user_profile;                 -- may show BOTH rows (no merge yet!)
SELECT * FROM user_profile FINAL;           -- forces correctness, at a cost
OPTIMIZE TABLE user_profile FINAL;          -- force a merge now (fine in dev, avoid routinely in prod)
SELECT * FROM user_profile;                 -- now shows only the latest row
```

## 6. Real-World Product Comparison

- Any team doing **CDC (change-data-capture)** ingestion from an OLTP database into
  ClickHouse (a very common pattern, and directly relevant to Kafka Connect/Debezium,
  Week 2 Day 13) typically reaches for `ReplacingMergeTree` or
  `VersionedCollapsingMergeTree` to represent the upstream table's updates/deletes.
- `SummingMergeTree`/`AggregatingMergeTree` are the standard building block behind
  **real-time rollup dashboards** — pre-aggregating at ingest time so dashboard
  queries hit far less raw data, a pattern you'll formalize with Materialized Views on
  Day 6.
- Contrast with **BigQuery**: has no equivalent engine-choice concept at all — it's a
  fully managed system where you don't choose a storage engine, you just write
  `MERGE`/`UPDATE` statements and BigQuery handles it, at its own cost/latency profile.
  This is a genuine capability ClickHouse asks you to actively engineer around.

## 7. Common Production Pitfalls
- Assuming `ReplacingMergeTree` deduplicates immediately on insert — it doesn't; this
  is the single most common ClickHouse mistake for people coming from OLTP databases.
- Overusing `FINAL` on large tables in hot query paths — it's correct, but forces
  merge-time work at query time and can be dramatically slower than an unmerged read
  or a properly pre-aggregated Materialized View.
- Running `OPTIMIZE TABLE ... FINAL` routinely in production as a "just make it
  correct" habit — it's a genuinely expensive operation on large tables and should be
  an occasional maintenance action, not a query-time crutch.

## 8. Review Questions
1. Why can a `ReplacingMergeTree` table return duplicate rows for a query run
   immediately after two inserts?
2. What's the actual cost of using `FINAL` on every query, and when is it worth paying?
3. When would you reach for `SummingMergeTree` vs. `AggregatingMergeTree`?
4. How does BigQuery avoid needing this whole engine-choice decision, and what do you
   give up in exchange?

## 9. Proficiency Checkpoint
If you can pick the right engine variant for a given data-update pattern and correctly
explain why "just inserted" doesn't mean "already deduplicated," you're at Level 2,
moving into Level 3.

## Next
Day 3 covers the primary key and sparse index — why `ORDER BY` is the single most
consequential design decision for a MergeTree table's query performance.
