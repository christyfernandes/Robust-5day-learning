# Day 8: Kafka Streams & ksqlDB — Stream-Table Duality

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Build a running word-count as a KTable using Kafka Streams' DSL, and explain the
stream-table duality that makes it work.

## 2. Core Concept (basics → advanced)

**Kafka Streams** is a client library (not a separate cluster to operate — it embeds
directly in your application) for building stream-processing applications on top of
Kafka. Its core abstraction rests on a genuinely elegant idea: **stream-table
duality** — a **KStream** (an unbounded sequence of independent records) and a
**KTable** (a materialized, continuously-updated view of "latest value per key") are
two views of the *same underlying data*. Every KTable update is really just another
record on the stream (its **changelog**); every stream can be interpreted as a table if
you only care about the latest value per key.

```
KStream (record-at-a-time):    "user1: login"  "user1: click"  "user1: logout"
                                (three independent events)

KTable (latest-value-per-key):  user1 → "logout"   (only the LATEST value matters,
                                                      older events for the same key
                                                      are conceptually superseded)

Same Kafka topic, two different interpretations depending on what you need.
```

**ksqlDB** offers the same underlying stream-table model but as a SQL-like managed
service with its own cluster, rather than an embedded library — a genuine deployment
trade-off: Kafka Streams runs *inside* your application (no separate infrastructure,
but you own scaling/deployment as part of your app), while ksqlDB is a separately
operated service (its own scaling/ops story, but a SQL interface accessible to anyone,
not just your application's own code).

## 3. How It Really Works (Internals)

A KTable is physically backed by a **changelog topic** — every update to the table is
appended as a new record, and Kafka Streams maintains a local, embedded state store
(RocksDB, by default — the same storage engine from Day 5's Flink state lesson) that's
kept in sync with this changelog. On failure/restart, Kafka Streams can rebuild the
local state store entirely by replaying the changelog topic from the beginning — the
changelog topic *is* the durable source of truth; the local RocksDB store is just a
queryable cache of it.

A **word count** example makes the duality concrete: the input is a KStream of
individual words (record-at-a-time); grouping by word and counting produces a KTable
(word → running count) — and that KTable's changes are themselves emitted as a stream
of `(word, new_count)` updates, which downstream consumers can treat as either a stream
of count-change events or query as a table for "what's the count right now."

## 4. Architecture & Design Pattern Spotlight

**Pattern: stream-table duality.** This single idea — that a log and a materialized
view of "latest state" are two representations of the same information — is one of the
most conceptually important ideas in the entire curriculum. You'll recognize it again
explicitly in Week 4's CQRS discussion (a read-model is a table; the events that built
it are a stream) and in ClickHouse's Materialized Views (Week 1, Day 6) turning an
insert stream into a continuously updated table.

## 5. Hands-On Lab

```java
StreamsBuilder builder = new StreamsBuilder();
KStream<String, String> textLines = builder.stream("input-topic");

KTable<String, Long> wordCounts = textLines
    .flatMapValues(text -> Arrays.asList(text.toLowerCase().split("\\W+")))
    .groupBy((key, word) -> word)
    .count();

wordCounts.toStream().to("word-count-output");
```
Run this, produce a few lines of text into `input-topic`, and consume
`word-count-output` — observe that it's a stream of *updates* (word, new running count)
rather than final aggregated values. Query the underlying state store directly via
Kafka Streams' Interactive Queries API to confirm you can read "current count for word
X" without waiting for a new event.

## 6. Real-World Product Comparison

- Kafka Streams (embedded, library-based) vs. **ksqlDB or Flink** (managed
  cluster-based) is a genuine architectural choice many teams face: embed
  stream-processing logic directly in an existing service (simpler deployment, tied to
  that service's lifecycle) vs. run a separate, independently-scaled processing layer.
- **Confluent** built ksqlDB specifically to make Kafka Streams-style processing
  accessible via SQL to teams without dedicated stream-processing engineers — the same
  "make advanced infrastructure approachable via SQL" motivation behind BigQuery/
  ClickHouse's own SQL-first design.

## 7. Common Production Pitfalls

- Choosing Kafka Streams for a workload that really needs a separately-scaled
  processing tier (independent of any one application's lifecycle) — coupling stream
  processing to a specific app's deployment cadence when it shouldn't be coupled.
- Not accounting for changelog-topic storage growth — a KTable with high key
  cardinality and frequent updates means a correspondingly large changelog topic.
- Forgetting that local state stores need to be rebuilt (replaying the changelog) on a
  fresh instance or after certain failures — this can mean a real startup delay
  proportional to changelog size, worth testing before assuming instant failover.

## 8. Review Questions
1. What's the precise relationship between a KStream, a KTable, and a changelog topic?
2. Why can a KTable be rebuilt entirely from its changelog topic after a failure?
3. What's the genuine deployment trade-off between Kafka Streams and ksqlDB?
4. Where else in this curriculum have you seen the same "log vs. materialized view"
   duality?

## 9. Proficiency Checkpoint
If you can explain why a KTable and a KStream are "the same data, different lens" and
justify Kafka Streams vs. ksqlDB vs. Flink for a given use case, you're at Level 3.

## Next
Day 9 covers Kafka's exactly-once semantics — the transactional API that makes
multi-topic atomic writes possible.
