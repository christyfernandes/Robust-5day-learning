# Day 6: Elasticsearch — Indexing Internals: Segments & Near-Real-Time Search

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Tune `refresh_interval` and observe the resulting delay between indexing a document and
being able to search for it — and explain why that delay exists at all.

## 2. Core Concept (basics → advanced)

An Elasticsearch shard is really a Lucene index under the hood, and Lucene's storage is
**segment-based**: each batch of indexed documents is written as a new, immutable
**segment** (its own mini inverted index). Documents are never updated in place —
an "update" is really a delete-marker on the old version plus a new document in a new
segment. Over time, many small segments accumulate, and a background **merge** process
combines them into fewer, larger segments (also physically removing documents marked
as deleted along the way).

```
Write path:
  index doc → in-memory buffer (NOT yet searchable)
       │
       ▼ refresh (default: every 1s)
  new segment created, opened for search  ← NOW searchable ("near real-time")
       │
       ▼ flush (less frequent — writes to disk + clears translog)
  segment durably persisted
       │
       ▼ merge (background, ongoing)
  small segments combined into fewer, larger ones
```

## 3. How It Really Works (Internals)

**Refresh** is what makes newly-indexed documents searchable — it opens a new "reader"
view that includes the latest in-memory segment. This is *not* the same as
**flush**, which is about durability (writing segments to disk and clearing the
**translog**, Elasticsearch's write-ahead log used for crash recovery of not-yet-flushed
data). This is the precise reason Elasticsearch is called "near-real-time" rather than
real-time: there's a real, configurable gap (`refresh_interval`, default 1 second)
between "document indexed" and "document searchable," by deliberate design — refreshing
after every single document would be prohibitively expensive at any real write volume.

**Segment merging** matters operationally because: more segments means slower search
(a query must check every segment), so merge policy tuning is a genuine performance
lever, and merges themselves consume I/O and CPU — a heavy-merge period can visibly
compete with query load for resources, which is why bulk-load workflows often
temporarily disable/relax refresh and merge settings during the load, then re-enable
them afterward.

## 4. Architecture & Design Pattern Spotlight

**Pattern: LSM-tree-style segment accumulation + background compaction.** This is
*exactly* the same storage pattern as RocksDB (Day 5's Flink state backend), Cassandra,
and most modern write-optimized storage engines: never mutate existing files, append new
immutable segments, and merge/compact in the background. Recognizing this pattern here
sets up a direct, explicit comparison to ClickHouse's own MergeTree family tomorrow —
same storage-engine philosophy, different specific engine.

## 5. Hands-On Lab

```bash
curl -X PUT "localhost:9200/day6test" -H 'Content-Type: application/json' -d'
{ "settings": { "refresh_interval": "30s" } }'

curl -X POST "localhost:9200/day6test/_doc" -H 'Content-Type: application/json' -d'
{ "message": "will this be searchable immediately?" }'

# immediately search — should return ZERO hits (refresh hasn't happened yet)
curl "localhost:9200/day6test/_search?q=immediately"

# force a refresh manually and search again
curl -X POST "localhost:9200/day6test/_refresh"
curl "localhost:9200/day6test/_search?q=immediately"   # now it appears
```
Repeat with `refresh_interval: "1s"` (the default) and observe the much shorter natural
delay without a manual refresh.

## 6. Real-World Product Comparison

- High-throughput bulk-loading workflows (common at companies indexing large log
  volumes, like observability platforms) routinely set `refresh_interval: -1`
  (disabled) during a bulk load, then re-enable it afterward — trading temporary search
  staleness for significantly faster ingest.
- This segment-merge storage model is the direct conceptual sibling of **ClickHouse's
  MergeTree** family (tomorrow's lesson) — both are LSM-style engines, optimized for
  very different query shapes (full-text search vs. columnar analytics) on top of a
  structurally similar storage foundation.

## 7. Common Production Pitfalls

- Setting `refresh_interval` too aggressively low "to be safe" on a heavy-write index —
  refreshing very frequently has a real CPU/memory cost, often unnecessary for use
  cases that don't actually need sub-second search visibility.
- Not distinguishing refresh-related staleness from a genuine indexing failure when
  debugging "why isn't my document showing up in search" — check whether a refresh
  happened before assuming the document failed to index at all.
- Ignoring merge-related resource contention as a cause of periodic search-latency
  spikes — merges are background work, but they're not free.

## 8. Review Questions
1. What's the precise difference between a refresh and a flush?
2. Why can't Elasticsearch update a document in place?
3. Why does bulk-loading commonly disable refresh temporarily?
4. What's the direct structural parallel between Lucene's segments and RocksDB's SSTables?

## 9. Proficiency Checkpoint
If you can explain "near-real-time" accurately (not just "it's basically instant") and
tune refresh behavior appropriately for a stated workload, you're at Level 2 moving
into Level 3.

## Next
Day 7 combines this week's concepts into one lab session, including your first ADR.
