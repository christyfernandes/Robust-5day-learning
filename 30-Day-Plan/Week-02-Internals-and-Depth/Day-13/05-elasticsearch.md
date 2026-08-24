# Day 13: Elasticsearch — Vector Search & kNN

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Index documents with a `dense_vector` field, run a `knn` query, and explain how
approximate nearest-neighbor search differs fundamentally from BM25 keyword matching.

## 2. Core Concept (basics → advanced)

Everything studied about Elasticsearch so far (Week 1, Day 3's BM25) matches based on
**exact or fuzzy term overlap** — "wireless headphones" matches documents containing
those words. **Vector search** matches based on **semantic similarity** instead: text
(or images, or other content) is converted into a dense numeric vector (an
"embedding," produced by a machine learning model) that captures meaning, and a search
query is itself converted into a vector, with results ranked by vector similarity
(commonly cosine similarity or Euclidean distance) — meaning a search for "affordable
laptop" can match a document about a "budget-friendly notebook computer" even though
they share almost no literal words in common.

```
BM25 (Week 1, Day 3):     "wireless headphones" ──▶ matches documents
                           containing those literal terms (with stemming/synonyms
                           handled by the analyzer, but fundamentally term-based)

kNN / vector search:       "affordable laptop" ──▶ embedded as a vector ──▶
                           finds documents whose embeddings are numerically
                           CLOSE in vector space, regardless of shared words
```

## 3. How It Really Works (Internals)

Finding the exact nearest neighbors among millions of high-dimensional vectors via
brute-force comparison would be far too slow for real-time search — Elasticsearch
uses **HNSW (Hierarchical Navigable Small World)** graphs, an approximate
nearest-neighbor algorithm: vectors are organized into a multi-layer graph structure
where each vector is connected to a small number of "nearby" vectors, and search
navigates this graph greedily from a coarse upper layer down to a fine-grained bottom
layer, finding a very good (but not always exactly optimal) approximation of the true
nearest neighbors, in a small fraction of the time brute-force comparison would take.

This is the same **approximate algorithm trading precision for speed** trade-off
you've now seen repeatedly this month (HyperLogLog's cardinality estimation, Week 1
Day 6; Redis's approximate LRU sampling, Week 1 Day 6) — HNSW accepts a small,
tunable chance of missing the absolute-best match in exchange for search speed that
scales to realistic production vector-search workloads.

## 4. Architecture & Design Pattern Spotlight

**Pattern: approximate nearest-neighbor search — the vector-space instance of the
"approximate over exact for speed" pattern recurring across this curriculum.** Modern
semantic search use cases (recommendation systems, "find similar" features,
retrieval-augmented generation pipelines) rely on exactly this mechanism, and
recognizing HNSW as one more instance of a familiar trade-off (rather than an entirely
foreign new concept) should make it feel more approachable than "AI search" marketing
language often makes it sound.

## 5. Hands-On Lab

```json
PUT /products_vec
{ "mappings": { "properties": {
    "title": { "type": "text" },
    "title_vector": { "type": "dense_vector", "dims": 4, "index": true, "similarity": "cosine" }
}}}

POST /products_vec/_doc
{ "title": "budget-friendly notebook computer", "title_vector": [0.12, 0.85, -0.3, 0.44] }

POST /products_vec/_doc
{ "title": "premium leather office chair", "title_vector": [-0.9, 0.1, 0.75, -0.2] }

GET /products_vec/_search
{ "knn": {
    "field": "title_vector",
    "query_vector": [0.15, 0.80, -0.28, 0.40],
    "k": 5, "num_candidates": 50
}}
```
(In practice, vectors come from an embedding model rather than being hand-written —
today's lab uses small hand-crafted vectors purely to make the mechanics visible.)
Confirm the "notebook computer" document ranks first, being numerically closer to the
query vector, despite the query sharing no literal words with either document's title.

## 6. Real-World Product Comparison

- Modern **semantic search and recommendation systems** (product discovery, content
  recommendation) increasingly combine vector search with traditional BM25 (a
  **hybrid search** approach) — using keyword matching for precision on exact terms
  and vector similarity for semantic recall, rather than choosing one exclusively.
- **Dedicated vector databases** (a distinct category of system entirely, e.g.
  purpose-built for large-scale embedding search) compete directly with
  Elasticsearch's built-in vector search for workloads where vector search is the
  *primary*, not supplementary, access pattern — worth knowing this category exists
  even outside Elasticsearch's own implementation.

## 7. Common Production Pitfalls

- Using vector search alone for a use case where exact keyword matching genuinely
  matters (e.g., an exact product SKU or code lookup) — semantic similarity can
  actively hurt precision for these queries; hybrid search or query-type routing is
  usually the right answer.
- Not tuning `num_candidates` appropriately — too low, and HNSW's approximation
  quality suffers meaningfully; too high, and query latency increases without
  proportional benefit.
- Treating embedding quality as a given — vector search result quality is entirely
  bounded by how good the underlying embedding model is at capturing genuine semantic
  similarity for your specific domain; a poor embedding model produces poor search
  regardless of how well-tuned HNSW is.

## 8. Review Questions
1. What's the fundamental difference between what BM25 and vector search each match
   on?
2. Why is exact nearest-neighbor search too slow for realistic production use, and
   what does HNSW trade to solve that?
3. When would hybrid search (BM25 + vector) outperform either approach alone?
4. What determines vector search result quality, independent of the search algorithm
   itself?

## 9. Proficiency Checkpoint
If you can correctly decide when vector search, keyword search, or hybrid search fits
a given use case, and explain HNSW's approximate trade-off, you're at Level 3.

## Next
Day 14 is this week's integrated lab and review, applying everything from Week 2
directly to your real production systems.
