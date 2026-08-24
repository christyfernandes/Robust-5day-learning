# Day 22: Elasticsearch — Design Patterns: CQRS Read-Model & Search Facade

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Sketch a full CQRS design with Kafka as the write path and Elasticsearch as the
read model, tying together three tracks studied across this curriculum.

## 2. Core Concept (basics → advanced)

Week 2, Day 10 introduced CQRS conceptually, naming Elasticsearch-fed-by-Kafka as
a canonical example. Today, design it concretely: a write-side service commits
changes to its own store (normalized, transactional) and emits an event to Kafka
(Transactional Outbox, Week 1 Day 5, for reliable event emission); a consumer
(potentially the Kafka table engine pattern, Week 2 Day 13, adapted, or a
dedicated Flink/Connect job) transforms and indexes those events into
Elasticsearch, which serves as the purpose-built **read model** for search and
faceted-filtering use cases the write-side store isn't optimized for.

A **search-as-a-service facade** is the complementary application-layer pattern:
expose a clean, stable search API to consumers, with Elasticsearch (or whichever
engine actually backs it) as an implementation detail behind that facade —
allowing the backing search engine to be swapped (e.g., ES to OpenSearch, Day 20;
or even ES to ClickHouse for some query shapes, Day 24's "when NOT to use it"
lesson) without every consumer needing to change.

## 3. How It Really Works (Internals)

The design decisions that actually matter here: **what's the staleness tolerance**
for this specific read model (Week 2, Day 10's CQRS lesson) — does the event
pipeline from write-side commit to ES-searchable document need to complete in
milliseconds, seconds, or is a few-second lag acceptable? And **what happens on
reindex** — since ES documents are effectively rebuilt from source events
(Week 1, Day 6's segment immutability meaning updates are delete+reinsert), a
full ES schema change requires either a live reindex-in-place or building a new
index and cutting over (the rollover-alias pattern from Week 2, Day 11's ILM
lesson) — this needs to be designed for from the start, not discovered as a
surprise during the first schema change.

## 4. Architecture & Design Pattern Spotlight

**Pattern: read/write model separation, applied concretely — synthesizing Kafka
(the event backbone, Day 22's Kafka lesson), the Outbox pattern (Week 1, Day 5),
and Elasticsearch (the read model) into one coherent design**, exactly the
cross-track synthesis this Week 4 is meant to build.

## 5. Hands-On Lab

Sketch a full CQRS design for a real or realistic feature (a product catalog with
faceted search is a good default): the write-side schema and its Outbox-based
event emission, the Kafka topic(s) involved, the transformation/indexing process
into Elasticsearch, and the search-facade API layer that shields consumers from
the ES implementation detail. Explicitly state your staleness tolerance and your
reindex/schema-evolution strategy.

## 6. Real-World Product Comparison

- **E-commerce platforms** (referenced in Week 2, Day 10's CQRS lesson) are the
  canonical real-world instance of exactly this design — a transactional
  inventory/catalog system as the write side, Elasticsearch as the searchable,
  facet-filterable read model.
- A **search-as-a-service facade** is standard practice at any organization
  large enough to have swapped search backends at least once — the facade layer
  is precisely what made that swap possible without a full consumer-side rewrite.

## 7. Common Production Pitfalls

- Not designing for reindex/schema-evolution from the start, discovering only
  during the first required schema change that there's no clean migration path.
- Exposing Elasticsearch's query DSL directly to consumers instead of a stable
  facade API, coupling every consumer to ES-specific query syntax and making a
  future backend swap much harder.
- Not setting an explicit staleness tolerance, leaving "how fresh should search
  results be" as an undocumented assumption different teams might interpret
  differently.

## 8. Review Questions
1. How does the Outbox pattern (Week 1, Day 5) fit into this CQRS design
   specifically?
2. Why does ES's document immutability (Week 1, Day 6) make schema evolution a
   design concern from the start, not an afterthought?
3. What does a search-as-a-service facade protect consumers from?
4. What's your own real feature's actual staleness tolerance, and does your
   design meet it?

## 9. Proficiency Checkpoint
If you can design a complete, concrete CQRS system spanning three tracks studied
this month, you're at Level 4.

## Next
Day 23 covers Elasticsearch case studies — GitHub's historical code search, Uber
logging, Wikipedia's CirrusSearch.
