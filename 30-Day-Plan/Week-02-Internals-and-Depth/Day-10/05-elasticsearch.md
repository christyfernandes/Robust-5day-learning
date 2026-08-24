# Day 10: Elasticsearch — Data Modeling: Nested vs. Object vs. Parent-Child

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Model the same one-to-many relationship three different ways, and compare query
complexity and index size trade-offs.

## 2. Core Concept (basics → advanced)

Elasticsearch documents are fundamentally flat, JSON-like structures — but real data
often has one-to-many relationships (a product with multiple reviews, an order with
multiple line items), and Elasticsearch offers three distinct ways to model this, with
real trade-offs:

- **Object (plain nested JSON)**: the simplest — an array of sub-objects stored
  directly in the parent document. Internally, Lucene *flattens* this: `reviews:
  [{author: "A", rating: 5}, {author: "B", rating: 1}]` becomes `reviews.author:
  ["A","B"]` and `reviews.rating: [5,1]` as separate flattened arrays — losing the
  *association* between a specific author and their specific rating. A query for
  "reviews where author=A AND rating=1" would incorrectly match this document, since it
  only checks that *both* values appear somewhere in the flattened arrays, not that they
  came from the same sub-object.
- **Nested type**: solves exactly that problem — each sub-object is indexed as a
  hidden, *separate* Lucene document, preserving the object-level association, queryable
  via a special `nested` query that correctly scopes the match to one sub-object at a
  time. Correct, but nested queries are more expensive, and updating *any* nested
  sub-object requires reindexing the *entire* parent document (Lucene's segments are
  immutable — Week 1, Day 6).
- **Parent-child (`join` field)**: parent and child are indexed as **entirely separate
  documents** (not sub-documents within one), linked via a join field — children can be
  added, updated, or deleted independently without touching the parent document at all.
  More flexible for frequently-changing relationships, but joins at query time are
  markedly more expensive than nested queries.

```
Object:        one Lucene doc, flattened arrays — WRONG for correlated sub-field queries
Nested:        one Lucene doc + hidden separate docs per sub-object — CORRECT, costlier query
Parent-child:  fully separate documents, joined at query time — most flexible, costliest query
```

## 3. How It Really Works (Internals)

The object-type flattening problem is the single most common "why is my search
returning wrong results" bug in Elasticsearch schema design — it's not an error, the
query executes and returns a plausible-looking (wrong) result, structurally similar in
spirit to the fan-out problem you studied in ClickHouse (Week 2, Day 9): a
syntactically valid operation producing an incorrect answer because an implicit
assumption about structure/cardinality didn't hold.

Nested documents trade update cost for query correctness and reasonable query
performance (since nested docs still live physically close to their parent, in the
same Lucene segment) — parent-child trades query cost for update flexibility (since
child documents are fully independent and can be modified without touching the parent
at all, useful when children change far more often than parents, e.g., comments on a
rarely-changing blog post).

## 4. Architecture & Design Pattern Spotlight

**Pattern: denormalization trade-offs — the same "correctness vs. update cost vs.
query cost" triangle that every data-modeling decision this month has involved.**
Choosing object/nested/parent-child is structurally the same kind of decision as
choosing ClickHouse's denormalize-and-avoid-joins philosophy (Week 1) vs. a normalized
schema — there's no universally correct answer, only a correct answer *for a specific,
stated access pattern*.

## 5. Hands-On Lab

Model a `product` with multiple `reviews` (`{author, rating}`) three ways in test
indices, insert the same data into each, then run the query "find products with a
review by 'alice' rated 1 star" against all three:
```json
// nested query (correct for the "nested" mapping)
{ "query": { "nested": {
    "path": "reviews",
    "query": { "bool": { "must": [
        { "match": { "reviews.author": "alice" } },
        { "match": { "reviews.rating": 1 } }
    ]}}
}}}
```
Run the equivalent flat `bool` query against the plain-object mapping and confirm it
incorrectly matches a product where "alice" and a 1-star rating exist in *different*
reviews — this is the flattening bug made concrete.

## 6. Real-World Product Comparison

- E-commerce platforms with product reviews almost universally use **nested** type for
  exactly this reason — reviews change occasionally, but correctness of
  "author+rating" correlation matters for filtered search.
- **Parent-child** is common for use cases like comment threads on frequently-updated
  content (news sites, forums) where children are added/removed far more often than the
  parent document itself changes, making per-review reindexing of the whole parent
  document (nested's cost) unacceptable.

## 7. Common Production Pitfalls

- Using the default object mapping for genuinely one-to-many data without realizing
  Lucene flattens it, then being surprised by incorrect query results under
  multi-field, multi-value filtering.
- Choosing nested type for data that changes very frequently at the sub-document
  level — full parent-document reindexing on every child update can become a real
  indexing throughput bottleneck.
- Choosing parent-child by default "for flexibility" without needing it — the query-time
  join cost is a real, ongoing tax paid on every relevant search, not a one-time cost.

## 8. Review Questions
1. Why does the plain object mapping silently break correlated multi-field queries on
   sub-documents?
2. What does nested type cost on update, and why?
3. What does parent-child cost on query, and why is that an acceptable trade for some
   use cases?
4. How is this the same underlying trade-off class as ClickHouse's denormalization
   philosophy?

## 9. Proficiency Checkpoint
If you can choose the right modeling approach for a stated access-and-update pattern,
and explain precisely why the naive object mapping would produce wrong results, you're
at Level 3.

## Next
Day 11 covers Index Lifecycle Management — hot-warm-cold-frozen tiering, the direct
cross-link to yesterday's ClickHouse storage-policy lesson.
