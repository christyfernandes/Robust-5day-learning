# Day 12: PySpark — File Formats: Parquet Internals

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Inspect a Parquet file's row-group metadata (min/max statistics) and explain how
predicate and column pushdown use that metadata to skip work entirely.

## 2. Core Concept (basics → advanced)

Parquet is a **columnar** file format (values for one column are stored contiguously,
not row-by-row) organized into **row groups** — large horizontal slices of the file
(e.g., 128MB each), within which data is further split by column. Each row group
carries **embedded statistics per column** — minimum value, maximum value, null count
— written directly into the file's own metadata (the "footer").

```
Parquet file:
┌─────────────── Row Group 1 ───────────────┐
│ Column A: [values...] | min=1,  max=1000  │
│ Column B: [values...] | min=10, max=50    │
└────────────────────────────────────────────┘
┌─────────────── Row Group 2 ───────────────┐
│ Column A: [values...] | min=1001, max=2000│
│ Column B: [values...] | min=5,    max=45  │
└────────────────────────────────────────────┘
                    Footer: schema + per-row-group statistics
```

## 3. How It Really Works (Internals)

**Predicate pushdown**: given a query filter like `WHERE column_a > 1500`, Spark's
Parquet reader checks each row group's *metadata* (`min`/`max` for `column_a`) **before
reading any actual data** — Row Group 1 (max=1000) is provably irrelevant and skipped
entirely, without ever touching its bytes on disk. This is conceptually the same
"skip using cheap coarse metadata" idea as ClickHouse's sparse index (Week 1, Day 3) —
different mechanism (per-row-group min/max vs. a granule-level sparse index), same
underlying strategy.

**Column pushdown** (also called projection pushdown): if a query only needs
`column_a` and `column_b` out of a table with 50 columns, Parquet's columnar layout
means the reader can read *only* those two columns' bytes from disk, skipping the other
48 entirely — this is precisely why columnar formats are dramatically more efficient
than row-oriented formats (like CSV) for wide-table analytical queries that only touch
a few columns at a time.

## 4. Architecture & Design Pattern Spotlight

**Pattern: columnar file format with embedded statistics for pruning.** This exact
pattern — skip work using cheap, coarse, pre-computed metadata before touching real
data — recurs as one of the most consistently reused ideas in this entire curriculum:
ClickHouse's sparse index (Week 1, Day 3), BigQuery's partition/column pruning,
Elasticsearch's segment-level skip lists, and now Parquet's row-group statistics are
all instances of the identical underlying strategy, implemented differently per system.

## 5. Hands-On Lab

```python
import pyarrow.parquet as pq

df.write.parquet("/tmp/day12_test.parquet")

pf = pq.ParquetFile("/tmp/day12_test.parquet")
for i in range(pf.num_row_groups):
    rg_meta = pf.metadata.row_group(i)
    col_meta = rg_meta.column(0)  # first column's stats
    print(f"Row group {i}: min={col_meta.statistics.min}, max={col_meta.statistics.max}")
```
Run a Spark query with a `WHERE` filter on this column, and enable Spark's Parquet
predicate-pushdown logging (or check `.explain()` for `PushedFilters`) — confirm the
filter is listed as pushed down. Compare total bytes read (visible in the Spark UI's
input size metric) between a filter that should skip most row groups versus one that
can't skip any.

## 6. Real-World Product Comparison

- **ClickHouse's native MergeTree** format achieves similar pruning through its own
  sparse index and granule mechanism (Week 1, Day 3) rather than Parquet's row-group
  statistics — genuinely different implementations converging on the same "skip data
  using coarse metadata" strategy, worth comparing explicitly since your own migration
  work spans exactly this format boundary.
- **Apache Iceberg and Delta Lake** (Day 13) build additional metadata layers *on top
  of* Parquet files specifically to make this pruning even more effective at scale
  (tracking statistics across many files without needing to open each file's footer
  individually).

## 7. Common Production Pitfalls

- Writing very small Parquet files (e.g., from over-partitioned output) — row-group
  statistics lose their pruning value when each file/row-group is tiny, since there's
  little to skip; this also creates the "small files problem" that plagues many lake
  architectures.
- Not verifying predicate pushdown is actually happening for a specific query shape —
  some filter expressions (complex UDFs, certain type casts) aren't eligible for
  pushdown, silently forcing a full scan despite the file format's capability.
- Writing data without any logical sort order relative to common filter columns —
  Parquet's min/max pruning only helps when a row group's value range is actually
  narrow, which depends on the data being reasonably sorted/clustered by that column.

## 8. Review Questions
1. What specifically does predicate pushdown check, and when does it check it?
2. Why does column pushdown matter more for wide tables than narrow ones?
3. Why do very small row groups reduce the value of embedded statistics?
4. How is this the same underlying pattern as ClickHouse's sparse index?

## 9. Proficiency Checkpoint
If you can inspect real Parquet row-group metadata and predict which row groups a
given filter would skip, you're at Level 3.

## Next
Day 13 covers the lakehouse formats (Delta Lake, Iceberg, Hudi) built on top of
Parquet — adding ACID transactions and time travel to exactly this file format.
