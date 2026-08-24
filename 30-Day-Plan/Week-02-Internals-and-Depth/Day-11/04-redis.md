# Day 11: Redis — Caching Patterns: Cache-Aside, Read-Through, Write-Through, Write-Behind

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Implement cache-aside and write-through for the same data, and compare their staleness
windows — directly relevant to your MDO portal cache-bypass investigation.

## 2. Core Concept (basics → advanced)

Four standard patterns for keeping a cache in sync with an underlying data source, each
with a different consistency/complexity trade-off:

- **Cache-aside (lazy loading)**: the application checks the cache first; on a miss, it
  reads from the source, then populates the cache itself. Writes go directly to the
  source, and the application is responsible for invalidating/updating the cache
  entry — the most common pattern, and the one most vulnerable to the cache-key design
  bugs from Week 1, Day 6.
- **Read-through**: conceptually similar to cache-aside, but the *cache layer itself*
  (not the application) is responsible for loading from the source on a miss —
  application code only ever talks to the cache, simplifying application logic at the
  cost of requiring cache infrastructure that supports this mode.
- **Write-through**: every write goes to the cache *and* the source synchronously, as
  one logical operation — the cache is never stale relative to the source, at the cost
  of every write now paying the latency of both operations.
- **Write-behind (write-back)**: writes go to the cache immediately and are
  asynchronously flushed to the source later — lowest write latency, but a real risk
  window where a cache failure before the flush completes means data loss.

```
Cache-aside:     App ──miss──▶ reads SOURCE ──▶ App populates CACHE itself
Read-through:    App ──miss──▶ CACHE reads source itself, App never touches source directly
Write-through:   App ──write──▶ CACHE + SOURCE updated together, synchronously
Write-behind:    App ──write──▶ CACHE only (fast) ──later, async──▶ SOURCE
```

## 3. How It Really Works (Internals)

The staleness/consistency trade-off is the entire point of choosing between these:
cache-aside and read-through can both leave a **stale cache entry** if the source is
updated by some path that doesn't go through the same cache-invalidation logic (exactly
Week 1 Day 6's cache-bypass problem, potentially — a dashboard's embedded query path
updating data without triggering the expected cache invalidation). Write-through
eliminates that specific staleness risk entirely (cache and source change together,
always) but adds latency to every write. Write-behind inverts the trade further,
favoring write latency over durability guarantees.

For a **read-heavy, write-light** workload (a very common shape — dashboards, product
catalogs), cache-aside is usually the pragmatic default: writes are rare enough that
their extra invalidation-logic complexity is manageable, and reads benefit hugely from
caching. For a workload with **frequent writes that must never be lost even briefly**,
write-through is the safer choice despite its latency cost.

## 4. Architecture & Design Pattern Spotlight

**Pattern: cache consistency strategies — a spectrum from "app manages everything"
(cache-aside) to "cache and source move together" (write-through) to "cache is the
fast path, source catches up later" (write-behind).** This maps directly onto Week 1
Day 6's cache-invalidation lesson — today gives you the concrete named patterns for
*how* invalidation/synchronization actually gets implemented, rather than just the
abstract problem.

## 5. Hands-On Lab

```python
import redis, time
r = redis.Redis()

# Cache-aside
def get_product_cache_aside(product_id):
    cached = r.get(f"product:{product_id}")
    if cached:
        return cached
    value = fetch_from_source(product_id)     # simulate a "source" read
    r.setex(f"product:{product_id}", 60, value)
    return value

def update_product_cache_aside(product_id, new_value):
    write_to_source(product_id, new_value)     # write source only
    r.delete(f"product:{product_id}")          # invalidate — NOT update — the cache

# Write-through
def update_product_write_through(product_id, new_value):
    write_to_source(product_id, new_value)
    r.setex(f"product:{product_id}", 60, new_value)   # cache updated in the SAME operation
```
Simulate a concurrent read arriving *during* each update — measure the window where a
reader could see stale data under cache-aside (between the source write and the
cache-delete) versus under write-through (there should be no such window, since both
updates are part of one synchronous operation).

## 6. Real-World Product Comparison

- Most **CDN and dashboard caching layers** (directly relevant to your MDO portal
  work) use cache-aside as the default pattern — which is exactly why cache-key design
  and invalidation logic (Week 1, Day 6) are the actual load-bearing correctness
  mechanism, not the pattern choice itself.
- **Write-behind** is common in systems prioritizing write throughput above all else
  (e.g., some analytics ingestion buffers) — accepting a small durability risk window
  in exchange for dramatically lower write latency.

## 7. Common Production Pitfalls

- Using cache-aside but forgetting to invalidate on *every* code path that writes to
  the source — any update path that doesn't go through the expected invalidation logic
  leaves a stale cache entry with no error signal, precisely the kind of bug worth
  checking for in your MDO portal investigation.
- Choosing write-through for a write-heavy workload without accounting for the
  doubled write latency — every write now pays for both operations, which can
  meaningfully affect a write-heavy path's overall throughput.
- Using write-behind without a clear understanding of the data-loss window if the
  cache fails before flushing to source — this needs to be a conscious, accepted risk,
  not an overlooked detail.

## 8. Review Questions
1. What's the key structural difference between cache-aside and read-through?
2. Why does write-through eliminate a specific staleness risk that cache-aside has?
3. What does write-behind trade away, and why might that trade still be worthwhile?
4. How does this lesson connect directly to Week 1's cache-bypass investigation?

## 9. Proficiency Checkpoint
If you can choose the right caching pattern for a stated workload and explain its
staleness/latency trade-off precisely, you're at Level 3 — directly applicable to your
ongoing MDO portal work.

## Next
Day 12 covers Redis as a primary store vs. cache-only trade-offs — when you'd trust
Redis with data that has no separate source of truth at all.
