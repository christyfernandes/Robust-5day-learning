# Day 1: Elasticsearch — Search & Analytics Foundations

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain the **inverted index** concretely enough to predict why full-text search is
fast and why exact-match filtering on a keyword field is faster still, and perform
basic indexing/search operations.

## 2. Core Concept (basics → advanced)

**Elasticsearch is a distributed layer over Apache Lucene.** Lucene provides the actual
search data structure and query execution on a single machine; Elasticsearch adds
sharding, replication, a REST API, and cluster coordination on top. Understanding this
split matters: many "Elasticsearch internals" questions are really "Lucene internals"
questions.

**The inverted index — the core idea.** A normal (forward) index maps document → words
it contains. An **inverted** index maps word → which documents contain it — the same
structure as a book's back-of-book index. This is what makes "find all documents
containing 'kafka'" fast: it's a direct lookup, not a scan of every document.

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
`text` fields go through an **analyzer** (tokenize + lowercase + stem, etc.) before
being written into the inverted index; `keyword` fields are stored as-is, for exact
matches, sorting, and aggregations.

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
2. Why does Lucene write immutable segments instead of mutating one big index?
3. When would you choose `keyword` over `text` for a field, concretely?
4. Name one thing Algolia gives up in exchange for its hosted simplicity.

## 9. Proficiency Checkpoint
If you can explain the inverted index well enough to predict which of two fields
(text vs. keyword) will support a given query type, you're at Level 2.

## Next
Day 2 goes deeper into analyzers (tokenizers + filters) and mapping design — the
foundation for both relevance tuning (Week 2) and correct aggregations.
