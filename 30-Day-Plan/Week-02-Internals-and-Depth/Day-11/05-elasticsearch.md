# Day 11: Elasticsearch — Index Lifecycle Management (ILM)

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Define an ILM policy that rolls over and moves an index through hot→warm→cold phases,
and connect it directly to ClickHouse's TTL tiering from Day 10.

## 2. Core Concept (basics → advanced)

**ILM (Index Lifecycle Management)** automates what would otherwise be manual index
housekeeping: as an index (typically a time-based one, like daily log indices) ages, ILM
moves it through defined **phases**, each with its own configuration:

- **Hot**: actively being written to; on fast, expensive storage; typically triggers a
  **rollover** (start writing to a new index) based on size or age thresholds.
- **Warm**: no longer written to, but still queried reasonably often; can be
  moved to less expensive nodes, and can have replica count reduced or be
  force-merged (fewer, larger segments — Week 1 Day 6 — since no more writes are
  coming).
- **Cold**: infrequently queried; moved to the cheapest available storage tier,
  often with further-reduced resource allocation.
- **Frozen** (or deleted): rarely, if ever, queried; either kept in a highly
  compressed, slow-to-query state, or deleted entirely once retention requirements are
  satisfied.

```
new logs ──▶ [HOT index] ──rollover (size/age)──▶ new hot index created
                  │
                  ▼ (age threshold reached)
              [WARM]  ← force-merged, fewer replicas, cheaper nodes
                  │
                  ▼ (age threshold reached)
              [COLD]  ← cheapest storage, minimal resources
                  │
                  ▼ (retention threshold reached)
              [DELETE]
```

## 3. How It Really Works (Internals)

ILM is implemented as a background process that periodically evaluates every managed
index against its policy's phase transition conditions and takes the corresponding
action (rollover, shrink, force-merge, relocate to different node roles via node
attributes, or delete) — this is precisely the same kind of "policy-driven, automatic
background housekeeping" mechanism as ClickHouse's TTL-triggered part movement (Day
10): both let you declare *intent* ("move to cold after 30 days") rather than manually
scripting data movement, and both execute that intent via periodic background checks
rather than an immediate, synchronous action at the exact threshold moment.

The **rollover** mechanism specifically solves a problem that's easy to get wrong
manually: writing to one ever-growing index degrades performance over time (larger
indices are slower to merge, query, and manage) — rollover automatically starts a
fresh index once a threshold is hit, while an **alias** transparently points queries
at "the currently writable index" without application code needing to track index
names directly.

## 4. Architecture & Design Pattern Spotlight

**Pattern: tiered storage by access recency, policy-driven — the direct structural
twin of yesterday's ClickHouse hot/cold TTL lesson.** Elasticsearch's phase-based ILM
and ClickHouse's TTL-to-volume mechanism are solving the identical problem
(recent data needs speed, old data needs to be cheap) with genuinely analogous
mechanisms — a declared policy, evaluated periodically, driving automatic data
movement — differing mainly in vocabulary (phases vs. TTL/volumes) and in
Elasticsearch's case, adding rollover as an additional first step specific to its
index-per-time-window operational model.

## 5. Hands-On Lab

```json
PUT _ilm/policy/logs_policy
{
  "policy": {
    "phases": {
      "hot":  { "actions": { "rollover": { "max_size": "5gb", "max_age": "1d" } } },
      "warm": { "min_age": "2d", "actions": { "forcemerge": { "max_num_segments": 1 },
                                               "shrink": { "number_of_shards": 1 } } },
      "cold": { "min_age": "7d", "actions": { "freeze": {} } },
      "delete": { "min_age": "30d", "actions": { "delete": {} } }
    }
  }
}
```
Apply this policy to a test index template with a rollover alias, index a batch of
documents (enough to trigger rollover on size), and check `GET
logs*/_ilm/explain` to see each index's current phase and what action ILM will take
next. Compare this policy structure directly against your ClickHouse cluster's actual
TTL configuration from Day 10 — note the analogous phase/threshold structure.

## 6. Real-World Product Comparison

- **Observability platforms** (log/metrics-heavy Elasticsearch deployments) are the
  canonical ILM use case — high-volume, time-based indices where hot-warm-cold-delete
  tiering directly controls infrastructure cost at scale.
- This is the same underlying cost-management lever your **ClickHouse migration
  work** is exercising — whichever engine you standardize on for the MDO portal,
  the tiering *strategy* (recent=fast/expensive, old=slow/cheap) transfers directly,
  even though the specific configuration syntax differs.

## 7. Common Production Pitfalls

- Setting rollover thresholds without considering actual query patterns — too-frequent
  rollover creates many small indices (worse query performance, since more indices
  means more shards to check per query); too-infrequent rollover means each index
  grows too large before finally rolling over.
- Force-merging an index that's still occasionally written to — force-merge assumes
  no more writes are coming and can cause issues if that assumption is violated.
- Not verifying that ILM policies are actually executing as expected in production —
  a misconfigured or stalled ILM policy can leave indices in the wrong phase (and on
  the wrong, more expensive storage tier) indefinitely without an obvious alert.

## 8. Review Questions
1. What problem does rollover solve that a single ever-growing index wouldn't?
2. Why is force-merging only safe once an index is no longer being written to?
3. What's the direct structural parallel between ILM phases and ClickHouse's TTL-to-
   volume mechanism?
4. Why might too-frequent rollover actually hurt query performance?

## 9. Proficiency Checkpoint
If you can design an ILM policy for a stated retention/cost requirement and map it
directly onto the equivalent ClickHouse TTL configuration, you're at Level 3.

## Next
Day 12 covers Parquet file internals and Lambda vs. Kappa architectures — connecting
this week's storage-tiering theme to file formats and pipeline architecture broadly.
