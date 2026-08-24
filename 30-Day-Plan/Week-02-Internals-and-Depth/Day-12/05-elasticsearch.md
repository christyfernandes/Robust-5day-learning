# Day 12: Elasticsearch — Percolator & Reverse Search

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Register a percolator query, index a document, and confirm it matches — and explain
why this is "search inverted."

## 2. Core Concept (basics → advanced)

Ordinary search is: "I have a query, find matching documents from an existing index."
**Percolator** inverts this entirely: "I have a **document** (often one that just
arrived, in real time), find which of many pre-registered **queries** it matches" —
useful for alerting/monitoring use cases (saved search alerts, content-matching rules)
where you want to know, for each new incoming item, which of potentially thousands of
standing interest-criteria it satisfies.

```
Normal search:      1 query ──▶ matched against MANY stored documents

Percolator:         1 new document ──▶ matched against MANY stored QUERIES
                     (e.g., "does this new article match any of my
                      saved search alerts?" — evaluated the instant
                      the article arrives, not by re-running every
                      saved search periodically against the whole index)
```

## 3. How It Really Works (Internals)

A percolator query is stored as a specially-mapped field (`percolator` type) inside a
regular document — internally, Elasticsearch actually indexes registered queries
themselves using extracted terms (a technique that lets it efficiently narrow down
"which registered queries could *possibly* match this document" before doing exact
evaluation), rather than naively evaluating every single registered query against
every incoming document, which wouldn't scale past a small number of registered
queries. This is conceptually similar to how a spam filter or content-classification
system with thousands of rules avoids evaluating every rule against every message —
some form of pre-filtering narrows the candidate set before exact matching.

## 4. Architecture & Design Pattern Spotlight

**Pattern: "store the query, match incoming data against it" — inverted search, the
foundational pattern behind saved-search alerting and real-time content-matching
systems generally.** This pattern shows up conceptually anywhere a system needs
"notify me when new data matches my criteria" rather than "let me search existing
data" — a genuinely different indexing/matching direction worth recognizing as its
own named pattern, distinct from everything else studied this month.

## 5. Hands-On Lab

```json
PUT /alerts
{ "mappings": { "properties": {
    "query": { "type": "percolator" },
    "title": { "type": "text" }
}}}

POST /alerts/_doc/alert1
{ "query": { "match": { "title": "clickhouse" } } }

POST /alerts/_search
{ "query": { "percolate": {
    "field": "query",
    "document": { "title": "our clickhouse migration is going well" }
}}}
```
Confirm the search returns `alert1` as a match — this new document is being tested
against the *stored query*, the reverse of every search you've written so far this
month. Register a second alert query for a different term and confirm a document
matching neither, one, or both alerts behaves correctly.

## 6. Real-World Product Comparison

- **Saved-search alerting features** (news aggregators, job-listing alert emails,
  brand-monitoring tools) are the canonical percolator use case — "notify me the
  instant something matching my saved criteria appears" is exactly this pattern.
- **Content-moderation and compliance-monitoring systems** at scale often use a
  similar inverted-matching architecture (thousands of standing rules, evaluated
  against each new piece of content in real time) — whether or not they use
  Elasticsearch specifically, the percolator pattern is the right mental model for
  this class of system.

## 7. Common Production Pitfalls

- Naively evaluating every registered query against every document in application
  code (instead of using percolator's optimized matching) once the number of
  registered queries grows past a small number — this doesn't scale linearly the way
  percolator's internal optimization does.
- Not monitoring how many registered queries exist over time — an unbounded, ever-
  growing set of saved alerts/rules has real performance implications worth tracking.
- Treating percolator as a replacement for normal search rather than recognizing it
  solves a genuinely different problem — the two are complementary, not substitutes.

## 8. Review Questions
1. What's inverted about percolator compared to normal search?
2. Why doesn't Elasticsearch naively evaluate every registered query against every
   document?
3. Name a real-world use case where percolator's matching direction is exactly what's
   needed.
4. Why is this a genuinely different pattern from anything else covered this month,
   rather than a variant of normal search?

## 9. Proficiency Checkpoint
If you can correctly identify when a problem needs percolator's inverted matching
(rather than normal search) and implement it, you're at Level 3.

## Next
Day 13 covers vector search and kNN — a very different kind of "search," based on
semantic similarity rather than exact/fuzzy term matching.
