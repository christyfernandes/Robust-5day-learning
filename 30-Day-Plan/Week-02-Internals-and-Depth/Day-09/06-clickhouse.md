# Day 9: ClickHouse — The JOIN Fan-Out Problem (Your Live MDO Portal Issue)

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Reproduce a fan-out bug with a fact + dimension table, observe an inflated `SUM()`,
and fix it — this is a direct, deliberate rehearsal of your real production
investigation.

## 2. Core Concept (basics → advanced)

**Fan-out** happens when a `JOIN` matches more than one row on the "many" side for a
single row on the "one" side, and an aggregation is computed *after* that join —
silently multiplying the aggregated value by however many matching rows existed, rather
than the count you actually intended.

```
fact table (orders):              dimension table (order_items, "should" be 1:1 but isn't):
  order_id=1, amount=100            order_id=1, item="A"
                                    order_id=1, item="B"    ← TWO rows for order_id=1!
                                    order_id=1, item="C"    ← THREE rows for order_id=1!

SELECT o.order_id, SUM(o.amount)
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
GROUP BY o.order_id

-- WRONG RESULT: amount gets summed 3 times (once per matching order_items row)
-- order_id=1 → SUM(amount) = 300, not 100  ← this is fan-out, silently inflating the SUM
```

This is exactly the shape of the MDO portal dashboard issue: a metric that should
reflect one fact-table row's value is being multiplied by however many rows a join
brings in on the other side — and because the join *executes correctly* (it's not
returning wrong rows, just more of them than the aggregation logic expects), this bug
produces a plausible-looking, wrong number rather than an obvious error.

## 3. How It Really Works (Internals)

This bites columnar, denormalized-first engines like ClickHouse **specifically**
because the natural ClickHouse-idiomatic approach — wide, pre-joined/denormalized
tables, minimal normalization — makes accidental one-to-many relationships easy to
introduce without realizing it. Contrast with a normalized OLTP schema, where such a
one-to-many relationship is usually explicit and intentional (a proper foreign-key
relationship, joined deliberately for a specific reason) — ClickHouse's whole
philosophy of "denormalize aggressively, storage is cheap, joins are what you avoid"
means the *discipline* of checking cardinality before aggregating is not built into
the schema the way normalized foreign keys somewhat enforce it.

**The fix, in order of preference:**
1. **Aggregate before joining** — compute the aggregation on the fact table *first*
   (`GROUP BY order_id` on `orders` alone, if that's genuinely all you need), then join
   the dimension table afterward only for attributes you need to display, never for
   values you're summing.
2. **Use a dictionary instead of a JOIN** (Day 11's ClickHouse lesson) — if the
   "dimension" side is really just a lookup (one value per key), a `dictGet()` call
   sidesteps the join (and its fan-out risk) entirely.
3. **Deduplicate or pre-aggregate the many-side before joining**, if you genuinely need
   dimension attributes and the fan-out is unavoidable structurally — explicitly
   collapse the many-side to one row per key first (e.g., `argMax` or `any()` per key)
   so the join is provably 1:1 before you aggregate.

## 4. Architecture & Design Pattern Spotlight

**Pattern: row multiplication before aggregation — a correctness bug that hides inside
a syntactically valid query.** The general principle worth internalizing broadly:
**always determine and verify actual join cardinality (1:1, 1:many, many:many)
*before* deciding whether it's safe to aggregate after the join** — this is precisely
the review discipline your MDO portal investigation needs to apply to every
dashboard query currently suspected of cost/correctness issues.

## 5. Hands-On Lab

```sql
CREATE TABLE orders (order_id UInt32, amount Decimal(10,2)) ENGINE = MergeTree ORDER BY order_id;
CREATE TABLE order_items (order_id UInt32, item String) ENGINE = MergeTree ORDER BY order_id;

INSERT INTO orders VALUES (1, 100.00), (2, 50.00);
INSERT INTO order_items VALUES (1, 'A'), (1, 'B'), (1, 'C'), (2, 'X');

-- reproduce the bug:
SELECT o.order_id, SUM(o.amount) AS total
FROM orders o JOIN order_items i ON o.order_id = i.order_id
GROUP BY o.order_id;
-- order_id=1 incorrectly shows 300.00 (100 × 3 matching item rows), not 100.00

-- the fix — aggregate BEFORE joining:
SELECT order_id, amount AS total FROM orders;
-- (if you need item-level detail alongside, join AFTER this aggregation, never before it)
```
Confirm the inflated result, then confirm the fix produces the correct `100.00` for
order 1. Now go find one real MDO portal dashboard query and check its actual join
cardinality using `system.query_log` or an `EXPLAIN` — is it provably 1:1, or could it
be silently fanning out the same way?

## 6. Real-World Product Comparison

- This exact failure mode is well-documented across **every** columnar/OLAP engine
  that supports JOIN (BigQuery, Snowflake, Druid) — it's a fundamental SQL semantics
  issue (aggregation after a one-to-many join), not a ClickHouse-specific bug, though
  ClickHouse's denormalize-by-default culture means it's encountered more often there
  in practice.
- Traditional **normalized OLTP** systems (Postgres/MySQL) hit the identical bug when
  developers write the same mistaken query shape — the difference is cultural/habitual
  (normalized schemas make people more consciously aware of cardinality), not technical.

## 7. Common Production Pitfalls

- Trusting a dashboard number because the query "runs without error" — a fan-out bug
  produces a plausible, wrong number with zero error signal.
- Adding a `DISTINCT` as a quick fix without understanding *why* it works (or verifying
  it actually fixes the specific query) — `DISTINCT` can mask fan-out in some shapes of
  query but is not a general, reliable fix, and can itself introduce different
  correctness issues.
- Not systematically auditing existing dashboard queries for this pattern after finding
  it once — if it happened in one MDO portal query, it's worth checking every query with
  a similar join+aggregate shape.

## 8. Review Questions
1. Why does a fan-out bug produce a plausible-looking wrong number instead of an error?
2. Why does ClickHouse's denormalize-first culture make this bug more likely than in a
   normalized OLTP schema?
3. What's the preferred fix, in order, and why is "aggregate before joining" the first
   choice?
4. How would you audit an existing dashboard query for undetected fan-out risk?

## 9. Proficiency Checkpoint
If you can look at a real production query and correctly determine its join
cardinality before trusting an aggregation built on top of it, you're at a genuine
Level 3.5+ — this is precisely the skill your live MDO portal investigation requires,
rehearsed here before applying it to the real dashboards.

## Next
Day 10 covers hot/cold tiering — your exact TTL-to-GCS storage-policy setup — while
Day 11 revisits this fan-out problem with dictionaries as the structural fix.
