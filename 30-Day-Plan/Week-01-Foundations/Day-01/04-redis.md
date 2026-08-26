# Day 1: Redis — In-Memory Data Structures Foundations

## Time: ~30 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain why Redis's single-threaded design is a deliberate performance choice (not a
limitation to work around), and use the core data structures correctly, including
knowing which operations are O(1) vs. more expensive.

## 2. Core Concept (basics → advanced)

**Start here if Redis is genuinely new to you.** Redis is a database that keeps all of
its data **in RAM** rather than on disk, which is what makes it extremely fast
(reading/writing memory is roughly 100-1000x faster than reading/writing a typical
disk) — the trade-off is that RAM is more expensive per gigabyte than disk and is
volatile (data disappears if the process dies, unless you explicitly configure
persistence, covered Day 3). Redis is most commonly used as a **cache** sitting in
front of a slower, disk-backed database, or as fast, temporary shared storage between
multiple application processes (session data, rate limiters, real-time counters).

**Redis is single-threaded for command execution, by design.** One thread processes
commands one at a time against the in-memory data — no locks needed for most
operations, because there's no concurrent access to guard against within that thread
(two commands literally cannot run at the exact same instant, so neither can corrupt
the other's work mid-operation). This sounds like it should be slow; it isn't, because
in-memory operations on simple data structures are extremely fast (microseconds), and
Redis avoids the context-switch and locking overhead a multi-threaded design would pay
for the same workload. (Redis does use background threads for some I/O and
lazy-freeing since v4/v6, but command execution itself remains single-threaded — this
nuance matters and is exactly why DragonflyDB and Redis 7's multi-threaded I/O exist,
both covered in Week 2.)

**Core data structures** (a "key" is just the name you look a value up by, like a
variable name — every one of these lives under one key):
```
String    → simple value, or counter (INCR/DECR are atomic)
List      → ordered, push/pop from either end — O(1) at head/tail
Set       → unordered unique members — O(1) membership check
Hash      → field-value map within one key — good for structured objects
Sorted Set→ members with a score, kept in sorted order — O(log N) insert (skip list)
```
("O(1)" means the operation takes roughly the same tiny amount of time no matter how
big the collection is — a fixed number of steps. "O(log N)" means it gets slightly
slower as the collection grows, but very gradually — doubling a sorted set's size adds
only one extra step, not double the work. Both are considered "fast" in practice; the
distinction matters mainly when comparing structures for a specific access pattern.)

```python
import redis
r = redis.Redis()

r.set("session:abc123", "user_42", ex=3600)          # TTL in seconds
r.lpush("recent_orders", "order_101", "order_102")   # list, newest at head
r.sadd("tags:post_9", "python", "data-eng")          # set, unique tags
r.hset("user:42", mapping={"name": "Christy", "role": "architect"})  # hash
r.zadd("leaderboard", {"alice": 150, "bob": 200})    # sorted set: member -> score
```

**TTL and atomicity.** TTL ("time to live") means a key automatically deletes itself
after a set number of seconds — `EX`/`PX` set an expiry directly on `SET`. `INCR` is
**atomic** even under concurrent access from many clients simultaneously — "atomic"
here means the whole read-increment-write happens as one indivisible step, so two
clients calling `INCR` on the same key at nearly the same moment can never both read
the same starting value and silently lose one of the increments (a very common bug in
systems without this guarantee) — this is a direct, free consequence of the
single-threaded model: no other command can interleave in the middle of it.

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
import redis
r = redis.Redis()

def is_allowed(user_id, limit=10, window_seconds=60):
    key = f"rate:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window_seconds)
    return count <= limit

for i in range(1, 16):
    allowed = is_allowed("demo_user")
    ttl = r.ttl("rate:demo_user")
    print(f"call {i:2d}: count={r.get('rate:demo_user').decode():>2} allowed={allowed}  ttl={ttl}")
```
Call it in a loop 15 times for the same `user_id` and confirm it starts rejecting after
10. Then try `r.ttl(key)` to see the countdown — this is the exact building block
Architecture Day 22 revisits as a formal rate-limiting pattern.

### Sample Output

```
call  1: count= 1 allowed=True  ttl=60
call  2: count= 2 allowed=True  ttl=60
call  3: count= 3 allowed=True  ttl=60
call  4: count= 4 allowed=True  ttl=60
call  5: count= 5 allowed=True  ttl=60
call  6: count= 6 allowed=True  ttl=60
call  7: count= 7 allowed=True  ttl=60
call  8: count= 8 allowed=True  ttl=60
call  9: count= 9 allowed=True  ttl=60
call 10: count=10 allowed=True  ttl=60
call 11: count=11 allowed=False  ttl=60
call 12: count=12 allowed=False  ttl=60
call 13: count=13 allowed=False  ttl=60
call 14: count=14 allowed=False  ttl=60
call 15: count=15 allowed=False  ttl=60
```

Reading this line by line:
- `count` climbs by exactly 1 on every call — that's `r.incr(key)` doing its atomic
  read-and-increment, once per call, with no lost updates.
- `allowed` flips from `True` to `False` exactly at the transition from call 10 to
  call 11 — that's `count <= limit` (with `limit=10`) evaluating false for the first
  time. This is the whole rate limiter: once the count exceeds the limit, every
  further call in the same window is rejected, but Redis keeps counting anyway (notice
  `count` keeps climbing past 15 rather than freezing at 11) — a real rate limiter
  usually wants to know "how far over the limit are we," which this preserves for
  free.
- `ttl` stays at `60` for every single call, never resetting or counting down between
  calls in this fast loop — that's `if count == 1: r.expire(key, window_seconds)`
  doing its job correctly: the expiry is set **once**, only on the very first call
  (when `count == 1`), and every subsequent call in the same window leaves that
  original 60-second countdown alone rather than restarting it. (If you added a
  `time.sleep(5)` between calls, you'd see `ttl` actually count down from 60 toward 0
  in real time — it looks frozen here only because the whole loop runs in a fraction
  of a second.)
- This single pattern — `INCR` to count, `EXPIRE` only when `count == 1` — is the
  entire mechanism behind a fixed-window rate limiter, and it's atomic-safe even if
  many different application servers are calling `is_allowed()` against the same
  Redis instance concurrently for the same user.

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
<details><summary>Show answer</summary>

Because only one thread ever executes commands, and it always finishes one command
completely before starting the next — there's no possibility of two commands
interleaving mid-execution against the same data, which is exactly the scenario locks
normally exist to prevent. No concurrency within command execution means no need to
guard against it.

</details>

2. What's the real cost of running `KEYS *` on a large keyspace, and what should you
   use instead?
<details><summary>Show answer</summary>

`KEYS *` scans every single key in the entire keyspace in one go, and because Redis is
single-threaded, that one command blocks all other clients' commands for its entire
duration — on a keyspace with millions of keys, that can be seconds of total
unavailability for everyone. `SCAN` solves this by walking the keyspace incrementally
across many small calls (using a cursor), letting other commands run in between each
small chunk, so no single call blocks everything else for long.

</details>

3. Which data structure would you pick for a leaderboard, and why is its insert
   O(log N) rather than O(1)?
<details><summary>Show answer</summary>

A Sorted Set (`ZADD`/`ZRANGE`) — it stores members with a score and keeps them
continuously ordered by that score, which is exactly what a leaderboard needs
("who's in 5th place right now"). It's O(log N) rather than O(1) because it's
implemented as a skip list internally, which has to find the correct sorted position
for a new/updated member — that search takes more steps as the structure grows
(logarithmically), unlike a plain hash which can drop a value in without caring about
order at all.

</details>

4. What's genuinely different about Memcached vs. Redis beyond "Redis has more
   features"?
<details><summary>Show answer</summary>

Memcached is multi-threaded for its core operations, meaning a single Memcached
instance can use multiple CPU cores directly for command processing, where a single
Redis instance is capped at one core's worth of command-execution throughput (Redis
scales further via Cluster/multiple instances instead — Week 2, Day 10). Memcached
also has no built-in persistence and no rich data structures (just plain key-value) —
a deliberately simpler design for pure caching, trading Redis's extra capability for
straightforward, cache-only multi-core throughput.

</details>

## 9. Proficiency Checkpoint

**Quick Recap:**
- **Single-threaded command execution** = no locks needed, predictable latency, but
  one slow command blocks everyone else — a deliberate trade-off, not an oversight.
- **String/List/Set/Hash/Sorted Set** — five core structures; pick based on access
  pattern (ordered by insertion? unique membership? field-value pairs? ranked by
  score?), not habit.
- **O(1)** = roughly constant time regardless of size; **O(log N)** = grows slowly with
  size — both fast, but the distinction matters for very large collections.
- **TTL** = a key that deletes itself automatically after N seconds — the first line
  of defense against unbounded memory growth.
- **Atomicity** (e.g., `INCR`) = the whole operation completes as one indivisible
  step, safe even under many concurrent clients, guaranteed for free by the
  single-threaded model.

If you can pick the right data structure for a given access pattern and explain why
single-threaded execution is a deliberate trade-off (not an oversight), you're at
Level 2.

## Next
Day 2 covers the more specialized structures — sorted sets in depth, HyperLogLog,
bitmaps, and geospatial commands — plus when each earns its keep over a plain hash/set.
