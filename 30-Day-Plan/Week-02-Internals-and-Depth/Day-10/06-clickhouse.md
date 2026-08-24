# Day 10: ClickHouse — Hot/Cold Tiering: TTL TO VOLUME/DISK & storage_policy

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Configure a 2-tier storage policy (hot NVMe / cold object storage) with a TTL that
moves aging parts to the cold tier — this is your own production cluster's exact
configuration, made explicit end to end.

## 2. Core Concept (basics → advanced)

A `storage_policy` defines one or more **volumes**, each backed by one or more
**disks**, ordered by priority — ClickHouse writes new parts to the highest-priority
volume by default, and a table-level `TTL ... TO VOLUME 'cold'` (or `TO DISK 'cold'`)
clause tells the background merge process to physically move parts that match the TTL
condition (typically, "older than N days") to the specified lower-priority volume,
without any application-level intervention.

```
storage_policy "hot_cold":
  volume "hot"  (priority 1): disk "nvme_local"    ← new inserts land here
  volume "cold" (priority 2): disk "gcs_backed"    ← TTL-moved parts land here

TABLE events (...)
ENGINE = MergeTree
ORDER BY (org_id, event_time)
TTL event_time + INTERVAL 30 DAY TO VOLUME 'cold'
SETTINGS storage_policy = 'hot_cold';

New INSERT ──▶ lands on "hot" (NVMe)
       │
       ▼ (background process, runs periodically)
Part older than 30 days? ──▶ MOVED (not copied — the original part is relocated)
                              to "cold" (GCS-backed disk)
```

## 3. How It Really Works (Internals)

This move is executed by the same background **merge/mutation machinery** that handles
regular part merging (Week 1, Day 1's MergeTree lesson) — TTL-based movement is treated
as another housekeeping task the merge scheduler periodically checks for, alongside
merging small parts into larger ones. Critically, a **query spanning both hot and cold
data works completely transparently** — the query planner doesn't need to know or care
which volume a given part lives on; it just reads whichever parts satisfy the query's
predicates, at whatever latency that volume's underlying storage provides. This is
exactly why the trade-off is invisible at the SQL layer and only shows up as query
latency: a query that happens to need mostly recent (hot) data is fast; a query
spanning a long historical window that pulls in many cold-tier parts is correspondingly
slower, since GCS-backed reads have materially higher latency than local NVMe.

Your cluster's specific configuration — hot NVMe, cold GCS-backed storage, TTL-based
movement — is a direct, deliberate application of this exact mechanism, chosen
specifically because most real query traffic concentrates on recent data while
historical data needs to exist (for compliance/analysis) without paying full NVMe
storage cost for data rarely queried.

## 4. Architecture & Design Pattern Spotlight

**Pattern: tiered storage by access recency, with policy-driven (not manual) data
movement.** This is the exact same pattern as Kafka's tiered storage (Day 10's Kafka
lesson) and Elasticsearch's hot-warm-cold node roles (Day 10's Elasticsearch lesson) —
by this point in the curriculum you've now seen three independent systems solve
"recent data needs speed, old data needs cheap storage" with a declarative policy
rather than manual data-shuffling — recognizing this as one pattern, applied three
times, is exactly the kind of cross-system fluency this curriculum is built to produce.

## 5. Hands-On Lab

On your own cluster (or a local test cluster mirroring its shape):
```sql
-- verify current policy assignment
SELECT name, policy_name FROM system.storage_policies;

-- check where a specific table's parts currently live
SELECT name, disk_name, modification_time
FROM system.parts
WHERE table = 'events' AND active
ORDER BY modification_time DESC
LIMIT 20;
```
Insert a small batch of synthetic data with an artificially old `event_time` (e.g.,
40 days in the past, past your 30-day TTL threshold), force a TTL-driven merge cycle
with `OPTIMIZE TABLE events FINAL`, then re-check `system.parts` — confirm the
`disk_name` for that part has changed from your hot disk to your cold disk. Time a
query against purely recent data vs. a query spanning the cold-tier range, and record
the latency difference — this is your cluster's real hot/cold trade-off, quantified.

## 6. Real-World Product Comparison

- **BigQuery** achieves a comparable cost effect through its storage pricing model
  (long-term storage discount for tables/partitions untouched for 90 days) rather than
  an explicit, configurable volume/TTL mechanism — the cost incentive is similar, but
  ClickHouse's model gives you direct, granular control over exactly where data
  physically lives and when it moves.
- **Elasticsearch's ILM** (Day 11) is the closest direct analog — index lifecycle
  policies moving indices through hot→warm→cold→frozen tiers on a schedule, the same
  underlying idea applied to a different storage engine's unit of data (an index
  rather than a MergeTree part).

## 7. Common Production Pitfalls

- Setting the TTL threshold without validating actual query patterns first — if a
  meaningful fraction of real queries span the boundary you've chosen, you've just
  made a large fraction of production queries pay cold-tier latency unnecessarily.
- Not monitoring the background merge/TTL-move process's own resource usage — moving
  large parts to object storage is itself I/O and network work that competes with
  regular query and merge load.
- Forgetting that cold-tier reads have real latency and cost implications for
  interactive dashboards — a report that silently starts spanning the TTL boundary
  (e.g., a "trailing 60 days" report against a 30-day hot tier) can regress in latency
  without any code change, purely because more of its data now lives cold.

## 8. Review Questions
1. What specifically triggers a part's move from hot to cold storage?
2. Why is this move handled by the same machinery as regular part merging?
3. Why is the hot/cold split invisible to the SQL query layer, and only visible as
   latency?
4. What's the direct structural parallel between this mechanism and Elasticsearch's ILM?

## 9. Proficiency Checkpoint
If you can explain your own production cluster's storage policy end to end — from
`INSERT` to eventual cold-tier move to query-time transparency — and reason about the
latency trade-off for a specific query pattern, you're at a genuine Level 3.5+ on this
exact production system you already operate.

## Next
Day 11 covers dictionaries — a fast lookup alternative to JOIN that directly fixes
Day 9's fan-out problem structurally, rather than just working around it query by query.
