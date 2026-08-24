# Day 15: Elasticsearch — Shard Sizing & Refresh Tuning

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Compare indexing throughput at `refresh_interval=1s` vs. `30s` on a bulk load, and
explain the shard over-sizing/under-sizing trade-off.

## 2. Core Concept (basics → advanced)

**Shard sizing** is a genuine Goldilocks problem: too many small shards means
excessive per-shard overhead (each shard has real memory/file-handle cost, and a
query touching many tiny shards pays more coordination overhead than the actual
work justifies) — too few large shards means slower individual queries (larger
segments to search, Week 1 Day 6) and slower recovery/rebalancing (moving one giant
shard is a bigger, slower operation than moving several smaller ones). A commonly
cited starting heuristic is keeping shard size in the tens of GB range, but — as with
Day 15's PySpark playbook — this is a heuristic to validate against your actual data
and query patterns, not a universal constant.

**Refresh interval tuning** (Week 1, Day 6) directly trades indexing throughput
against search-visibility latency — a longer `refresh_interval` during bulk loading
means less frequent (and therefore less overhead-heavy) segment creation, letting
more indexing throughput go toward actual data ingestion rather than repeated
refresh operations.

## 3. How It Really Works (Internals)

Over-sharding's overhead cost compounds specifically at the cluster-coordination
level (Week 1, Day 5) — every additional shard is another unit the master-eligible
quorum must track in cluster state, and every query against an over-sharded index
means more scatter-gather fan-out (Week 1, Day 4) than the actual data volume would
otherwise require. This is a direct, quantifiable cost, not an abstract concern —
it's exactly why "just create lots of small shards for safety" is not a
cost-free choice.

Refresh-interval tuning's benefit during bulk loading comes from reducing the
frequency of the segment-creation/merge cycle (Week 1, Day 6) — fewer, larger
refresh operations mean less cumulative merge overhead competing with the actual
indexing work for I/O and CPU resources during the load.

## 4. Architecture & Design Pattern Spotlight

**Pattern: right-sizing distributed storage units — the same underlying "not too
many, not too few, sized to actual data volume" reasoning as Kafka partition count
(Day 15's Kafka lesson) and Spark shuffle partition sizing (Day 15's PySpark
lesson).** Recognizing this as one recurring sizing problem, appearing across every
distributed system studied this month, should make each new instance faster to
reason about from first principles.

## 5. Hands-On Lab

```bash
curl -X PUT "localhost:9200/bulk_test_fast" -d '{"settings":{"refresh_interval":"1s"}}'
curl -X PUT "localhost:9200/bulk_test_slow" -d '{"settings":{"refresh_interval":"30s"}}'
```
Bulk-index the same ~500K synthetic documents into both indices, timing the total
indexing duration for each. Compare indexing throughput directly, and check
`GET _cat/segments` for each index afterward — the slower-refresh index should show
fewer, more consolidated segments given the same document count.

## 6. Real-World Product Comparison

- **Observability platforms** (high-volume log ingestion) commonly disable refresh
  entirely (`refresh_interval: -1`) during known bulk-load windows, re-enabling it
  once the load completes — the same technique from Week 1 Day 6, quantified here.
- Shard-sizing guidance varies meaningfully between **Elasticsearch's** general
  recommendations and any specific vendor's managed-service defaults (e.g., a
  managed observability platform's opinionated index templates) — worth checking
  actual current guidance rather than relying on memorized numbers that can shift
  between versions.

## 7. Common Production Pitfalls

- Over-sharding "just in case" without validating actual per-shard size against
  data volume — a very common, avoidable source of unnecessary cluster overhead.
- Leaving `refresh_interval` at its default during a large, known bulk-load
  operation, missing an easy throughput win.
- Not revisiting shard sizing as data volume grows over an index's lifetime — a
  sizing decision correct at launch can become wrong as actual volume diverges from
  original estimates.

## 8. Review Questions
1. What's the concrete cluster-level cost of over-sharding, beyond "it feels
   wasteful"?
2. Why does reducing refresh frequency improve bulk-indexing throughput?
3. Why is shard-size guidance a heuristic to validate, not a fixed rule?
4. How is this the same underlying sizing problem as Kafka partition count?

## 9. Proficiency Checkpoint
If you can reason about shard sizing from actual data volume and query patterns, and
quantify a refresh-interval tuning benefit, you're at Level 3.5.

## Next
Day 16 covers query-performance profiling — the `_search` profile API applied to
genuinely expensive query patterns like leading wildcards and scripts.
