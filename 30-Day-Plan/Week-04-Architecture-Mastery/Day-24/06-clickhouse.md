# Day 24: ClickHouse — When NOT to Use It

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Write the one sentence you'd say in a design review when someone proposes
ClickHouse for the wrong job.

## 2. Core Concept (basics → advanced)

ClickHouse's architecture — columnar, MergeTree-based, optimized for large
analytical scans (Week 1, Day 1) — is a poor fit for:
- **High-concurrency point lookups**: "give me this one row by primary key,
  very fast, thousands of times per second" is precisely the OLTP access
  pattern ClickHouse's sparse index (Week 1, Day 3) deliberately does *not*
  optimize for — a proper key-value store (Redis) or an OLTP database
  (Postgres) fits this pattern far better.
- **Frequent updates/deletes**: MergeTree's immutable-parts design (Week 1, Day
  1) means updates/deletes are comparatively expensive, asynchronous operations
  (not the instant, cheap row-level updates an OLTP database provides) —
  a workload with genuinely frequent per-row mutation is fighting ClickHouse's
  fundamental design.
- **Small datasets**: the operational overhead of running a ClickHouse cluster
  (Week 3's tuning, monitoring, security, backup lessons) is unjustified for
  data that would fit comfortably and perform perfectly well in a much simpler
  single-node database.

## 3. How It Really Works (Internals)

The correct mental test: **is this workload dominated by large scans and
aggregations over relatively static (or append-mostly) data, or by frequent
point lookups/updates on individual rows?** ClickHouse's entire architecture —
sparse index, MergeTree immutability, vectorized batch execution (Weeks 1-2) —
is a deliberate, coherent set of trade-offs optimized for the former; using it
for the latter fights every one of those design decisions simultaneously.

## 4. Architecture & Design Pattern Spotlight

**Pattern: matching tool architecture to actual access pattern — the OLAP-vs-
OLTP distinction is the most fundamental instance of this principle across the
entire curriculum**, and ClickHouse sits unambiguously on the OLAP side.

## 5. Hands-On Lab

Write the one sentence you'd say in a design review when someone proposes
ClickHouse as the primary store for a high-frequency, point-lookup-and-update
application workload.

## 6. Real-World Product Comparison

- **Druid and Pinot** are close ClickHouse competitors for real-time OLAP,
  each with different specific trade-offs (Druid's segment-based architecture,
  Pinot's real-time ingestion focus) — worth knowing they exist as alternatives
  within the same OLAP category, distinct from the OLTP-vs-OLAP question.
- **BigQuery and Snowflake** remain reasonable choices when the managed-
  service trade-off (Week 3, Day 20) outweighs self-hosting's control benefits
  for a given team's operational maturity and scale.

## 7. Common Production Pitfalls

- Using ClickHouse as a general-purpose application database, fighting its
  OLAP-optimized architecture for OLTP-shaped access patterns.
- Standing up a ClickHouse cluster (with all its Week 3 operational overhead)
  for a dataset small enough to run comfortably on a single-node database.

## 8. Review Questions
1. Why does ClickHouse's sparse index make point lookups a poor fit?
2. Why are frequent updates/deletes expensive under MergeTree's design?
3. What's your one-sentence design-review pushback?
4. What would make a workload genuinely need ClickHouse, versus Druid, Pinot,
   or a managed warehouse?

## 9. Proficiency Checkpoint
If you have a real, specific pushback ready and can name the OLTP-vs-OLAP
distinction as the deciding question, you're at Level 4.

## Next
Day 25 applies every "when NOT to use it" judgment from today directly to
designing your actual MDO portal migration.
