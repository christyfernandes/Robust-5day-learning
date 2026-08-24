# Day 13: Redis — Modern Alternatives: DragonflyDB, Valkey, KeyDB

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Benchmark the same workload against Redis and DragonflyDB with `redis-benchmark`, and
explain the architectural difference that produces any observed performance gap.

## 2. Core Concept (basics → advanced)

Redis's single-threaded execution model (Week 1, Day 1) is simple and avoids entire
classes of concurrency bugs, but means a single Redis instance can only use **one CPU
core** for command execution, regardless of how many cores the host machine has —
scaling beyond one core's throughput traditionally required Cluster/sharding (Week 2,
Day 10), not a bigger single instance.

Several projects address this directly while remaining API-compatible (a drop-in
replacement from the client's point of view):
- **DragonflyDB**: a from-scratch reimplementation using a genuinely
  **multi-threaded, shared-nothing architecture** — capable of using multiple cores
  within a single instance, while implementing the Redis (and Memcached) wire protocol
  for compatibility with existing clients.
- **Valkey**: a community-governed fork of Redis itself (created after Redis's
  license change away from a fully open-source license), maintaining close alignment
  with Redis's own codebase and roadmap.
- **KeyDB**: an earlier multi-threaded Redis fork, also aiming for API compatibility
  with better multi-core utilization than stock Redis.

## 3. How It Really Works (Internals)

DragonflyDB's multi-threaded design specifically avoids the classic problem
multi-threading usually introduces (lock contention on shared data structures) by
using a **shared-nothing** architecture internally — each thread owns a disjoint
subset of the keyspace, similar in spirit to how Redis Cluster shards across separate
*instances* (Week 2, Day 10), except here the "shards" are threads within a single
process rather than separate Cluster nodes, meaning you get better multi-core
utilization without the operational overhead of a multi-node Cluster deployment for
workloads that don't need multi-node scale but do need more than one core's worth of
throughput.

For your team's actual DragonflyDB evaluation, this maps to a very specific question:
does your Redis workload's bottleneck come from single-core CPU saturation (in which
case DragonflyDB's architecture directly addresses it) or from something else
entirely (network bandwidth, memory capacity, or a workload shape — like very large
values — that doesn't particularly benefit from more cores)? The benchmark in today's
lab is how you'd actually answer that, rather than assuming a multi-threaded
alternative automatically helps.

## 4. Architecture & Design Pattern Spotlight

**Pattern: multi-threaded, API-compatible reimplementation — solving a single-node
scaling ceiling without requiring clients to change anything, by preserving the wire
protocol while replacing the internal execution model.** This is a distinct strategy
from horizontal scaling (Redis Cluster, Week 2 Day 10) — vertical, single-node
multi-core utilization vs. horizontal, multi-node distribution are two different
scaling axes, and DragonflyDB specifically targets the vertical axis.

## 5. Hands-On Lab

```bash
# Redis baseline
redis-benchmark -h localhost -p 6379 -t set,get -n 1000000 -c 50 -P 16

# DragonflyDB (same protocol, different port/instance)
redis-benchmark -h localhost -p 6380 -t set,get -n 1000000 -c 50 -P 16
```
Run both against instances with comparable memory/CPU allocation, and compare
requests/sec directly. Then check CPU utilization *during* each benchmark
(`top`/`htop`) — confirm whether Redis is saturating a single core while DragonflyDB
spreads load across multiple cores, which is the actual mechanism behind any
throughput difference you observe (rather than treating the benchmark number as an
unexplained black box).

## 6. Real-World Product Comparison

- This is **directly** the evaluation your own cost/performance work has already
  flagged DragonflyDB for — today's lab produces a real, quantified data point for
  that ongoing evaluation, tied to an explicit architectural explanation rather than
  just a benchmark headline number.
- **Valkey**'s emergence (community fork after Redis's licensing change) is worth
  tracking for a different reason than DragonflyDB — it's not primarily a
  performance play but a governance/licensing one, relevant to your evaluation for
  different reasons (licensing terms, long-term community backing) than the
  throughput question DragonflyDB addresses.

## 7. Common Production Pitfalls

- Adopting a multi-threaded alternative based on published benchmarks alone, without
  validating against your *own* actual workload shape (value sizes, command mix,
  connection concurrency) — published benchmarks often use configurations that don't
  match a specific production workload.
- Not accounting for operational maturity/tooling differences when evaluating a
  newer alternative — raw performance is one dimension; monitoring integrations,
  operational runbooks, and team familiarity are real switching costs too.
- Assuming API compatibility means *complete* behavioral compatibility — subtle
  differences in edge-case command behavior or configuration semantics can exist even
  between wire-protocol-compatible implementations; validate anything your
  application depends on precisely.

## 8. Review Questions
1. What specifically limits stock Redis to one CPU core, architecturally?
2. How does DragonflyDB's shared-nothing multi-threading avoid lock contention?
3. What question should you answer *before* assuming a multi-threaded alternative
   will help your specific workload?
4. Why is Valkey's motivation different in kind from DragonflyDB's?

## 9. Proficiency Checkpoint
If you can run a real, apples-to-apples benchmark and explain the architectural
reason behind any observed difference, you're at Level 3 — directly useful for your
team's actual evaluation.

## Next
Day 14 is this week's integrated lab and review, benchmarking DragonflyDB against
Redis as one of its concrete deliverables.
