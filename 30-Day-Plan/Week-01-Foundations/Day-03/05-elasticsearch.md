# Day 3: Elasticsearch — Query DSL & BM25 Scoring

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Write a compound `bool` query mixing scoring and non-scoring clauses correctly, and
explain what actually produces a document's relevance score.

## 2. Core Concept (basics → advanced)

Elasticsearch's Query DSL has two fundamentally different execution paths, and mixing
them up is the single most common beginner mistake:

- **Query context**: "how *well* does this document match?" — computes a relevance
  **score**. Used for the parts of a search that should affect ranking (e.g., matching
  the user's search terms).
- **Filter context**: "does this document match, yes or no?" — no scoring, and
  **cacheable** by Elasticsearch since the answer doesn't change between identical
  queries. Used for anything that should narrow results without affecting ranking (e.g.,
  `status: "published"`, a date range, a category filter).

```json
{
  "query": {
    "bool": {
      "must":   [ { "match": { "title": "wireless headphones" } } ],  // scores
      "should": [ { "match": { "brand": "sony" } } ],                 // scores, optional boost
      "filter": [ { "term":  { "status": "in_stock" } },              // no score, cached
                  { "range": { "price": { "lte": 200 } } } ]          // no score, cached
    }
  }
}
```
Putting a filter-like clause (e.g., `status: published`) into `must` instead of `filter`
still works correctly, but silently makes it contribute to the score *and* miss out on
filter caching — a subtle correctness-adjacent performance bug.

## 3. How It Really Works (Internals)

Elasticsearch's default scoring algorithm is **BM25** (a refinement of the older TF-IDF).
Three inputs, combined:
- **Term frequency (TF)**: how often the search term appears in *this* document — but
  BM25 applies **saturation**, so the 10th occurrence of a term contributes much less
  additional score than the 2nd (unlike raw TF-IDF, where score scales linearly forever).
- **Inverse document frequency (IDF)**: rare terms across the whole index score higher
  than common ones — matching "quantum" is worth more than matching "the."
- **Field length normalization**: a match in a short field (a title) counts for more than
  the same match in a long field (a full product description), since a match is a larger
  fraction of a short document's total content.

Filter-context clauses skip this scoring computation entirely — they're evaluated as a
plain bitset match, and Elasticsearch caches frequently-used filter bitsets so repeated
identical filters (like a common category filter) become nearly free on subsequent
queries.

## 4. Architecture & Design Pattern Spotlight

**Pattern: probabilistic relevance ranking.** BM25 is a scoring function, not a boolean
match — it's ranking documents by an *estimate of relevance*, not proving a fact about
them. This mental shift (from "does it match" to "how well, probabilistically, does it
match") is the core skill for anything you'll build with search in the loop, and it's
also why the same query against the same data can reasonably return different orderings
after a reindex with different analyzer settings.

## 5. Hands-On Lab

```bash
curl -X POST "localhost:9200/products/_bulk" -H 'Content-Type: application/json' --data-binary @- <<'EOF'
{ "index": {} }
{ "title": "Sony Wireless Headphones", "brand": "sony", "status": "in_stock", "price": 149 }
{ "index": {} }
{ "title": "Generic Wired Headphones", "brand": "generic", "status": "in_stock", "price": 19 }
{ "index": {} }
{ "title": "Sony Wireless Earbuds", "brand": "sony", "status": "out_of_stock", "price": 99 }
EOF
```
Now run the compound query above and inspect `_score` on each hit (`GET
/products/_search?explain=true` for the full BM25 breakdown). Then move the `status`
filter into `must` instead and compare: does `status` now affect the score? Does the
out-of-stock item still get returned, since it's no longer filtered out?

## 6. Real-World Product Comparison

- **Wikipedia's CirrusSearch** runs on Elasticsearch and relies heavily on BM25 tuning
  (field boosts, custom analyzers) to rank article search — a domain where naive TF-IDF
  would over-favor documents that simply repeat the search term many times.
- **Algolia** takes a fundamentally different approach: a tunable, rule-based ranking
  formula (typo tolerance, popularity signals, custom business rules) rather than a pure
  probabilistic model — often preferred for e-commerce search where "typo-tolerant,
  business-rule-driven" beats "textbook-relevant" as a product goal.

## 7. Common Production Pitfalls

- Putting non-scoring clauses in `must` instead of `filter` — works, but loses caching
  and pollutes the score with irrelevant signal.
- Forgetting that BM25 score is **not comparable across different queries** (only within
  the same query's result set) — don't build alerting/thresholds on absolute score
  values across different searches.
- Not re-testing relevance after an analyzer change — reindexing with a different
  tokenizer/filter chain can silently reorder results for the exact same query.

## 8. Review Questions
1. What's the practical (not just semantic) difference between `must` and `filter`?
2. Why does BM25 apply term-frequency saturation instead of scaling linearly?
3. Why is a match in a short field worth more than the same match in a long field?
4. Why shouldn't you compare BM25 scores across two different search queries?

## 9. Proficiency Checkpoint
If you can correctly place every clause of a real compound query into `must` / `should`
/ `filter` and explain why, you're at Level 2 moving toward Level 3.

## Next
Day 4 covers aggregations — the mechanism behind dashboard-style rollups, and the direct
conceptual twin of a ClickHouse `GROUP BY`.
