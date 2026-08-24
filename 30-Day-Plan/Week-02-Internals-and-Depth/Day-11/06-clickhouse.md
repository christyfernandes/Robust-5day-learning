# Day 11: ClickHouse — Dictionaries: Fast Lookups as a JOIN Alternative

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Replace a small dimension-table JOIN with a `dictGet()` call, and confirm it produces
both a simpler query plan and correctness immunity to the fan-out problem from Day 9.

## 2. Core Concept (basics → advanced)

A **dictionary** in ClickHouse is an in-memory (or partially cached) key-value
structure, loaded from a source (a table, a file, an external database) on a refresh
schedule, and queried via `dictGet(dict_name, attribute, key)` rather than a `JOIN`.
For genuinely "lookup" relationships — a `dimension` table where you want exactly one
attribute value per key, not a join that could accidentally match multiple rows — a
dictionary sidesteps the entire fan-out risk class from Day 9, because `dictGet()` is
defined to return exactly one value per key, by construction, never "however many
matching rows happened to exist."

```
JOIN approach (fan-out risk from Day 9):
  SELECT o.order_id, o.amount, d.tier
  FROM orders o JOIN customer_dim d ON o.customer_id = d.customer_id
  -- if customer_dim somehow has 2 rows for one customer_id, amount gets
  -- silently duplicated in any subsequent aggregation

Dictionary approach (fan-out STRUCTURALLY IMPOSSIBLE):
  SELECT order_id, amount, dictGet('customer_dim', 'tier', customer_id) AS tier
  FROM orders
  -- dictGet() always returns exactly ONE value per key — there is no
  -- "multiple matching rows" case to accidentally multiply anything
```

## 3. How It Really Works (Internals)

Dictionaries are loaded (fully or partially, depending on the configured **layout** —
`flat`, `hashed`, `cache`, `direct`, among others) into memory ahead of query time,
and refreshed on a configurable interval independent of any specific query — meaning a
`dictGet()` lookup at query time is typically a fast, in-memory hash lookup, with no
shuffle, no join-plan complexity, and critically, **no risk of the many-side
cardinality surprising you**, since a dictionary is defined as a key→value mapping,
not a general relation that could have duplicate keys unless you explicitly configure
it otherwise.

This makes dictionaries the natural, structural fix (not just a query-rewrite
workaround) for exactly the class of bug investigated on Day 9 — anywhere a "dimension"
table is genuinely meant to be a lookup (one row per key), converting the JOIN to a
dictionary lookup both simplifies the query and makes the fan-out bug class
*impossible to reintroduce later*, since the data structure itself enforces the
one-value-per-key invariant that a JOIN's underlying table can silently violate.

## 4. Architecture & Design Pattern Spotlight

**Pattern: external dictionary lookup instead of JOIN — trading generality (a JOIN can
express arbitrary relationships) for both performance and a correctness guarantee (a
dictionary can't fan out).** This is the same "narrow the interface to prevent a whole
bug class" philosophy behind strongly-typed APIs generally — a `JOIN` is more powerful
but leaves cardinality assumptions implicit and unenforced; a dictionary makes the
"exactly one value per key" assumption explicit and structurally guaranteed.

## 5. Hands-On Lab

```sql
CREATE DICTIONARY customer_dim_dict (
    customer_id UInt32,
    tier String
)
PRIMARY KEY customer_id
SOURCE(CLICKHOUSE(TABLE 'customer_dim'))
LAYOUT(HASHED())
LIFETIME(300);   -- refresh every 5 minutes

SELECT
    order_id,
    amount,
    dictGet('customer_dim_dict', 'tier', customer_id) AS tier
FROM orders;
```
Compare `EXPLAIN` output for this query against the equivalent `JOIN`-based version
from Day 9's lab — confirm the dictionary version has no join step in its plan at all.
Then deliberately insert a duplicate `customer_id` row into `customer_dim` (the fan-out
setup from Day 9) and confirm the `JOIN` version now produces an inflated `SUM()` while
the `dictGet()` version is **completely unaffected**, since it was never capable of
expressing the many-rows-per-key case to begin with.

## 6. Real-World Product Comparison

- Dictionaries are a distinctive ClickHouse feature relative to most general-purpose
  SQL engines — **BigQuery** and most warehouses require an explicit `JOIN` for this
  same lookup pattern, accepting the fan-out risk as an ever-present possibility that
  must be guarded against query by query rather than structurally eliminated.
- This is directly the fix worth proposing for any MDO portal dashboard query
  currently using a `JOIN` purely for a lookup-shaped dimension — converting to a
  dictionary is both a performance win and a permanent fix for that specific query's
  fan-out exposure.

## 7. Common Production Pitfalls

- Using a dictionary for a relationship that's genuinely one-to-many (not a true
  lookup) — `dictGet()` will silently return only one value in ways that may not match
  your actual intent; dictionaries are for genuine key→value lookups only.
- Setting `LIFETIME` too long for a dimension table that changes frequently —
  dictionary data can be stale relative to the source table between refreshes, a
  distinct trade-off from a JOIN (which always reads current data).
- Choosing an inappropriate layout (e.g., `flat` for a very high-cardinality key space)
  — layout choice affects both memory usage and lookup performance, and the defaults
  aren't universally correct for every dictionary's actual key cardinality.

## 8. Review Questions
1. Why is a dictionary structurally immune to the fan-out problem, not just less
   likely to trigger it?
2. What's the practical cost of the `LIFETIME` refresh interval, and what does it
   trade against always-current JOIN semantics?
3. When would a dictionary be the *wrong* choice, despite its fan-out immunity?
4. Why does this represent a structural fix rather than a workaround?

## 9. Proficiency Checkpoint
If you can identify a real dashboard query using a JOIN purely as a lookup, and
correctly convert it to a dictionary while explaining exactly why that eliminates the
fan-out risk class, you're at Level 3.5 — a directly deployable fix for this week's
real production investigation.

## Next
Day 12 covers codecs and compression — `Delta`, `DoubleDelta`, `Gorilla` — directly
relevant to your cost-reduction mission.
