# Day 16: ClickHouse — Cluster Tuning: HAProxy Routing & Resource Quotas

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Configure a per-user `max_memory_usage` quota and confirm it's enforced — directly
applicable to your own cluster's HAProxy-fronted architecture.

## 2. Core Concept (basics → advanced)

Your own production cluster already uses **HAProxy** as a query-routing layer in
front of the ClickHouse nodes — this plays exactly the load-balancing role from Day
15's Architecture lesson (round-robin or least-connections across ClickHouse nodes,
avoiding overloading any single node with all client traffic) — but routing is only
half the operational picture. **Resource quotas**, configured per user/role directly
in ClickHouse, govern what a *single query or user* is allowed to consume once
routed to a node: `max_memory_usage` (per-query memory ceiling),
`max_execution_time`, and broader **quotas** (rate limits on queries/rows/bytes over
a time window, applied per user).

```
Client query
     │
     ▼
HAProxy (Day 15's load-balancing pattern — routes to a healthy ClickHouse node)
     │
     ▼
ClickHouse node — enforces per-user/role resource limits:
  max_memory_usage = 10GB    ← THIS query killed if it exceeds this
  max_execution_time = 30s   ← THIS query killed if it runs longer
  QUOTA: max 1000 queries / 100GB read per hour for this user
```

## 3. How It Really Works (Internals)

HAProxy solves the **which node** question; per-user quotas solve the **how much of
that node's resources can this specific query/user consume** question — genuinely
independent layers of control, both necessary for a healthy multi-tenant cluster.
Without per-user memory/execution limits, a single poorly-written or accidentally
expensive query (perhaps a fan-out bug, Week 2 Day 9, or an unindexed full scan)
can consume enough of a node's memory to degrade or crash other concurrent queries
sharing that node — resource quotas are exactly the mechanism that turns "one bad
query" from a cluster-wide incident into a contained, single-query failure (directly
echoing Day 15's bulkhead-isolation architecture pattern, applied at the query-
resource level within a single ClickHouse node).

## 4. Architecture & Design Pattern Spotlight

**Pattern: load-balanced query routing (HAProxy) + resource governance (quotas) —
two separate, complementary control layers, precisely your own cluster's actual
architecture.** This is a direct, concrete instance of Week 2 Day 13's bulkhead
pattern: quotas isolate one user/query's resource consumption from affecting others
sharing the same node, the same fault-containment goal as a ship's bulkheads, applied
to query resource consumption rather than network calls.

## 5. Hands-On Lab

```sql
CREATE USER analytics_readonly IDENTIFIED WITH no_password
SETTINGS max_memory_usage = 5000000000, max_execution_time = 30;

CREATE QUOTA analytics_quota
FOR INTERVAL 1 HOUR MAX QUERIES 1000, MAX READ ROWS 100000000
TO analytics_readonly;

-- confirm enforcement:
-- run a deliberately memory-heavy query as this user and confirm it's killed
-- once it exceeds 5GB, with a clear "Memory limit exceeded" error
```
Verify the quota's query-count limit is enforced by running enough queries as this
user within an hour to exceed the configured threshold, and confirm ClickHouse
rejects further queries with a clear quota-exceeded error.

## 6. Real-World Product Comparison

- **BigQuery** enforces analogous per-project/per-user cost and concurrency
  controls (custom cost controls, concurrent-query limits) — the same underlying
  governance need, expressed through BigQuery's own pricing-and-quota model rather
  than ClickHouse's explicit user/role-based settings.
- This is directly the layer your team would configure to safely give broader
  analytics-team query access to the production ClickHouse cluster without risking
  one team's expensive ad hoc query degrading service for others — a concrete,
  immediately applicable governance mechanism for your migration's rollout plan.

## 7. Common Production Pitfalls

- Relying on HAProxy alone for cluster health, without per-user resource quotas —
  routing traffic evenly across nodes doesn't prevent one expensive query from
  degrading whichever node it lands on.
- Setting quotas too permissively "to avoid blocking legitimate work," effectively
  making them meaningless as a protective mechanism.
- Not testing quota enforcement before relying on it — confirming the expected
  behavior (a clear, actionable error) rather than assuming configuration syntax is
  correct.

## 8. Review Questions
1. What's the precise division of responsibility between HAProxy and per-user
   quotas in your own cluster's architecture?
2. Why do resource quotas function as a bulkhead pattern within a single ClickHouse
   node?
3. What real production problem (from earlier this month) would per-user memory
   limits have directly contained?
4. Why is testing quota enforcement, not just configuring it, an essential step?

## 9. Proficiency Checkpoint
If you can configure and verify per-user resource governance on your own cluster
architecture, you're at Level 3.5 — directly deployable for safely expanding
analytics-team access as part of your migration rollout.

## Next
Day 17 covers ClickHouse system-table monitoring — `system.parts`/`system.merges`/
`system.replicas` — for ongoing cluster health observability.
