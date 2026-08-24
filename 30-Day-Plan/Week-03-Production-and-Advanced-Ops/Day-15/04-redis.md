# Day 15: Redis — Pipelining, Slow-Log & Big-Key Detection

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Use `redis-cli --bigkeys` and `SLOWLOG GET` on a populated instance to find real
performance issues, and explain why pipelining reduces round-trip overhead.

## 2. Core Concept (basics → advanced)

**Pipelining** sends multiple commands to Redis without waiting for each individual
response before sending the next — the client batches requests, the server processes
them in order, and responses come back as one batch. Since Redis's actual command
execution is extremely fast (Week 1, Day 1's single-threaded reactor model), the
dominant cost for many small operations is often **network round-trip time**, not
command execution itself — pipelining amortizes that round-trip cost across many
commands, similar in spirit to Kafka's batching trade-off (Week 2, Day 11), though
here there's no latency cost being traded away, since pipelining doesn't need to
*wait* to accumulate a batch the way Kafka's `linger.ms` does.

**`SLOWLOG`** records commands that exceeded a configurable execution-time threshold
— given Redis's single-threaded model, **any** slow command blocks every other client
for its duration (Week 1, Day 5's Lua-scripting lesson made this point about scripts
specifically; it applies to any slow command generally, including operations on large
collections). **Big-key detection** (`redis-cli --bigkeys`, or `MEMORY USAGE` on
suspect keys) finds keys whose size makes basic operations on them disproportionately
expensive — a single very large hash, set, or sorted set can dominate memory usage and
turn ordinarily-cheap-looking operations into slow ones.

## 3. How It Really Works (Internals)

A "hot key" (very frequently accessed) and a "big key" (very large in size) are
related but distinct problems: a hot key concentrates *request volume* on one piece
of data (a potential bottleneck even if the key itself is small), while a big key
concentrates *data size* and makes even infrequent operations on it comparatively
expensive (e.g., a full scan of a large sorted set). Both show up in
`redis-cli --bigkeys`'s sampling scan (which finds the largest keys per data type) and
in `SLOWLOG` (which surfaces the actual slow commands, whatever their cause) — using
both together triangulates whether a specific performance issue traces to key size,
access pattern, or command choice.

## 4. Architecture & Design Pattern Spotlight

**Pattern: round-trip reduction via batching (pipelining) — the same underlying
efficiency idea as Kafka producer batching (Week 2, Day 11), applied without a
latency-for-throughput trade-off since Redis pipelining doesn't need to "wait to
accumulate."** Recognizing when round-trip overhead, rather than actual work, is the
real bottleneck is a widely-applicable diagnostic skill across many systems, not
just Redis.

## 5. Hands-On Lab

```bash
# populate a test instance with varied key sizes, including a few deliberately large ones
redis-cli --bigkeys

# find slow commands
redis-cli CONFIG SET slowlog-log-slower-than 10000   # 10ms threshold, for testing
redis-cli SLOWLOG GET 10
redis-cli SLOWLOG RESET
```
Then measure pipelining's effect directly:
```python
import redis, time
r = redis.Redis()

start = time.time()
for i in range(10000):
    r.set(f"key:{i}", i)          # one round trip per command
print("Without pipeline:", time.time() - start)

start = time.time()
pipe = r.pipeline()
for i in range(10000):
    pipe.set(f"key:{i}", i)       # batched — ONE round trip for all 10000
pipe.execute()
print("With pipeline:", time.time() - start)
```
Compare the timings directly — quantify the round-trip-overhead reduction.

## 6. Real-World Product Comparison

- Large-scale Redis operators (GitHub, Twitter-era Redis usage) run `--bigkeys` scans
  and `SLOWLOG` monitoring as routine, ongoing operational hygiene — not a one-time
  diagnostic, since key-size and access-pattern issues tend to emerge gradually as an
  application evolves.
- Pipelining is standard practice in any Redis client library used for bulk
  operations — most production Redis client code doing more than a handful of
  operations at once should be pipelining by default.

## 7. Common Production Pitfalls

- Not pipelining bulk operations, paying unnecessary round-trip latency for
  workloads doing hundreds or thousands of small operations.
- Ignoring `SLOWLOG` until a performance incident forces investigation — proactive,
  periodic review catches emerging big-key or slow-command issues before they become
  incidents.
- Storing genuinely large collections in a single key without considering whether
  splitting across multiple keys (or a different data structure) would avoid the
  big-key problem structurally.

## 8. Review Questions
1. Why does pipelining help even though Redis itself executes commands very fast?
2. What's the practical difference between a hot key and a big key?
3. Why does Redis's single-threaded model make `SLOWLOG` monitoring especially
   important?
4. How would you use `--bigkeys` and `SLOWLOG` together to triangulate a real
   performance issue?

## 9. Proficiency Checkpoint
If you can find and correctly diagnose a real big-key or slow-command issue using
these tools, you're at Level 3.5.

## Next
Day 16 covers memory optimization via compact encodings (`ziplist`/`listpack`) —
directly related to today's big-key investigation.
