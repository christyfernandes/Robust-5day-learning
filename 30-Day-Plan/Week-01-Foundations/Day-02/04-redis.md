# Day 2: Redis — Sorted Sets, HyperLogLog, Bitmaps & Geospatial

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Choose the correct specialized structure for a given problem (ranking, cardinality
estimation, flags-at-scale, proximity) and explain the space/accuracy trade-off each one
makes to get its performance.

## 2. Core Concept (basics → advanced)

**Sorted Sets — the workhorse for ranking.** Every member has a score; Redis maintains
the set in score order internally, giving you O(log N) insert/update and O(log N) range
queries "give me rank 10–20" or "give me everyone with score > X" — without you ever
writing a sort yourself.
```python
r.zadd("leaderboard", {"alice": 1500, "bob": 1200, "carol": 1800})
r.zrevrange("leaderboard", 0, 2, withscores=True)   # top 3, highest first
r.zrank("leaderboard", "bob")                        # bob's rank (0-indexed, ascending)
r.zincrby("leaderboard", 50, "alice")                 # atomic score increment
```

**HyperLogLog — approximate cardinality at fixed memory cost.** Counting *exact*
distinct values (e.g., unique daily visitors) normally requires storing every value
you've seen (a Set, growing with cardinality). HyperLogLog instead uses a fixed ~12KB
of memory *regardless of how many millions of distinct items you add*, at the cost of a
small, well-understood error rate (~0.81% standard error).
```python
r.pfadd("unique_visitors:2026-08-24", "user1", "user2", "user3")
r.pfcount("unique_visitors:2026-08-24")   # approximate distinct count
```

**Bitmaps — a String, addressed bit-by-bit.** For flags-at-scale (e.g., "did user N log
in today?" across millions of users), a bitmap uses 1 bit per user rather than a full
key per user.
```python
r.setbit("logged_in:2026-08-24", user_id, 1)
r.bitcount("logged_in:2026-08-24")  # how many users logged in today
```

**Geospatial — sorted sets under the hood.** `GEOADD` stores lat/long as a specially
encoded score in a sorted set (a **geohash**), so proximity queries reuse the same
sorted-set machinery you already know.
```python
r.geoadd("stores", (77.5946, 12.9716, "store:bengaluru"))
r.georadius("stores", 77.6, 12.97, 10, unit="km")  # stores within 10km
```

## 3. How It Really Works (Internals)

A sorted set is implemented as a combination of a **hash table** (for O(1)
member→score lookup) and a **skip list** (a probabilistic, layered linked-list
structure that gives O(log N) ordered traversal without needing a balanced tree). Skip
lists are simpler to implement correctly under concurrent-ish access patterns than a
balanced tree, which is part of why Redis's author chose them.

HyperLogLog works by hashing each input and tracking the **longest run of leading
zeros** observed in any hash — a clever probabilistic estimator: the longer the longest
run you've seen, the more distinct values you've likely hashed (this is genuinely
counter-intuitive the first time you see it, but it's the entire trick, and it's why
the memory footprint stays flat regardless of true cardinality).

## 4. Architecture & Design Pattern Spotlight

**Pattern: trading exactness for fixed memory (probabilistic data structures).**
HyperLogLog and Bloom filters (not built into core Redis, but a close conceptual
cousin, and available via the RedisBloom module) both make this same trade explicitly.
This is a recurring theme in systems that operate "at scale" — ClickHouse's
`uniqExact` vs. approximate `uniq` functions (Week 2) make the identical trade-off for
the identical reason.

## 5. Hands-On Lab
Build a same-day "unique active users" counter two ways and compare memory:
```python
# Exact (Set) - grows with cardinality
for uid in range(100_000):
    r.sadd("exact_visitors", f"user{uid}")
print("exact:", r.scard("exact_visitors"))

# Approximate (HyperLogLog) - fixed ~12KB regardless
for uid in range(100_000):
    r.pfadd("approx_visitors", f"user{uid}")
print("approx:", r.pfcount("approx_visitors"))

print(r.memory_usage("exact_visitors"), "vs", r.memory_usage("approx_visitors"))
```

## 6. Real-World Product Comparison

- **Twitter-style timelines and gaming leaderboards** are the canonical sorted-set use
  case — real-time rank queries over millions of entries, updated constantly, with no
  separate sort step needed.
- Google's original **HyperLogLog paper** (an evolution of the earlier LogLog
  algorithm) is used far beyond Redis — BigQuery's `APPROX_COUNT_DISTINCT` and
  ClickHouse's `uniq()` function are built on the same family of algorithm, so what you
  learn here transfers directly.
- Contrast with a **database-side `COUNT(DISTINCT ...)`**: exact, but requires
  scanning/hashing every row every time, unlike HyperLogLog's incremental,
  fixed-memory running count.

## 7. Common Production Pitfalls
- Using a plain Set for a "roughly how many uniques" metric when the cardinality could
  grow unbounded — memory grows linearly with true cardinality, which surprises people
  who only tested at small scale.
- Forgetting sorted-set operations are O(log N), not O(1) — usually fine, but worth
  knowing before assuming every Redis operation is equally cheap (Day 1's "avoid slow
  commands" caution applies here too, at a smaller scale).
- Using bitmaps for sparse, high-cardinality IDs without offsetting them — a bitmap's
  size is proportional to the *highest bit position set*, so a single very large user ID
  used directly as an offset can allocate far more memory than intended.

## 8. Review Questions
1. Why is a sorted set's insert O(log N) instead of O(1) like a hash?
2. Mechanically, what does HyperLogLog track to estimate cardinality?
3. When would you deliberately choose an approximate count over an exact one?
4. What's the actual memory-usage gotcha with Redis bitmaps?

## 9. Proficiency Checkpoint
If you can choose the right structure (sorted set vs. HyperLogLog vs. bitmap) for a
given problem and justify the trade-off out loud, you're at Level 2, moving into Level 3.

## Next
Day 3 covers persistence — RDB snapshots vs. AOF, and what actually happens (and what's
lost) when Redis crashes under each configuration.
