# Day 1: Elasticsearch — Search & Analytics Foundations

## Time: ~30 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain the **inverted index** concretely enough to predict why full-text search is
fast and why exact-match filtering on a keyword field is faster still, and perform
basic indexing/search operations.

## 2. Core Concept (basics → advanced)

**Start here if Elasticsearch is genuinely new to you.** Elasticsearch is a system for
storing documents (think: JSON objects, like a product listing or a log entry) and
searching/filtering/aggregating across huge numbers of them very quickly — its two
headline strengths are **full-text search** ("find documents whose description
mentions 'wireless keyboard', even if not word-for-word") and **fast rollups over
large volumes** (Week 1, Day 4's aggregations). An **index** in Elasticsearch is
roughly analogous to a table in a traditional database; a **document** is roughly
analogous to one row.

**Elasticsearch is a distributed layer over Apache Lucene.** Lucene provides the actual
search data structure and query execution on a single machine; Elasticsearch adds
sharding, replication, a REST API, and cluster coordination on top. Understanding this
split matters: many "Elasticsearch internals" questions are really "Lucene internals"
questions.

**The inverted index — the core idea.** A normal (forward) index maps document → words
it contains. An **inverted** index maps word → which documents contain it — the same
structure as a book's back-of-book index (which doesn't list "page 1: these topics,
page 2: these topics" — it lists "this topic: these pages," so you can jump straight to
the pages you actually care about). This is what makes "find all documents containing
'kafka'" fast: it's a direct lookup, not a scan of every document.

```
Forward index (what you'd naively build):
  doc1 -> ["kafka", "streaming", "platform"]
  doc2 -> ["kafka", "cluster", "broker"]

Inverted index (what Lucene actually builds):
  "kafka"     -> [doc1, doc2]
  "streaming" -> [doc1]
  "cluster"   -> [doc2]
  "broker"    -> [doc2]
```

**Index, document, mapping:**
```json
PUT /products
{
  "mappings": {
    "properties": {
      "name":  { "type": "text" },      // analyzed, tokenized, good for full-text search
      "sku":   { "type": "keyword" },   // exact match only, not tokenized
      "price": { "type": "float" }
    }
  }
}
```
A **mapping** is Elasticsearch's term for a schema — it declares each field's type and,
critically, *how that field should be treated for search*. `text` fields go through an
**analyzer** (tokenize into individual words + lowercase + stem, etc.) before being
written into the inverted index — this is what lets a search for "keyboard" match a
document containing "Keyboards" (plural, different case). `keyword` fields are stored
as-is, completely unanalyzed, used for exact matches, sorting, and aggregations —
searching a `keyword` field for "keyboard" will **not** match a stored value of
"Keyboards"; it has to match character-for-character.

## 3. How It Really Works (Internals)

Under the hood, Lucene doesn't maintain one giant mutable index — it writes immutable
**segments** (small self-contained inverted indexes), and periodically merges smaller
segments into larger ones in the background. A search is really "search every segment,
merge the results" — this is why indexing is fast (just write a new small segment) but
why too many small segments hurts search performance (more segments to fan out across).
This segment-merge design is the same conceptual family as an LSM-tree and, not
coincidentally, the same family as ClickHouse's MergeTree parts (Day 6 draws this
connection explicitly).

```
                    ┌──────────────────────────┐
                    │   Elasticsearch Index      │
                    │  ┌────────┐  ┌────────┐   │
                    │  │Segment1│  │Segment2│...│  ← each immutable, own inverted index
                    │  └────────┘  └────────┘   │
                    └──────────────────────────┘
                                 │
                     periodic background merge
```

## 4. Architecture & Design Pattern Spotlight

**Pattern: the inverted index.** It's the foundational pattern for every search engine
(Lucene/Elasticsearch, Solr, and conceptually even a database's full-text search
extension). Recognizing it here means you'll immediately understand *why* keyword
lookups are fast in any system that uses one, including outside search engines (e.g.,
a database's GIN index in Postgres is also an inverted index).

## 5. Hands-On Lab
```bash
# Docker
docker run -d --name es -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.14.0
```
```bash
curl -X PUT "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d '
{"name": "Wireless Mechanical Keyboard", "sku": "KB-001", "price": 79.99}'

curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d '
{"query": {"match": {"name": "keyboard"}}}'
```
Notice `match` on `name` (a `text` field) finds "keyboard" even though you searched a
different case/word form than stored — that's the analyzer at work. Try the same
search against `sku` with `term` instead of `match` and observe it requires an exact
match.

### Sample Output

The `PUT` (indexing the document) responds with:
```json
{
  "_index": "products",
  "_id": "1",
  "_version": 1,
  "result": "created",
  "_shards": { "total": 2, "successful": 1, "failed": 0 },
  "_seq_no": 0,
  "_primary_term": 1
}
```

The `_search` query responds with something shaped like this:
```json
{
  "took": 4,
  "timed_out": false,
  "_shards": { "total": 1, "successful": 1, "skipped": 0, "failed": 0 },
  "hits": {
    "total": { "value": 1, "relation": "eq" },
    "max_score": 0.9808291,
    "hits": [
      {
        "_index": "products",
        "_id": "1",
        "_score": 0.9808291,
        "_source": {
          "name": "Wireless Mechanical Keyboard",
          "sku": "KB-001",
          "price": 79.99
        }
      }
    ]
  }
}
```

Reading this piece by piece:
- **`result: "created"`** on the index response confirms the document was actually
  written — worth checking explicitly the first few times, since a malformed request
  can sometimes return a 200-level response with a different `result` value (like
  `"updated"` if a document with that ID already existed) rather than an obvious error.
- **`took: 4`** is milliseconds the search itself took on the server — this is search
  execution time only, not including network round-trip, and is the number worth
  watching if you're chasing query performance later (Week 3).
- **`hits.total.value: 1`** is how many documents matched, total — separate from how
  many are actually *returned* in the `hits.hits` array (which is capped, 10 by
  default, for pagination).
- **`_score: 0.9808291`** is the relevance score Lucene computed for how well this
  document matches your query (higher = more relevant) — the exact decimal value
  depends on term frequency, document length, and how rare the matched term is across
  the whole index (the full scoring formula, BM25, is Week 1 Day 3's topic) — don't
  worry about the specific digits, only that it's a real, comparable-across-results
  number, and that it exists *because* you used `match` (a scoring query), not `term`.
- If you re-run the second query using `term` against `sku` for the value `"keyboard"`
  (lowercase) instead of `"KB-001"`, you'd get back `hits.total.value: 0` — zero
  results — because `term` never analyzes/lowercases anything, and the stored `sku`
  value doesn't literally contain the substring you're matching against at all. This
  is the concrete, hands-on proof of the `text` vs. `keyword` distinction from the Core
  Concept section: same underlying document, two very differently-behaving fields.

## 6. Real-World Product Comparison

- **Wikipedia's CirrusSearch** is built on Elasticsearch, powering full-text search
  across all Wikipedia content at huge scale.
- **Uber** has historically used Elasticsearch heavily for log analytics and
  operational search across its microservices fleet.
- Contrast with **Algolia**: a fully-hosted, developer-first search API optimized for
  instant-as-you-type typo-tolerant search (product catalogs, docs sites) — you trade
  infrastructure control for near-zero ops burden and excellent default relevance
  tuning; Elasticsearch gives you far more control (and far more to operate) in return.

## 7. Common Production Pitfalls
- Mapping a field as `text` when you actually need exact-match/sorting/aggregation —
  you'll get surprising partial-match behavior. Use `keyword` (or both, via multi-fields,
  Day 2) for anything you filter or aggregate on exactly.
- Leaving the default mapping to be auto-inferred at first-write time for
  production data — inferred types are often wrong for your actual query patterns and
  are expensive to change later (usually requires reindexing).
- Treating "search" and "analytics" (aggregations) as needing separate systems when
  Elasticsearch was explicitly designed to do both — but see Week 4's honest comparison
  against ClickHouse for large aggregation-heavy dashboard workloads specifically.

## 8. Review Questions

1. What problem does an inverted index solve that a forward index doesn't?
<details><summary>Show answer</summary>

A forward index (document → words it contains) only helps if you already know which
document you want and need to know what's in it. It gives you no fast way to answer
"which documents contain the word X" — you'd have to scan every document's word list
one by one. An inverted index (word → documents containing it) makes that exact
query a direct lookup instead of a full scan, which is the whole point of a search
engine.

</details>

2. Why does Lucene write immutable segments instead of mutating one big index?
<details><summary>Show answer</summary>

Writing a brand-new small segment for each batch of new documents is fast and simple
— no need to find-and-update existing data structures in place, which would be slow
and complex to do safely, especially under concurrent reads. The trade-off is that a
search has to check every segment and merge the results, so Lucene periodically
merges smaller segments into larger ones in the background to keep the segment count
(and therefore search cost) manageable over time.

</details>

3. When would you choose `keyword` over `text` for a field, concretely?
<details><summary>Show answer</summary>

Whenever you need exact-match filtering, sorting, or aggregating on a field's exact
value — a SKU code, a status enum ("pending"/"shipped"), an email address, a
category ID. Anywhere you'd write `WHERE column = 'exact_value'` in SQL rather than a
fuzzy text search, `keyword` is the right choice; `text` is for genuinely free-form,
human-written content you want to search flexibly (titles, descriptions, comments).

</details>

4. Name one thing Algolia gives up in exchange for its hosted simplicity.
<details><summary>Show answer</summary>

Direct infrastructure control — with Algolia you can't tune the underlying cluster
topology, sharding strategy, or low-level scoring internals the way you can with a
self-hosted Elasticsearch cluster; you work within Algolia's own configuration
surface and pricing model instead. In exchange you get near-zero operational burden
and strong default relevance tuning for common use cases like e-commerce search.

</details>

## 9. Proficiency Checkpoint

**Quick Recap:**
- **Index** ≈ a table; **document** ≈ a row; **mapping** ≈ a schema, but critically
  also declares *how* each field is treated for search.
- **Inverted index**: word → list of documents containing it — the reason full-text
  lookups are fast (a direct lookup instead of scanning every document).
- **`text` fields**: analyzed (tokenized, lowercased, etc.) before indexing — good for
  flexible, fuzzy full-text search.
- **`keyword` fields**: stored exactly as-is, unanalyzed — required for exact-match
  filters, sorting, and aggregations.
- **Segments**: Lucene's immutable, append-only storage units, periodically merged in
  the background — same family as an LSM-tree, same family as ClickHouse's MergeTree.
- **`_score`**: a relevance number (higher = more relevant) that only scoring queries
  (like `match`) produce — `term` matches are exact, all-or-nothing, no fuzzy scoring.

If you can explain the inverted index well enough to predict which of two fields
(text vs. keyword) will support a given query type, you're at Level 2.

## Next
Day 2 goes deeper into analyzers (tokenizers + filters) and mapping design — the
foundation for both relevance tuning (Week 2) and correct aggregations.
