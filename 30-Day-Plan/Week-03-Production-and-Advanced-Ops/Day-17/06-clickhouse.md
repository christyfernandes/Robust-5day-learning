# Day 17: ClickHouse — Monitoring: System Tables & Grafana Dashboards

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Query `system.parts` to find a table with too many active parts — a common,
directly actionable performance symptom on your own cluster.

## 2. Core Concept (basics → advanced)

ClickHouse exposes its entire operational state through queryable **system
tables** — genuinely just regular tables you `SELECT` from, using the exact same SQL
skills studied all month, rather than a separate monitoring API/protocol:

- **`system.parts`**: every data part per table, per replica — directly surfaces
  the too-many-parts issue from Day 15.
- **`system.merges`**: currently in-progress background merges — useful for seeing
  whether merge activity is keeping up with insert rate, or falling behind.
- **`system.replicas`**: per-table replication status — `is_leader`,
  `absolute_delay` (how far behind a replica is), directly extending Week 1 Day 5's
  replication lesson into an observable, queryable health signal.

## 3. How It Really Works (Internals)

Because these are genuinely queryable tables, you can build arbitrarily
sophisticated monitoring **using SQL you already know** — a Grafana dashboard backed
by ClickHouse system-table queries is, under the hood, just periodic `SELECT`
statements against `system.parts`/`system.merges`/`system.replicas` (and others,
like `system.query_log` from Day 15), visualized over time. This is a genuine
operational advantage over systems requiring a separate monitoring protocol/API
surface — the same skill (writing a `SELECT` against a system table) that lets you
investigate a one-off performance question (Day 15) also builds your standing
dashboards.

## 4. Architecture & Design Pattern Spotlight

**Pattern: system-table-driven observability — monitoring infrastructure expressed
as ordinary queries against the same query engine being monitored.** This is a
genuinely elegant design choice, and worth contrasting explicitly with
Elasticsearch's separate `_cluster/health` and `hot_threads` REST APIs (today's
Elasticsearch lesson) — both approaches solve the same observability need, but
ClickHouse's system-tables approach means "how do I monitor X" and "how do I query
X" are, for a SQL-fluent team, literally the same skill.

## 5. Hands-On Lab

```sql
-- find tables with too many active parts (Day 15's too-many-parts symptom)
SELECT table, count() AS active_parts
FROM system.parts WHERE active
GROUP BY table
ORDER BY active_parts DESC LIMIT 10;

-- check merge activity keeping pace with inserts
SELECT * FROM system.merges;

-- check replication health/lag
SELECT database, table, is_leader, absolute_delay, queue_size
FROM system.replicas
ORDER BY absolute_delay DESC;
```
Run these against your real cluster. If any table shows a high active-part count,
cross-reference with `system.merges` to see whether merges are actively working on
that table right now, or whether merge activity appears stalled — a distinct,
differently-actionable finding.

## 6. Real-World Product Comparison

- The standard **ClickHouse + Grafana** monitoring stack (widely documented and
  used in production ClickHouse deployments) is built entirely on periodic queries
  against exactly these system tables — this is not a niche approach but the
  standard operational pattern your team would adopt post-migration.
- Contrast with **BigQuery**, which as a fully-managed service exposes much less
  of this operational detail directly to users — another concrete example of the
  "more control, more operational responsibility" trade-off inherent in your
  self-hosted migration.

## 7. Common Production Pitfalls

- Not building standing dashboards from these system tables, relying only on
  reactive, manual queries during an active incident.
- Finding a too-many-parts table without checking `system.merges` to understand
  *why* merges aren't keeping pace — the fix differs depending on whether it's an
  insert-batching problem (Day 15) or a genuine merge-throughput capacity issue.
- Not monitoring `system.replicas`' `absolute_delay` continuously — a
  growing replication delay is an early warning of a replica falling behind, well
  before it becomes a bigger consistency or availability concern.

## 8. Review Questions
1. Why is ClickHouse's system-table approach to monitoring architecturally
   different from Elasticsearch's REST-API approach?
2. What specifically would you check to distinguish an insert-batching cause from a
   merge-capacity cause for a too-many-parts finding?
3. What does `system.replicas`' `absolute_delay` measure, and why does it matter?
4. Why is this monitoring approach a genuine operational advantage for a SQL-fluent
   team specifically?

## 9. Proficiency Checkpoint
If you can build a real diagnostic query set against your own cluster's system
tables and correctly interpret the results, you're at Level 3.5 — this is your
actual production monitoring toolkit going forward.

## Next
Day 18 covers ClickHouse security — RBAC and row-level security policies — relevant
for multi-tenant analytics team access on your cluster.
