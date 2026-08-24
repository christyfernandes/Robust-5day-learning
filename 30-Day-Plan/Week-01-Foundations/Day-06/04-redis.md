# Day 6: Redis — Eviction Policies & Memory Fragmentation

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Configure `allkeys-lru` eviction, fill an instance past its memory limit, and explain
why Redis's LRU is approximate rather than exact.

## 2. Core Concept (basics → advanced)

When Redis hits `maxmemory`, its **eviction policy** decides what to remove to make
room for new writes:
- **`noeviction`**: refuse new writes with an error instead of evicting anything —
  correct when data loss is unacceptable, but means your application must handle write
  failures gracefully.
- **`allkeys-lru`** / **`volatile-lru`**: evict least-recently-used keys (optionally
  restricted to keys with a TTL set, for `volatile-*`).
- **`allkeys-lfu`** / **`volatile-lfu`**: evict least-frequently-used — better than LRU
  for workloads where "used a lot, but not recently" keys shouldn't be evicted just
  because of a temporary lull.
- **`allkeys-random`** / **`volatile-random`**: evict at random — cheaper to compute,
  useful when access patterns are genuinely uniform and precise eviction ordering
  doesn't matter.

## 3. How It Really Works (Internals)

Redis's LRU is **not** a true LRU list (which would require maintaining a doubly-linked
list ordered by access time, updated on every single read — real overhead at Redis's
scale). Instead, Redis uses **approximate LRU via random sampling**: on eviction, it
samples a small number of random keys (`maxmemory-samples`, default 5), evicts the
least-recently-used *among that sample*, and repeats as needed. This is dramatically
cheaper than true LRU while still being a statistically good approximation, especially
with a larger sample size — but it means "least recently used" is only ever
approximately true, not exact, and can occasionally evict a key that isn't truly the
global least-recently-used one.

**Memory fragmentation** is a separate concern: Redis's memory allocator (jemalloc by
default) can end up with a higher resident-memory footprint than the actual data would
require, because freed memory from deleted/expired keys isn't always immediately
reusable for new allocations of a different size. The `mem_fragmentation_ratio` in
`INFO memory` (`used_memory_rss / used_memory`) surfaces this — a ratio significantly
above 1 indicates real fragmentation overhead, and Redis supports **active
defragmentation** as a background process to reclaim it.

## 4. Architecture & Design Pattern Spotlight

**Pattern: approximate algorithms trading precision for overhead — sampling-based LRU
instead of exact bookkeeping.** This is the same underlying trade-off as HyperLogLog
(Day 2's cardinality estimation) and Elasticsearch's approximate `terms` aggregation
under sharding (Day 4) — a recurring theme this month: exact answers are often far more
expensive than "close enough," and mature systems deliberately choose approximate when
the precision isn't actually needed.

## 5. Hands-On Lab

```bash
# redis.conf
maxmemory 100mb
maxmemory-policy allkeys-lru
maxmemory-samples 5
```
Fill the instance past 100MB with synthetic keys of varying access frequency (write a
small script that periodically re-reads a "hot" subset of keys to keep them fresh),
then keep inserting new keys and watch `INFO stats` → `evicted_keys` climb. Verify your
hot subset survives longer than the cold, never-re-read keys. Then check
`mem_fragmentation_ratio` in `INFO memory` before and after a burst of key
deletions/expirations.

## 6. Real-World Product Comparison

- Approximate LRU via sampling is the same fundamental trade Redis makes elsewhere
  (HyperLogLog) and the same trade a CDN's or OS page cache's eviction algorithm often
  makes — exact LRU/LFU bookkeeping at very high throughput is rarely worth its overhead
  compared to a well-tuned approximation.
- **GitHub** and **Twitter**, both large Redis operators, tune `maxmemory-samples`
  upward for workloads where eviction accuracy matters more than the marginal CPU cost
  of a larger sample — a concrete example of the precision/overhead knob actually being
  turned in production.

## 7. Common Production Pitfalls

- Using `noeviction` in production without handling write-rejection errors in
  application code — writes simply start failing once memory is full, often surfacing
  as a confusing downstream error rather than an obvious "Redis is full" signal.
- Choosing `allkeys-lru` when your actual access pattern is closer to "frequently used
  in bursts, with quiet gaps" — `allkeys-lfu` is usually the better fit and is
  under-used relative to how often it would help.
- Ignoring `mem_fragmentation_ratio` on a long-running instance with heavy key
  churn — fragmentation can silently push actual memory usage well above what the
  dataset size would suggest, triggering unexpected eviction or OOM.

## 8. Review Questions
1. Why does Redis use sampling instead of a true LRU list?
2. What's the practical difference between `allkeys-lru` and `allkeys-lfu` for a
   bursty access pattern?
3. What does a `mem_fragmentation_ratio` significantly above 1 actually indicate?
4. Why might `noeviction` be the *correct* choice despite causing write failures?

## 9. Proficiency Checkpoint
If you can choose the right eviction policy for a described access pattern and explain
why sampling-based LRU is "good enough," you're at Level 2 moving into Level 3.

## Next
Day 7 combines the week's concepts into one lab session, including your first ADR.
