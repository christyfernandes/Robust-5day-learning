# Day 16: Elasticsearch — Query Performance: Profiling Expensive Query Traps

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Profile a leading-wildcard query with the `_search` profile API, and explain
precisely why it's expensive relative to other query shapes.

## 2. Core Concept (basics → advanced)

Some query patterns are inherently expensive against Lucene's inverted-index
structure (Week 1, Day 1), regardless of cluster size or hardware:

- **Leading wildcard queries** (`*ess` — wildcard at the *start* of the term): the
  inverted index is sorted alphabetically by term, meaning a trailing wildcard
  (`ess*`) can efficiently scan a contiguous alphabetical range, but a *leading*
  wildcard has no such contiguous range to exploit — it must effectively scan
  the entire term dictionary to find matches, an operation whose cost scales with
  total vocabulary size, not with how selective the query "feels."
- **Scripted queries/scoring**: running arbitrary script logic (Painless, commonly)
  per matching document bypasses precomputed index structures entirely, paying
  script-execution cost for every candidate document rather than benefiting from
  Lucene's optimized native query execution.

## 3. How It Really Works (Internals)

The inverted index (Week 1, Day 1) maps each term to a list of documents containing
it, and this mapping is efficiently searchable specifically because terms are stored
**sorted**. A trailing wildcard can binary-search to the right alphabetical
neighborhood and scan forward only as far as needed — a leading wildcard, structurally,
cannot use this sorted-order property at all, since matching "ends with X" gives no
information about *where alphabetically* such a term would sit. This is the same
class of insight as ClickHouse's `ORDER BY` prefix-matching rule (Week 1, Day 3) —
an index (any index) can only accelerate queries that align with the property it's
actually sorted/organized by.

## 4. Architecture & Design Pattern Spotlight

**Pattern: query cost analysis grounded in the underlying index structure, not
intuition about "how selective" a query looks.** This directly parallels Week 1 Day
3's ClickHouse sparse-index-prefix lesson — in both systems, whether a query can use
an index efficiently depends on a structural property of the query relative to how
the index is organized, not on how the query "reads" to a human.

## 5. Hands-On Lab

```json
GET /products/_search
{ "profile": true,
  "query": { "wildcard": { "title": "*phones" } } }
```
Run this against your test `products` index and inspect the profile output's timing
— compare it against the equivalent trailing-wildcard query (`"phones*"`) and a plain
`match` query on the same field. Quantify the difference directly, and note where
in the profile breakdown the leading-wildcard cost actually shows up.

## 6. Real-World Product Comparison

- Production search systems commonly **disallow or heavily restrict** leading-
  wildcard queries in user-facing search boxes for exactly this reason — offering an
  **edge n-gram** analyzer (indexing partial-word prefixes at index time) as an
  alternative when "search-as-you-type" or suffix matching is a genuine product
  requirement, rather than accepting the leading-wildcard cost at query time.
- **Elastic's own documentation** explicitly flags both leading wildcards and
  uncached scripted queries as anti-patterns for exactly this structural reason, not
  as an arbitrary style preference.

## 7. Common Production Pitfalls

- Allowing arbitrary leading-wildcard queries from user input without realizing the
  structural cost, discovering it only once query volume or vocabulary size makes
  the cost visible.
- Using scripted scoring for logic that could be expressed via a built-in query type
  (e.g., `function_score`, Week 2 Day 9) — built-in query types benefit from
  Lucene's optimized native execution in ways ad hoc scripts don't.
- Not using the profile API to distinguish "this specific query shape is inherently
  expensive" from "the cluster is generally under-resourced" — very different fixes.

## 8. Review Questions
1. Why can a trailing wildcard use the inverted index efficiently while a leading
   wildcard cannot?
2. What's the structural reason scripted queries bypass index optimizations?
3. How does this connect to ClickHouse's `ORDER BY` prefix-matching rule from Week 1?
4. What's a common alternative to leading-wildcard search for a genuine product
   requirement?

## 9. Proficiency Checkpoint
If you can identify and explain why a specific query shape is structurally expensive,
and propose a better-fitting alternative, you're at Level 3.5.

## Next
Day 17 covers cluster health monitoring — the `_cluster/health` and `_nodes/
hot_threads` APIs — for diagnosing broader cluster-level issues beyond a single
query's cost.
