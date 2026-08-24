# Day 8: Elasticsearch — Distributed Search Internals: Query-Then-Fetch

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Run a query against a multi-shard index, inspect the `_search` profile API's per-shard
timing, and explain the two-phase query-then-fetch execution model.

## 2. Core Concept (basics → advanced)

A search request against a multi-shard index executes in two distinct phases:

- **Query phase**: the coordinating node forwards the request to every relevant
  shard; each shard executes the query *locally* and returns only lightweight
  metadata — document IDs and scores — not full documents. The coordinating node merges
  these per-shard results and determines the final top-N globally.
- **Fetch phase**: only *after* the coordinating node knows exactly which documents are
  in the final top-N does it request the *actual document content* for just those
  specific documents from the shards that hold them — not from every shard, and not for
  every candidate, only the final winners.

```
Query phase:   Coordinator ──▶ Shard 1 (top 10 IDs+scores, LOCAL to shard 1)
                            ──▶ Shard 2 (top 10 IDs+scores, LOCAL to shard 2)
                            ──▶ Shard 3 (top 10 IDs+scores, LOCAL to shard 3)
               Coordinator merges → GLOBAL top 10 IDs

Fetch phase:   Coordinator ──▶ requests ONLY those 10 documents' full content
                                 from whichever shards actually hold them
```

## 3. How It Really Works (Internals)

This two-phase split exists specifically to avoid the expense of transferring full
document content for every candidate across the network — only lightweight
IDs+scores travel during the (larger) query phase, and full document bodies travel
only for the (much smaller) final result set during the fetch phase. This is exactly
the scatter-gather pattern from Day 4's aggregation lesson, applied to plain search
rather than aggregation — same coordinator/shard shape, different payload.

The `_search` **profile API** exposes per-shard timing for both phases explicitly —
this is the tool for diagnosing "why is this specific query slow": is one shard
consistently the slowest (a data-skew or hardware problem on that shard), or is the
overall query phase itself expensive (perhaps due to an inefficient query structure),
or is the fetch phase surprisingly slow (perhaps due to fetching very large documents,
or too many `_source` fields not actually needed by the caller)?

## 4. Architecture & Design Pattern Spotlight

**Pattern: scatter-gather, refined into a two-phase protocol that minimizes data
transferred until it's actually needed.** This is directly comparable to
**ClickHouse's distributed query routing** (today's ClickHouse lesson): both compute
cheap local partial results first, and only pull the "real" data for what's actually
needed in the final answer — a recurring efficiency pattern in every distributed
query engine in this curriculum.

## 5. Hands-On Lab

```json
GET /products/_search
{
  "profile": true,
  "query": { "match": { "title": "wireless headphones" } }
}
```
Run this against your Day 3 `products` index (or a larger synthetic one with several
shards for a more meaningful profile). In the response, find the `profile.shards`
array — compare `query` phase timing across shards. If you have a multi-shard index,
try adding `"_source": false` to skip the fetch phase's document-body retrieval
entirely and compare total latency.

## 6. Real-World Product Comparison

- This exact two-phase query-then-fetch model is standard across Lucene-based search
  engines, including **OpenSearch** (the community fork) — it's a foundational,
  not implementation-specific, design decision.
- Contrast with **ClickHouse's distributed table query routing** (today's ClickHouse
  lesson): conceptually similar scatter-gather shape, but ClickHouse typically merges
  actual aggregated *values* rather than document IDs+scores — different payload
  because the query shape (analytical rollup vs. ranked document retrieval) is
  different.

## 7. Common Production Pitfalls

- Requesting large `_source` fields (or all fields) when only a few are actually
  needed by the caller — inflates fetch-phase cost unnecessarily; `_source` filtering
  is a real, easy performance lever.
- Diagnosing "slow query" purely from total latency without checking the profile
  API's phase breakdown — the fix for a slow query phase (query structure, index
  design) is completely different from the fix for a slow fetch phase (`_source`
  filtering, document size).
- Not noticing one consistently slow shard across many queries — a strong signal of
  uneven shard sizing or a hardware issue on that specific node, not a general query
  problem.

## 8. Review Questions
1. Why does the query phase deliberately avoid transferring full document content?
2. What determines which specific documents get fetched during the fetch phase?
3. How would you use the profile API to distinguish a query-phase problem from a
   fetch-phase problem?
4. Why is this the same underlying pattern as scatter-gather aggregation?

## 9. Proficiency Checkpoint
If you can read a real profile-API response and correctly diagnose which phase (and
which shard) is the actual bottleneck, you're at Level 3.

## Next
Day 9 covers relevance tuning — BM25's `k1`/`b` parameters and `function_score` — now
that you understand exactly how a query executes underneath.
