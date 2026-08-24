# Day 5: Redis — Transactions & Lua Scripting

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Implement the same atomic "decrement stock if available" operation two ways —
`WATCH`/`MULTI`/`EXEC` and a Lua script — and explain why they give different
concurrency guarantees.

## 2. Core Concept (basics → advanced)

Redis offers two distinct mechanisms for atomic multi-step operations:

- **`MULTI`/`EXEC`**: queues a batch of commands, then executes them all atomically
  (no other client's commands can interleave between them). Combined with **`WATCH`**
  on a key, this becomes **optimistic concurrency control**: you watch a key, read its
  value, decide what to do, then `MULTI`/`EXEC` your writes — but if the watched key
  changed between your `WATCH` and your `EXEC`, the whole transaction is aborted (returns
  `nil`), and your client code must retry.
- **Lua scripting (`EVAL`)**: the entire script runs atomically as a single unit,
  because Redis is single-threaded and a script blocks all other commands until it
  finishes. No `WATCH`/retry dance needed — the read-decide-write logic happens
  server-side, atomically, by construction, not by optimistic detection.

```
WATCH/MULTI/EXEC:                          Lua (EVAL):

WATCH stock:sku123        ┐                EVAL "
GET stock:sku123           │ another         local s = redis.call('GET', KEYS[1])
  (decide in client code)  │ client's        if tonumber(s) > 0 then
MULTI                      │ write here      redis.call('DECR', KEYS[1])
DECR stock:sku123          │ aborts the        return 1
EXEC ◄──────────────────── ┘ transaction     else return 0 end
                                            " 1 stock:sku123
                                            (single atomic server-side operation,
                                             no possible interleaving at all)
```

## 3. How It Really Works (Internals)

`WATCH` doesn't lock anything — it registers the key for **change detection**: Redis
tracks whether the watched key was modified (by *any* client) between the `WATCH` and
the `EXEC`. If it was, `EXEC` returns `nil` (the transaction didn't run at all), and it's
entirely the client's responsibility to detect this and retry the whole read-decide-write
cycle. Under high contention on a hot key, this can mean many wasted retries — the
classic optimistic-concurrency trade-off (cheap when contention is low, wasteful when
it's high).

Lua scripts avoid this entirely because Redis's single-threaded execution model means
the *entire script* runs as one atomic unit with no other command interleaving possible
— there's no "another client changed it in between" window at all, by construction. The
cost: a long-running or inefficient Lua script blocks the *entire* Redis instance for
its duration (since everything is single-threaded) — so Lua trades away
concurrency-safety complexity for a new discipline requirement: scripts must be fast.

## 4. Architecture & Design Pattern Spotlight

**Pattern: optimistic concurrency control (`WATCH`/`MULTI`/`EXEC`) vs. server-side
atomic execution (Lua) — the exact same trade-off database transaction isolation levels
navigate.** `WATCH` is conceptually identical to optimistic locking with a version
check in a traditional database (read version, write only if version unchanged); Lua is
closer to a stored procedure executing atomically server-side. Recognize this pattern
and you'll immediately understand equivalent mechanisms in any other datastore you
encounter.

## 5. Hands-On Lab

```python
import redis
r = redis.Redis()
r.set("stock:sku123", 10)

# Approach 1: WATCH/MULTI/EXEC with manual retry
def decrement_if_available_watch(key):
    with r.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                current = int(pipe.get(key))
                pipe.multi()
                if current > 0:
                    pipe.decr(key)
                    pipe.execute()
                    return True
                pipe.unwatch()
                return False
            except redis.WatchError:
                continue  # someone else changed it — retry

# Approach 2: Lua script, no retry logic needed at all
decrement_script = r.register_script("""
local stock = tonumber(redis.call('GET', KEYS[1]))
if stock > 0 then
    redis.call('DECR', KEYS[1])
    return 1
else
    return 0
end
""")
decrement_script(keys=["stock:sku123"])
```
Simulate contention: spin up 50 concurrent calls to each approach against the same
starting stock of 10, and confirm both correctly stop at exactly 0 (never negative) —
then compare how much retry-handling code the `WATCH` approach needed versus the Lua
approach needing none.

## 6. Real-World Product Comparison

- Redis's `WATCH` model is directly analogous to **optimistic locking in Postgres**
  (`SELECT ... FOR UPDATE` is the pessimistic alternative; a version-column check-then-
  update is the optimistic equivalent) — same fundamental trade-off, different system.
- **Lua-as-atomic-unit** is Redis's lightweight answer to what a stored procedure gives
  you in a traditional RDBMS — atomicity without needing full ACID transaction
  machinery, appropriate for Redis's much simpler data model.

## 7. Common Production Pitfalls

- Writing a `WATCH`-based flow without a retry loop — under any real contention, a
  single-attempt `WATCH`/`MULTI`/`EXEC` will fail unpredictably and silently do nothing.
- Writing a slow Lua script (e.g., one that iterates over a huge collection) — because
  Redis is single-threaded, this blocks every other client for the script's full
  duration, a very different failure mode than a slow query in a multi-threaded database.
- Assuming Lua scripts are automatically "transactions" in the SQL-ACID sense — they're
  atomic and isolated, but Redis itself doesn't have rollback semantics mid-script if
  your own script logic has a bug.

## 8. Review Questions
1. What does `WATCH` actually track, and what happens when the watched key changes?
2. Why does a Lua script not need a retry loop the way `WATCH`/`MULTI`/`EXEC` does?
3. What's the real cost of choosing Lua over `WATCH`/`MULTI`/`EXEC`?
4. How is `WATCH` analogous to optimistic locking in a traditional database?

## 9. Proficiency Checkpoint
If you can implement the same atomic operation both ways and correctly explain when
you'd choose each, you're at Level 2 moving into Level 3.

## Next
Day 6 covers Redis eviction policies — what happens when a Redis instance hits its
memory limit, and why "approximate LRU" is the actual mechanism, not textbook LRU.
