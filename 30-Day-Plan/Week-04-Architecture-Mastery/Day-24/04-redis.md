# Day 24: Redis — When NOT to Use It

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Write the one sentence you'd say in a design review when someone proposes
Redis for the wrong job.

## 2. Core Concept (basics → advanced)

Redis's in-memory architecture (Week 1, Day 1) is a poor fit for:
- **Durability-critical primary storage without deliberate configuration**:
  Week 2, Day 12 covered exactly what it takes to trust Redis as a primary
  store — if that configuration work (AOF, replication quorums, tested
  backup/restore) isn't actually done, using Redis as an unconfigured primary
  store for critical data is a real risk, not a reasonable default.
- **Datasets far exceeding RAM economics**: Redis's whole performance profile
  depends on data fitting in memory — a dataset that would require an
  enormous, expensive RAM footprint to hold entirely in Redis is often
  better served by a disk-based store (or a hybrid, cache-in-front-of-disk
  architecture, Week 2 Day 11's caching patterns) rather than forcing
  everything into RAM at high cost.

## 3. How It Really Works (Internals)

The correct mental test: **is this data's access pattern genuinely
latency-critical and small enough to justify RAM economics, or would a
disk-based store with Redis as a cache layer in front of it (rather than the
primary store) serve the actual requirement more cost-effectively?**

## 4. Architecture & Design Pattern Spotlight

**Pattern: matching tool architecture to actual problem shape — RAM-based
storage's cost/performance trade-off only makes sense for data and access
patterns that actually benefit from it.**

## 5. Hands-On Lab

Write the one sentence you'd say in a design review when someone proposes
storing a very large, infrequently-accessed dataset entirely in Redis rather
than in a cheaper disk-based store with selective caching.

## 6. Real-World Product Comparison

- **Memcached**: simpler, if you genuinely only need a cache with no advanced
  data structures or persistence — sometimes the right, simpler choice when
  Redis's additional capability (Streams, Pub/Sub, Lua) isn't needed.
- **DragonflyDB** (Week 2, Day 13): worth evaluating specifically for
  throughput-bound Redis-API workloads, not as a universal Redis replacement.
- **An embedded cache** (in-process, no network hop) is the right choice when
  even Redis's latency is unnecessary overhead for a single-application cache
  need.

## 7. Common Production Pitfalls

- Using Redis as an unconfigured primary store for genuinely critical data,
  without the Week 2 Day 12 durability discipline actually in place.
- Storing a dataset in Redis that's large enough to make RAM cost
  disproportionate to the actual latency benefit gained.

## 8. Review Questions
1. What specific configuration work does trusting Redis as a primary store
   require?
2. When does RAM-based storage stop making economic sense?
3. What's your one-sentence design-review pushback?
4. When would Memcached or an embedded cache be the better fit than Redis?

## 9. Proficiency Checkpoint
If you have a real, specific pushback ready, you're at Level 4.

## Next
Day 25 applies this judgment directly to designing your MDO-portal cache-bypass
fix.
