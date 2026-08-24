# Day 18: Elasticsearch — Security: RBAC & Field/Document-Level Security

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Restrict a role to see only documents matching a filter, and hide one field entirely
— fine-grained access control beyond simple index-level permissions.

## 2. Core Concept (basics → advanced)

Elasticsearch's RBAC operates at multiple granularities, each solving a different
access-control need:
- **Index-level**: which indices a role can access at all (the coarsest level).
- **Document-level security (DLS)**: a role can only see documents matching a
  specified query filter, even within an index it otherwise has access to — e.g.,
  a sales rep role that can only see documents where `region` matches their own
  assigned region.
- **Field-level security (FLS)**: specific fields are hidden from a role entirely,
  even for documents the role can otherwise see — e.g., hiding a `salary` field from
  a general HR-reporting role while still allowing access to the rest of an
  employee document.

```
Full document:  { name: "Alice", region: "EMEA", salary: 95000, department: "Eng" }

Role with DLS (region=EMEA) + FLS (hide salary):
  Sees this document (region matches) AND
  Sees: { name: "Alice", region: "EMEA", department: "Eng" }  ← salary HIDDEN
```

## 3. How It Really Works (Internals)

DLS is implemented by transparently injecting the role's filter into every query
that role issues — the *query itself* is silently rewritten to `AND` the DLS filter
onto whatever the user actually searched for, meaning DLS is enforced consistently
regardless of how creatively a user constructs their query (they can't bypass it by
phrasing a query cleverly, since the filter is applied at the layer beneath their
query, not as a client-side check). FLS works similarly at the field level, stripping
restricted fields from the response after the query executes, regardless of whether
the user explicitly requested that field or asked for `_source: true` broadly.

This connects directly to Week 2 Day 10's CQRS lesson: DLS/FLS let you serve
*different read-model views of the same underlying index* to different roles,
without needing to maintain physically separate indices per audience — a more
efficient variant of the same "different consumers, different views" idea.

## 4. Architecture & Design Pattern Spotlight

**Pattern: fine-grained access control below the index level — document-level and
field-level, enforced transparently at query time.** This is the Elasticsearch-
specific instance of the same access-control granularity spectrum studied today in
Kafka (topic-level ACLs), Redis (command/key-pattern ACLs), and ClickHouse
(row-level policies) — recognizing that "how granular does access control need to
be" is a question every one of these systems answers with its own specific
mechanism, all serving the same underlying multi-tenancy/least-privilege goal.

## 5. Hands-On Lab

```json
POST /_security/role/emea_sales_readonly
{
  "indices": [{
    "names": ["employees"],
    "privileges": ["read"],
    "field_security": { "grant": ["name", "region", "department"] },
    "query": { "term": { "region": "EMEA" } }
  }]
}
```
Create a test user with this role, index a few documents spanning different
regions and including a `salary` field, and confirm: the role only ever sees `region:
EMEA` documents (DLS enforced), and the `salary` field never appears in any response
for this role (FLS enforced), even if explicitly requested.

## 6. Real-World Product Comparison

- **Multi-tenant SaaS platforms** built on Elasticsearch commonly use DLS to give
  each tenant a filtered view of a shared index (rather than maintaining one index
  per tenant, which doesn't scale well past a certain tenant count) — a direct,
  common production use of exactly this mechanism.
- This maps directly onto a genuine future need for your **MDO portal** — if
  broader analytics-team access to underlying data (BigQuery/ClickHouse today, or
  potentially an Elasticsearch layer in the future) needs row/field-level
  restriction by team or tenant, this is the mechanism family (alongside
  ClickHouse's row-level policies, today's lesson) to reach for.

## 7. Common Production Pitfalls

- Assuming index-level access control alone is sufficient when the actual
  requirement is per-tenant or per-role document filtering — DLS exists precisely
  because index-level granularity is often too coarse.
- Forgetting that FLS must be applied consistently across every role that
  shouldn't see a sensitive field — a single role misconfigured without the FLS
  restriction defeats the protection for anyone assigned that role.
- Not testing DLS/FLS with the actual query patterns real users will issue —
  confirming the filter is transparently applied regardless of query complexity,
  not just for a simple test query.

## 8. Review Questions
1. What's the difference between index-level, document-level, and field-level
   security?
2. Why can't a user bypass DLS by constructing a clever query?
3. How does DLS/FLS relate to the CQRS "different views for different consumers"
   idea from Week 2?
4. How does this compare to ClickHouse's row-level security policies (today's other
   lesson)?

## 9. Proficiency Checkpoint
If you can configure and verify real DLS and FLS restrictions together, you're at
Level 3.5.

## Next
Day 19 covers Elasticsearch resiliency — split-brain prevention and snapshot/restore
— the next layer of production hardening.
