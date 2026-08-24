# Day 4: Elasticsearch — Aggregations

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Build a `terms` + `date_histogram` aggregation that mimics a real dashboard panel, and
explain how a distributed aggregation actually gets computed across shards.

## 2. Core Concept (basics → advanced)

Aggregations are Elasticsearch's answer to "give me a rollup, not individual documents"
— exactly the same job a `GROUP BY` does in SQL/ClickHouse. Three families:

- **Metric aggregations**: a single number from a set of documents (`avg`, `sum`, `min`,
  `max`, `cardinality` for approximate distinct count).
- **Bucket aggregations**: split documents into groups (`terms` = group by field value,
  `date_histogram` = group by time interval, `range` = group by numeric bucket) — and
  buckets can nest, and can contain metric aggregations inside them.
- **Pipeline aggregations**: aggregations computed from the *output* of other
  aggregations (e.g., a moving average over a `date_histogram`'s buckets), rather than
  from raw documents.

```json
{
  "size": 0,
  "aggs": {
    "by_day": {
      "date_histogram": { "field": "@timestamp", "calendar_interval": "day" },
      "aggs": {
        "by_category": {
          "terms": { "field": "category.keyword", "size": 10 },
          "aggs": { "avg_price": { "avg": { "field": "price" } } }
        }
      }
    }
  }
}
```
This single query reproduces exactly what a dashboard panel like "average price by
category, per day" would show — nested buckets with a metric inside, computed in one
distributed pass.

## 3. How It Really Works (Internals)

Aggregations execute as a **scatter-gather**: the coordinating node sends the
aggregation request to every relevant shard, each shard computes its own local partial
result, and the coordinating node merges the partial results into the final answer. For
exact metrics (sum, count, min, max) this merge is exact. For `terms` aggregations,
though, each shard only returns its *own* top-N buckets by document count — if a term is
common overall but not in the top-N on any single shard, it can be **undercounted or
missed entirely** in the merged result. This is a genuine, well-known accuracy caveat
(mitigated by requesting more buckets per shard than you actually need, via the
`shard_size` parameter), not a bug.

**Cardinality** aggregations (approximate distinct count) use the **HyperLogLog**
algorithm rather than exact counting — trading a small, bounded error rate for
massively less memory than tracking every distinct value seen (this is the same
algorithm underlying ClickHouse's and BigQuery's approximate distinct-count functions,
covered directly in Day 2 of this curriculum).

## 4. Architecture & Design Pattern Spotlight

**Pattern: distributed rollup via scatter-gather with a merge step.** The exact shape
that any distributed `GROUP BY` takes — ClickHouse computing a `GROUP BY` across shards,
Spark computing an aggregation after a shuffle, and this ES aggregation are all the same
underlying pattern: compute local partials, merge globally. Recognizing this pattern is
exactly the skill that will make your BigQuery-dashboard-to-ClickHouse-equivalent
mapping work (this week's live task) go faster.

## 5. Hands-On Lab

Using the same `products` index from Day 3, build:
```json
{
  "size": 0,
  "aggs": {
    "by_brand": {
      "terms": { "field": "brand.keyword" },
      "aggs": { "avg_price": { "avg": { "field": "price" } } }
    }
  }
}
```
Then add a second dimension (nest a `date_histogram` if you add a timestamp field to
your test docs), and compare the response shape to what a Kibana/Grafana panel would
need to render a stacked bar chart — this is literally what those tools do under the
hood.

## 6. Real-World Product Comparison

- **Uber**'s internal analytics dashboards use Elasticsearch aggregations extensively
  for operational metrics where near-real-time (not perfectly exact) rollups are
  acceptable — the scatter-gather model gives fast results at the cost of the `terms`
  accuracy caveat above.
- Directly relevant to your work: this aggregation model is the **conceptual sibling**
  of what your MDO portal dashboards ask of BigQuery/ClickHouse via `GROUP BY` — the
  same nested-bucket-plus-metric shape, different engine underneath.

## 7. Common Production Pitfalls

- Trusting `terms` aggregation counts as exact when shard-level top-N truncation can
  under-count long-tail terms — always check `sum_other_doc_count` in the response.
  Not tuning `shard_size` when a `terms` aggregation feeds a business-critical report —
  the default is often too small for high-cardinality fields split across many shards.
- Running deep, expensive nested aggregations against a `size` (number of top-level
  buckets) that's far larger than actually needed — the multiplication of nested bucket
  computation grows fast.

## 8. Review Questions
1. Why can a `terms` aggregation undercount a term that's common overall but not locally
   common on any single shard?
2. What's the difference between a metric, bucket, and pipeline aggregation?
3. Why does cardinality use HyperLogLog instead of exact counting?
4. How is this scatter-gather model the same pattern as a distributed `GROUP BY`?

## 9. Proficiency Checkpoint
If you can build a nested bucket+metric aggregation that reproduces a real dashboard
panel, and explain the `terms` accuracy caveat, you're at Level 2 moving toward Level 3.

## Next
Day 5 covers Elasticsearch cluster architecture — node roles and how shards/replicas
are actually assigned across a real cluster, the infrastructure underneath today's
aggregations.
