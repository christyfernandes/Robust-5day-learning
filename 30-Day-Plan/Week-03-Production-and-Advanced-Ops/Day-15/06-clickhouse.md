# Day 15: ClickHouse — Query Profiling: EXPLAIN, system.query_log & Too-Many-Parts

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Profile a slow query using `EXPLAIN PIPELINE` and `system.query_log`, and correctly
identify the actual bottleneck rather than guessing.

## 2. Core Concept (basics → advanced)

Three complementary diagnostic tools, each answering a different question:
- **`EXPLAIN`** (plain, or with `indexes=1`): shows the *planned* query execution —
  which indexes/granules will be used (Week 1, Day 3), what join strategy is chosen.
- **`EXPLAIN PIPELINE`** (Week 2, Day 8): shows the actual vectorized execution
  pipeline stages and their parallelism.
- **`system.query_log`**: records what *actually happened* for completed queries —
  real rows read, real memory used, real duration — the ground truth to compare
  against what `EXPLAIN` predicted.

**Too-many-parts** is a distinct, common ClickHouse-specific performance problem: if
data is inserted in very small batches very frequently, MergeTree accumulates many
small parts faster than the background merge process (Week 1, Day 1) can consolidate
them — query performance degrades because more parts means more granule-index lookups
and more file handles to manage, and in severe cases ClickHouse will explicitly reject
further inserts ("too many parts") as a protective measure.

## 3. How It Really Works (Internals)

The real diagnostic workflow: run `EXPLAIN indexes=1` first to check whether the
sparse index (Week 1, Day 3) is actually being used as expected for the query's
filters — if not, that's very likely your primary bottleneck (a full scan where a
granule-skip should have been possible). If indexing looks correct, check
`system.query_log` for the query's actual `read_rows` and memory usage against what
the query's selectivity should predict — a mismatch here often points to unexpectedly
large row-group reads, a JOIN fan-out (Week 2, Day 9) inflating intermediate row
counts, or a too-many-parts situation forcing more granule lookups than the logical
data volume would otherwise require. Checking `system.parts` for the specific table's
active part count directly confirms or rules out the too-many-parts hypothesis.

## 4. Architecture & Design Pattern Spotlight

**Pattern: query-plan-driven tuning — diagnose using the plan and system tables
before guessing at a fix.** This mirrors the Spark UI-driven diagnostic discipline
from Week 1 Day 3 and the Elasticsearch profile-API discipline from Week 2 Day 8 —
across every system this month, the correct tuning workflow is "measure and diagnose
first, using the tool's own introspection facilities, then apply a targeted fix,"
never "guess and apply a generic fix."

## 5. Hands-On Lab

```sql
-- check if a real slow query is using the index as expected
EXPLAIN indexes = 1
SELECT * FROM events WHERE org_id = 42 AND event_time > now() - INTERVAL 7 DAY;

-- check its actual execution stats after running it
SELECT query, read_rows, read_bytes, memory_usage, query_duration_ms
FROM system.query_log
WHERE query LIKE '%org_id = 42%'
ORDER BY event_time DESC LIMIT 5;

-- check for a too-many-parts situation on the relevant table
SELECT table, count() AS active_parts
FROM system.parts
WHERE active
GROUP BY table
ORDER BY active_parts DESC;
```
Run this three-step workflow against a genuinely slow query in your test environment
(or, ideally, one from your real MDO portal dashboards) — write down which specific
hypothesis (index not used, unexpectedly large read, too-many-parts) the evidence
actually supports, rather than assuming a cause before checking.

## 6. Real-World Product Comparison

- This exact `EXPLAIN` + `system.query_log` diagnostic workflow is precisely how
  your team would approach any production ClickHouse slow-query investigation going
  forward — a directly reusable skill for post-migration operations.
- Too-many-parts is a **ClickHouse-specific** failure mode without a direct
  equivalent in BigQuery (a fully-managed engine that handles its own internal file
  organization) — worth explicitly flagging as a new operational concern your team
  will need to monitor for that didn't previously exist in your BigQuery-based
  workflow.

## 7. Common Production Pitfalls

- Assuming a query is slow because of "the cluster" generally, without checking
  `EXPLAIN`/`system.query_log` to identify the actual specific bottleneck.
- Ingesting data in very frequent, very small batches without awareness of the
  too-many-parts risk — batching inserts appropriately (fewer, larger batches) is a
  real operational practice, not an afterthought.
- Not distinguishing a genuinely slow query (needs a schema/index fix) from a
  resource-contention symptom (too many concurrent queries competing for the same
  cluster resources) — `system.query_log`'s memory/duration data for concurrent
  queries can help distinguish these.

## 8. Review Questions
1. What question does each of `EXPLAIN`, `EXPLAIN PIPELINE`, and `system.query_log`
   answer, respectively?
2. What specifically causes a too-many-parts situation, and why does it hurt query
   performance?
3. Why is "measure first, then fix" the correct diagnostic discipline here, as
   elsewhere this month?
4. How would too-many-parts show up differently than an indexing problem in your
   diagnostic workflow?

## 9. Proficiency Checkpoint
If you can run this three-tool diagnostic workflow on a real slow query and correctly
identify the actual bottleneck, you're at Level 3.5 — directly reusable for your
production cluster's ongoing operations.

## Next
Day 16 covers HAProxy query routing and per-query resource quotas — your own
cluster's exact routing layer.
