# Day 17: Redis — Monitoring: INFO, LATENCY HISTORY & Redis Insight

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Parse `INFO memory` and `INFO stats` output and identify three specific, actionable
fields for ongoing health monitoring.

## 2. Core Concept (basics → advanced)

Redis's built-in `INFO` command is a comprehensive, self-reporting health dump,
organized into sections — `INFO memory` (memory usage, fragmentation ratio, Week 1
Day 6), `INFO stats` (commands processed, keyspace hits/misses, evicted keys, Week 1
Day 6), `INFO replication` (replica status, lag, Week 2 Day 8), and more. **`LATENCY
HISTORY`** (paired with `LATENCY MONITOR`, enabled via `latency-monitor-threshold`)
records specific slow events by category, complementing `SLOWLOG`'s
command-level view (Day 15) with a broader latency-spike view across different
subsystems (fork operations, expire cycles, command execution).

## 3. How It Really Works (Internals)

Three fields worth specifically watching, each tying back to earlier lessons:
- **`mem_fragmentation_ratio`** (Week 1, Day 6): sustained values well above 1
  indicate real fragmentation overhead, worth investigating (or triggering active
  defragmentation) before it silently inflates required capacity.
- **`keyspace_hits` / `keyspace_misses`** (Week 2, Day 11's caching-pattern lesson):
  a rising miss ratio for a cache-aside workload can indicate either genuinely
  changing access patterns or a cache-invalidation bug causing unnecessary misses —
  directly actionable for exactly the cache-bypass investigation theme from earlier
  this curriculum.
- **`evicted_keys`** (Week 1, Day 6): a rapidly climbing count under a
  `maxmemory`-limited instance indicates memory pressure that may need capacity
  planning attention, or may indicate the eviction policy is actively (and
  correctly) doing its job — context (is this expected, steady-state eviction or a
  new, unexpected trend) determines which.

## 4. Architecture & Design Pattern Spotlight

**Pattern: built-in self-reporting — Redis exposing its own detailed operational
state directly, rather than requiring external instrumentation to observe basic
health.** This is a genuinely convenient design choice worth appreciating in
contrast to systems (some of what you'll compare in Week 4) that require more
external tooling to get equivalent visibility — but self-reporting is only useful if
someone is actually watching it, which is precisely why wiring `INFO` output into a
standing dashboard (Redis Insight, or a Prometheus exporter) matters more than the
data being technically available on request.

## 5. Hands-On Lab

```bash
redis-cli INFO memory | grep -E "used_memory:|used_memory_rss:|mem_fragmentation_ratio:"
redis-cli INFO stats | grep -E "keyspace_hits:|keyspace_misses:|evicted_keys:|expired_keys:"

redis-cli CONFIG SET latency-monitor-threshold 100
# ... generate some load, including a deliberately slow operation ...
redis-cli LATENCY HISTORY command
redis-cli LATENCY LATEST
```
Compute your instance's actual hit ratio (`keyspace_hits / (keyspace_hits +
keyspace_misses)`) and fragmentation ratio directly from real output, and write down
what specific action (if any) each value's current level would prompt you to take.

## 6. Real-World Product Comparison

- **Redis Insight** (Redis's own official GUI) visualizes exactly this `INFO`-sourced
  data plus additional profiling tools, aimed at making this monitoring accessible
  without needing to parse raw `INFO` output manually.
- Production Redis monitoring commonly exports these exact fields to
  **Prometheus/Grafana** via the `redis_exporter` project — the same
  monitoring-stack pattern used for Kafka (Day 17) and Flink (today), reinforcing
  that this observability stack composition is a general practice, not
  system-specific.

## 7. Common Production Pitfalls

- Treating `INFO` as a diagnostic tool to check only during an incident, rather than
  wiring key fields into standing dashboards/alerts.
- Not distinguishing "expected steady-state eviction" from "a new, concerning
  eviction trend" — the same raw number needs contextual interpretation.
- Ignoring `mem_fragmentation_ratio` until it's already severe — proactive
  monitoring catches the trend before active defragmentation becomes urgently
  necessary.

## 8. Review Questions
1. What are the three specific fields highlighted today, and what does each
   indicate?
2. Why is Redis's built-in self-reporting only as useful as the monitoring wired
   around it?
3. How does `LATENCY HISTORY` complement `SLOWLOG`'s view?
4. Why does the same raw eviction-count number require contextual interpretation?

## 9. Proficiency Checkpoint
If you can identify actionable signals from real `INFO` output and explain what each
would prompt you to do, you're at Level 3.5.

## Next
Day 18 covers Redis security — ACLs and TLS — access control for the instance you're
now monitoring effectively.
