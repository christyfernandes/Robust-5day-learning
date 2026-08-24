# Day 10: Architecture — CQRS in Depth

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Sketch a CQRS design for a feature where reads and writes have very different scaling
needs, and explain how Elasticsearch-as-read-model, fed by Kafka, embodies the pattern.

## 2. Core Concept (basics → advanced)

**CQRS (Command Query Responsibility Segregation)** separates the model used for
*writes* (commands — "place an order," "update a profile") from the model used for
*reads* (queries — "show me this user's order history," "search products by
category"). In a traditional CRUD architecture, one schema serves both, forcing
compromises (a schema optimized for transactional writes is rarely also optimal for
flexible, fast reads, and vice versa). CQRS accepts running **two separate models**,
kept in sync, each optimized for its own job.

```
Traditional (single model):        CQRS (separated models):

  App ──▶ [one DB schema] ◄── App    Write side:  App ──▶ [normalized write DB]
   (reads AND writes,                                          │
    one compromise schema)                                     ▼ events
                                                          [Kafka / event log]
                                                                 │
                                                                 ▼
                                    Read side:   App ◄── [denormalized read model]
                                                  (e.g., Elasticsearch, a
                                                   materialized view, a cache —
                                                   optimized PURELY for query speed)
```

## 3. How It Really Works (Internals)

The write side stays authoritative and typically normalized (or otherwise optimized
for correctness and transactional integrity); every write emits an event (this is
where event-carried state transfer, Day 9's Architecture lesson, typically shows up),
and a separate process consumes those events to build and continuously update one or
more **read-model projections** — each shaped exactly for a specific query pattern,
with no obligation to be "the same shape" as the write model at all. This is precisely
why **Elasticsearch, fed by a Kafka topic of change events, is a canonical CQRS read
model**: the write-side database stays clean and normalized; Elasticsearch holds a
denormalized, search-optimized projection built purely for fast, flexible querying,
kept eventually consistent with the write side via the event stream.

The unavoidable cost: **eventual consistency between the write model and every read
model** — a write is immediately durable on the write side, but the read-model
projection updates asynchronously, meaning a user could theoretically query
immediately after writing and see stale data for a brief window. This is a design
trade-off to make consciously (does this specific read *need* to be immediately
consistent, or is a brief lag acceptable?), not an accident to be surprised by.

## 4. Architecture & Design Pattern Spotlight

**Pattern: read/write model separation, with events as the synchronization
mechanism.** This ties together three tracks studied this month into one coherent
picture: a normalized write-side database, Kafka as the event backbone (Day 9), and
Elasticsearch (or a ClickHouse Materialized View, Week 1 Day 6) as a purpose-built read
model. Recognizing this composition — rather than three unrelated technology choices
— is exactly the kind of cross-track synthesis this curriculum is building toward, and
it directly describes the shape of systems you already operate (Sunbird's Kafka →
Druid pipeline is architecturally CQRS, whether or not it's been labeled that way).

## 5. Hands-On Lab

Sketch a CQRS design for a feature with genuinely different read/write scaling needs —
e.g., a product catalog where writes are infrequent (a few updates per hour from an
admin tool) but reads are extremely high-volume and need flexible filtering (a
consumer-facing search/browse experience). For your sketch, specify:
- What does the write-side schema look like, and what event does each write emit?
- What read-model(s) do you build, and in what storage (Elasticsearch? a cache?
  multiple different projections for different query shapes)?
- What's your acceptable staleness window for each read model, and would any specific
  query in this feature actually require strong consistency (in which case, should it
  bypass the read model and query the write side directly)?

## 6. Real-World Product Comparison

- **E-commerce platforms** almost universally use some form of this pattern: a
  transactional order/inventory system as the write side, and a search/catalog
  service (often Elasticsearch or a similar engine) as a purpose-built read model —
  exactly the shape you sketched above.
- Your own **Sunbird telemetry pipeline** (Flink → Kafka → Redis/Druid) is
  architecturally CQRS-shaped: raw events are the "write" side (append-only, source of
  truth), and Druid's aggregated views are read-model projections purpose-built for
  fast analytical queries — worth explicitly recognizing this the next time you
  document or extend that pipeline.

## 7. Common Production Pitfalls

- Adopting CQRS for a feature where read and write patterns are actually similar
  enough that the added complexity (two models, an event pipeline, eventual
  consistency to reason about) isn't worth the benefit — CQRS is a trade, not a
  default.
- Not clearly documenting each read model's staleness guarantee — teams downstream
  building on a read model need to know explicitly whether it's "usually a few seconds
  behind" or "usually a few minutes behind," since that shapes what they can safely
  build on top of it.
- Allowing the read model's shape to silently drift out of alignment with what the
  event stream actually provides — if the write side changes its event schema without
  updating every read-model consumer, projections silently become incomplete or stale
  in ways that are hard to detect without careful monitoring of projection lag.

## 8. Review Questions
1. What's the core trade CQRS makes, and when is that trade *not* worth it?
2. Why is Elasticsearch, fed by Kafka, a canonical CQRS read model?
3. What does "eventual consistency between write and read models" actually mean for a
   real user-facing feature?
4. How is your own Sunbird pipeline already CQRS-shaped, whether or not it's been
   called that?

## 9. Proficiency Checkpoint
If you can design a CQRS read/write split for a stated feature and correctly identify
its staleness trade-offs, you're at Level 3 — and you now have vocabulary for
architecture you already operate.

## Next
Day 11 covers Adaptive Query Execution, performance tuning, caching patterns, ILM,
dictionaries, and Lambda/Kappa architectures — Week 2's transition from "internals"
into "production tuning."
