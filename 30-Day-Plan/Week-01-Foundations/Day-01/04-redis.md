# Day 1: Redis — In-Memory Data Structures Foundations

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain why Redis's single-threaded design is a deliberate performance choice (not a
limitation to work around), and use the core data structures correctly, including
knowing which operations are O(1) vs. more expensive.

## 2. Core Concept (basics → advanced)

**Redis is single-threaded for command execution, by design.** One thread processes
commands one at a time against an in-memory data structure — no locks needed for most
operations, because there's no concurrent access to guard against within that thread.
This sounds like it should be slow; it isn't, because in-memory operations on simple
data structures are extremely fast (microseconds), and Redis avoids the context-switch
and locking overhead a multi-threaded design would pay for the same workload. (Redis
does use background threads for some I/O and lazy-freeing since v4/v6, but command
execution itself remains single-threaded — this nuance matters and is exactly why
DragonflyDB and Redis 7's multi-threaded I/O exist, both covered in Week 2.)

**Core data structures:**
```
String    → simple value, or counter (INCR/DECR are atomic)
List      → ordered, push/pop from either end — O(1) at head/tail
Set       → unordered unique members — O(1) membership check
Hash      → field-value map within one key — good for structured objects
Sorted Set→ members with a score, kept in sorted order — O(log N) insert (skip list)
```

```python
import redis
r = redis.Redis()

r.set("session:abc123", "user_42", ex=3600)          # TTL in seconds
r.lpush("recent_orders", "order_101", "order_102")   # list, newest at head
r.sadd("tags:post_9", "python", "data-eng")          # set, unique tags
r.hset("user:42", mapping={"name": "Christy", "role": "architect"})  # hash
r.zadd("leaderboard", {"alice": 150, "bob": 200})    # sorted set: member -> score
```

**TTL and atomicity.** `EX`/`PX` set an expiry directly on `SET`; `INCR` is atomic even
under concurrent access from many clients, because the single-threaded model guarantees
no interleaving mid-command.

## 3. How It Really Works (Internals)

Redis's event loop is a **reactor pattern**: a single thread runs an event loop (built
on epoll/kqueue) that multiplexes many client socket connections, dispatching each
ready command to be executed synchronously against the in-memory dataset, then moving
to the next ready event. This is the same underlying pattern as Node.js's event loop —
if that's familiar from your frontend background, the mental model transfers directly.

```
        many client connections
              │  │  │  │
              ▼  ▼  ▼  ▼
        ┌─────────────────────┐
        │   epoll/kqueue       │  ← OS-level "which sockets are ready?"
        │   event loop         │
        └──────────┬──────────┘
                    ▼
        ┌─────────────────────┐
        │ single command       │  ← executes one command fully before
        │ execution thread      │     moving to the next — no locking needed
        └─────────────────────┘
```

## 4. Architecture & Design Pattern Spotlight

**Pattern: single-threaded reactor for predictable low latency.** The trade-off: one
slow command (a poorly chosen `KEYS *` on a huge keyspace, or an O(N) operation on a
giant collection) blocks *everything* else, because there's only one thread. This is
why Redis documentation is emphatic about avoiding certain commands in production —
it's not paranoia, it's a direct consequence of this architecture.

## 5. Hands-On Lab
Build a simple rate limiter using `INCR` + `EXPIRE`:
```python
def is_allowed(user_id, limit=10, window_seconds=60):
    key = f"rate:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window_seconds)
    return count <= limit
```
Call it in a loop 15 times for the same `user_id` and confirm it starts rejecting after
10. Then try `r.ttl(key)` to see the countdown — this is the exact building block
Architecture Day 22 revisits as a formal rate-limiting pattern.

## 6. Real-World Product Comparison

- **Twitter** historically used Redis-backed structures for parts of its timeline
  architecture — sorted sets are a natural fit for "recent items ranked by time/score."
- **GitHub and Stack Overflow** both lean on Redis heavily for caching — Stack
  Overflow's architecture is famous for running on a surprisingly small number of
  servers partly because aggressive Redis caching keeps database load low.
- Contrast with **Memcached**: simpler (just a key-value cache, multi-threaded, no rich
  data structures, no persistence) — a reasonable choice if all you need is a pure
  cache and want to use every core without Redis's single-thread ceiling per instance.

## 7. Common Production Pitfalls
- Running `KEYS *` in production — it's O(N) and blocks the single thread for the
  entire scan on a large keyspace. Use `SCAN` (cursor-based, non-blocking) instead.
- Storing very large values in a single key (e.g., a multi-MB blob) — fine
  occasionally, but consider what one slow read/write does to the single command
  thread's throughput for everyone else.
- Forgetting TTLs entirely on cache keys — turns Redis into an unbounded memory sink
  (Day 6 covers eviction policies as the safety net, but TTL discipline is the first
  line of defense).

## 8. Review Questions
1. Why doesn't Redis need locks for most single-command operations?
2. What's the real cost of running `KEYS *` on a large keyspace, and what should you
   use instead?
3. Which data structure would you pick for a leaderboard, and why is its insert
   O(log N) rather than O(1)?
4. What's genuinely different about Memcached vs. Redis beyond "Redis has more
   features"?

## 9. Proficiency Checkpoint
If you can pick the right data structure for a given access pattern and explain why
single-threaded execution is a deliberate trade-off (not an oversight), you're at
Level 2.

## Next
Day 2 covers the more specialized structures — sorted sets in depth, HyperLogLog,
bitmaps, and geospatial commands — plus when each earns its keep over a plain hash/set.
