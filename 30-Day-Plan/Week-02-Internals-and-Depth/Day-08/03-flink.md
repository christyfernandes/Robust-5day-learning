# Day 8: Flink — Table API & SQL: Dynamic Tables

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Write a temporal join between an order stream and a point-in-time exchange-rate table
in Flink SQL, and explain what a "dynamic table" actually is.

## 2. Core Concept (basics → advanced)

Flink's Table API/SQL layer reframes an unbounded stream as a **dynamic table** — a
table that's continuously being modified by inserts, updates, and deletes as new
stream events arrive, conceptually identical to a regular SQL table except that it
never "finishes." Querying a dynamic table produces another dynamic table — the
result continuously updates as the input does, and can itself be converted back into a
**changelog stream** (a stream of insert/update/delete events representing the query
result's evolution over time).

```
DataStream API (Days 1-6):    explicit operators, explicit state — you write the "how"

Table API / SQL:              SELECT ... FROM orders o
                               JOIN rates FOR SYSTEM_TIME AS OF o.order_time r
                               ON o.currency = r.currency
                               (declarative "what," Flink figures out the "how" —
                                including which State backend/operator chain to use)
```

A **temporal join** specifically joins a stream against a *versioned* table as it
existed **at a specific point in time** — critically different from a normal stream-
stream join, because "exchange rate for USD" changes over time, and an order from
yesterday must join against yesterday's rate, not today's. `FOR SYSTEM_TIME AS OF` is
exactly this: "give me the version of this row as of the order's own timestamp."

## 3. How It Really Works (Internals)

Under the hood, Flink's Table API compiles down to the exact same DataStream
primitives you've been studying all week — keyed state, watermarks, operators — the
Table API is a higher-level abstraction *on top of*, not a replacement for, everything
from Days 1-7. A temporal join specifically requires keeping historical versions of
the "right side" table (the rates table) in state, keyed and timestamped, so a lookup
for "the rate as of time T" can find the correct historical version rather than just
the current one — this is meaningfully more state to manage than a simple current-value
lookup join, and is exactly the kind of query the DataStream API alone would require
substantial custom state-management code to implement correctly.

## 4. Architecture & Design Pattern Spotlight

**Pattern: dynamic tables over unbounded streams — declarative processing built on
the same primitives as the imperative API underneath.** This mirrors exactly how
Spark's DataFrame API (Days 1-2) sits on top of RDDs, and how ClickHouse's SQL sits on
top of its columnar storage engine — a recurring shape across this whole curriculum:
declarative surface, imperative/mechanical foundation underneath, with the framework
doing the translation.

## 5. Hands-On Lab

```sql
CREATE TABLE orders (
    order_id STRING, currency STRING, amount DOUBLE, order_time TIMESTAMP(3),
    WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
) WITH (...);

CREATE TABLE rates (
    currency STRING, rate DOUBLE, rate_time TIMESTAMP(3),
    WATERMARK FOR rate_time AS rate_time - INTERVAL '5' SECOND,
    PRIMARY KEY (currency) NOT ENFORCED
) WITH ('connector' = 'upsert-kafka', ...);

SELECT o.order_id, o.amount * r.rate AS amount_usd
FROM orders o
JOIN rates FOR SYSTEM_TIME AS OF o.order_time AS r
ON o.currency = r.currency;
```
Feed in rate changes over time and orders with timestamps spanning those changes —
verify each order joins against the rate that was actually in effect at its own
timestamp, not whatever the latest rate happens to be by the time the join executes.

## 6. Real-World Product Comparison

- Flink's Table API/SQL is the direct SQL-first equivalent of **Kafka Streams' KTable**
  model (Day 8's Kafka lesson) — both represent "latest state as of now" as a table
  view over an event stream, with Flink additionally supporting genuine temporal
  (point-in-time) semantics natively in SQL.
- Financial and pricing systems (common in ride-sharing/fintech, similar to Uber's
  pricing pipeline) rely heavily on temporal joins specifically because "which rate was
  in effect" is a correctness requirement, not a nice-to-have.

## 7. Common Production Pitfalls

- Using a regular (non-temporal) join when the "right side" table changes over time —
  silently joins against whatever the *current* value happens to be at execution time,
  producing incorrect historical results.
- Underestimating the state size required for temporal joins — Flink must retain
  enough historical versions of the right-side table to correctly answer joins for
  events arriving within your allowed lateness window.
- Mixing Table API and DataStream API without understanding the conversion boundary —
  going back and forth (`toDataStream`/`fromDataStream`) has real implications for
  watermark and changelog semantics that are easy to get subtly wrong.

## 8. Review Questions
1. What makes a table "dynamic," and how does it relate to a changelog stream?
2. Why does a temporal join need historical versions of the right-side table, not just
   the current value?
3. How does the Table API relate to the DataStream API underneath it?
4. Why would a regular join produce systematically wrong results for a
   changes-over-time dimension table?

## 9. Proficiency Checkpoint
If you can write a correct temporal join and explain why a non-temporal join would be
wrong for the same use case, you're at Level 3.

## Next
Day 9 covers Flink's exactly-once sink connectors — the two-phase-commit mechanism
that makes durable, non-duplicated output possible.
