# Day 12: Architecture — Data Mesh vs. Data Lake vs. Lakehouse vs. Data Warehouse

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Classify your team's current setup and your target setup using this framework — a
direct application to your BigQuery-to-ClickHouse shift.

## 2. Core Concept (basics → advanced)

Four architectural philosophies for organizing an organization's analytical data, often
conflated but genuinely distinct:

- **Data warehouse**: structured, schema-on-write, typically SQL-first (BigQuery,
  Snowflake) — optimized for reliable, governed business intelligence and reporting,
  historically at the cost of flexibility for less-structured or exploratory data.
- **Data lake**: raw, schema-on-read storage (commonly files in object storage —
  S3/GCS, in formats like Parquet) — maximally flexible, but historically lacking the
  transactional guarantees and query performance a warehouse provides.
- **Lakehouse**: applies warehouse-like features (ACID transactions, schema
  enforcement, time travel — via Delta Lake/Iceberg/Hudi, Day 13) *on top of* lake-style
  cheap object storage — an attempt to get the flexibility/cost profile of a lake with
  much of the reliability of a warehouse.
- **Data mesh**: a fundamentally different, *organizational* (not purely technical)
  philosophy — rather than one central team owning "the data platform," individual
  domain teams own their own data as a product, with federated governance standards
  ensuring interoperability across teams' independently-owned data.

```
Warehouse:   structured, governed, SQL-first        (BigQuery, Snowflake)
Lake:        raw, flexible, schema-on-read           (S3/GCS + Parquet files)
Lakehouse:   lake storage + warehouse-like guarantees (Delta/Iceberg/Hudi on object storage)
Data mesh:   ORGANIZATIONAL model — domain-owned data products, federated governance
             (can be built using warehouse, lake, OR lakehouse technology underneath)
```

## 3. How It Really Works (Internals)

The critical distinction to hold clearly: **warehouse/lake/lakehouse are technology
architecture choices; data mesh is an organizational/governance philosophy that sits
above (and is largely independent of) that technology choice.** A data mesh can be
implemented with a lakehouse underneath, or with per-domain warehouses, or with a mix —
the mesh philosophy is about *who owns and is accountable for* a given dataset's
quality and interface, not which storage engine holds the bytes. Conflating these
(treating "data mesh" as a technology to adopt rather than an organizational model to
adopt) is a common, consequential misunderstanding.

Your own **BigQuery → ClickHouse** shift is a warehouse-to-(potentially)-lakehouse-
adjacent technology decision — ClickHouse itself is closer to a warehouse in query
experience (structured, SQL-first, strong performance) but increasingly incorporates
lakehouse-adjacent capabilities (Iceberg/Delta table reading support in modern
versions) — worth being precise about which axis (technology vs. organizational
model) any given part of this migration conversation is actually addressing.

## 4. Architecture & Design Pattern Spotlight

**Pattern: separating the technology-architecture question (warehouse/lake/
lakehouse) from the organizational-governance question (centralized platform team vs.
data mesh) — two genuinely independent axes that get conflated constantly in industry
discourse.** Being able to cleanly separate these when discussing your own migration
avoids a common failure mode: debating "should we adopt a data mesh" when the actual
question on the table is "which storage/query engine should we use," or vice versa.

## 5. Hands-On Lab

Classify your team's setup along both axes explicitly:
- **Technology axis**: is your current BigQuery-centric setup warehouse, lake, or
  lakehouse-shaped? Is your target ClickHouse-based setup warehouse, lake, or
  lakehouse-shaped — and where does it sit if it incorporates Iceberg/Parquet reading
  alongside native MergeTree tables?
- **Organizational axis**: is data ownership currently centralized (one data
  engineering team owns everything) or federated (domain teams own their own data
  products)? Is this migration an opportunity (or a risk) to shift that organizational
  model, independent of the technology decision?

Write one paragraph distinguishing which parts of your migration conversation are
genuinely technology decisions versus genuinely organizational decisions.

## 6. Real-World Product Comparison

- **Databricks** popularized "lakehouse" specifically as a marketing and technical
  term for Delta Lake's approach — warehouse guarantees on lake-cheap storage — a
  genuinely useful technical innovation, independent of any organizational model.
- **Data mesh** (the term, from Zhamak Dehghani) is explicitly an organizational
  proposal, not a technology — many "data mesh" implementations in practice use
  entirely conventional warehouse or lakehouse technology underneath, just with
  different ownership and governance structures layered on top.

## 7. Common Production Pitfalls

- Treating "should we adopt a lakehouse" and "should we adopt a data mesh" as the
  same decision, when they're answerable independently and often should be.
- Adopting lakehouse technology without the governance/quality practices a warehouse
  historically enforced by default (schema-on-write, data quality checks) — the
  flexibility lakehouses offer can become a liability without deliberately
  reintroducing that discipline.
- Assuming a technology migration (BigQuery to ClickHouse) automatically implies or
  requires an organizational change — it doesn't; keep the two conversations
  explicitly separate in stakeholder discussions.

## 8. Review Questions
1. Why is data mesh fundamentally different in kind from warehouse/lake/lakehouse?
2. Where does a lakehouse sit relative to a pure warehouse and a pure lake, and why?
3. Why is it a mistake to conflate a technology migration with an organizational
   governance change?
4. How would you classify your own team's current and target setups along both axes?

## 9. Proficiency Checkpoint
If you can cleanly separate the technology and organizational questions in your own
migration conversation and classify your setup correctly along both axes, you're at
Level 3 — directly useful for framing stakeholder discussions this week.

## Next
Day 13 covers the lakehouse formats in depth (Delta/Iceberg/Hudi) and resilience
patterns (circuit breaker, bulkhead, retry) — completing Week 2's internals-and-depth
arc before Day 14's integrated lab.
