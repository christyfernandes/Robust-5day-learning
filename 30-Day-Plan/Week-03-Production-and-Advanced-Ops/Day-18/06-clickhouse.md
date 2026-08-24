# Day 18: ClickHouse — Security: RBAC & Row-Level Security Policies

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Define a row policy restricting a role to one tenant's data, and verify it's
enforced transparently — directly relevant to opening up multi-tenant analytics
access on your own cluster.

## 2. Core Concept (basics → advanced)

ClickHouse's RBAC combines familiar pieces (users, roles, grants on
databases/tables — Week 3 Day 16's quota lesson already introduced per-user
settings) with **row policies**: a filter attached to a table that's automatically
applied to every query a given role issues against it — structurally identical to
Elasticsearch's document-level security (today's Elasticsearch lesson), applied to
ClickHouse's table/row model instead of Elasticsearch's document model.

```sql
CREATE ROW POLICY tenant_isolation ON events
USING org_id = currentUser()::UInt32   -- or a lookup mapping user → allowed org_id
TO analytics_tenant_role;

-- any query this role issues against `events` automatically gets
-- "AND org_id = <this role's assigned org_id>" appended, transparently
```

## 3. How It Really Works (Internals)

Like Elasticsearch's DLS, the row policy is enforced **at the query-planning level**,
not as an application-side filter the client could omit or bypass — a role with a row
policy attached cannot see rows outside the policy's filter regardless of how the
query is phrased, since the filter is injected into the query plan itself before
execution. This is precisely the mechanism that would let you **safely expand
ClickHouse access to your broader analytics team** post-migration — giving different
teams query access to a shared `events` table while guaranteeing (structurally, not
by convention) that each team only ever sees their own tenant's/org's data, without
needing to maintain separate physical tables or databases per team.

Combined with Day 16's per-user quotas (resource governance) and standard grants
(table/column access), row policies complete the three-layer access-control picture
your migration's broader rollout plan needs: **what tables can this role touch**
(grants), **which specific rows within those tables** (row policies), and **how
much resource can this role consume** (quotas) — three independent, composable
controls.

## 4. Architecture & Design Pattern Spotlight

**Pattern: row-level access control — the ClickHouse-specific instance of the same
document-level security concept studied today in Elasticsearch, and conceptually
related to Redis's key-pattern ACLs and Kafka's topic ACLs.** By now you've seen this
exact "restrict visibility to a subset matching the requester's identity" pattern
implemented four different ways across four different systems this month — recognize
it as one general access-control principle with system-specific implementations,
not four unrelated features to memorize separately.

## 5. Hands-On Lab

```sql
CREATE ROLE tenant_a_analyst;
CREATE ROW POLICY tenant_a_policy ON events
USING org_id = 42
TO tenant_a_analyst;

GRANT SELECT ON events TO tenant_a_analyst;

CREATE USER analyst1 IDENTIFIED WITH no_password DEFAULT ROLE tenant_a_analyst;
```
As `analyst1`, run `SELECT DISTINCT org_id FROM events` and confirm **only** `42`
appears in results, regardless of how many other org_ids exist in the underlying
table — try a few different query shapes (aggregations, joins involving `events`) to
confirm the policy is enforced consistently, not just for a simple `SELECT *`.

## 6. Real-World Product Comparison

- **Snowflake** and **BigQuery** both offer analogous row-level security features
  (row access policies, row-level security policies respectively) — the same
  underlying multi-tenant data-governance need exists across every major analytical
  platform, ClickHouse included.
- This is directly the mechanism your team would use to responsibly expand
  ClickHouse access beyond the current data-engineering team to broader analytics
  stakeholders as part of your migration's rollout — a concrete, immediately
  applicable governance tool for exactly the access-expansion conversation likely to
  come up post-migration.

## 7. Common Production Pitfalls

- Relying on application-level filtering (trusting client code to always add the
  right `WHERE org_id = ...` clause) instead of a database-enforced row policy — a
  single application bug or ad hoc query tool bypasses application-level filtering
  entirely, while a row policy cannot be bypassed this way.
- Not testing row policies against realistic query shapes (joins, subqueries,
  aggregations) — confirming enforcement only against a trivial `SELECT *` and
  assuming it generalizes.
- Combining row policies with quotas and grants without documenting the full
  three-layer access model for each role — as the number of roles grows, undocumented
  overlapping policies become hard to reason about correctly.

## 8. Review Questions
1. Why is a row policy enforced at query-planning time rather than as an
   application-side filter?
2. What three independent, composable access-control layers does ClickHouse RBAC
   provide together?
3. How is this the same underlying pattern as Elasticsearch's document-level
   security?
4. Why is application-level filtering alone an insufficient substitute for a row
   policy?

## 9. Proficiency Checkpoint
If you can configure and verify a real row policy across multiple query shapes,
you're at Level 3.5 — directly deployable for safely expanding your cluster's
analytics-team access.

## Next
Day 19 covers ClickHouse backup and disaster recovery — `clickhouse-backup` and
replica-based DR strategies.
