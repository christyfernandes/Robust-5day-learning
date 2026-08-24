# Day 18: Redis — Security: ACLs & TLS

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Create an ACL user restricted to a specific key prefix and command subset, and
verify both restrictions are enforced.

## 2. Core Concept (basics → advanced)

Modern Redis (v6+) supports **fine-grained ACLs** — a real evolution beyond the older
single-password model, letting you restrict a user to specific **commands** (e.g.,
only `GET`/`SET`, no `FLUSHALL` or `CONFIG`) and specific **key patterns** (e.g., only
keys matching `session:*`), rather than an all-or-nothing credential. Combined with
**TLS** for encryption-in-transit, this gives Redis a genuine authentication +
authorization security model comparable to Kafka's SASL/SSL + ACLs (today's Kafka
lesson) and ClickHouse's RBAC (today's ClickHouse lesson).

```
ACL USER app_readonly:
  Commands allowed:  GET, MGET, EXISTS  (read-only subset)
  Commands denied:   everything else, including SET, DEL, FLUSHALL

  Keys allowed:      session:*           (only this prefix)
  Keys denied:       everything else, including other apps' keyspaces
```

## 3. How It Really Works (Internals)

This is a direct extension of the durability/access concerns studied earlier this
month — a multi-tenant Redis deployment (multiple applications sharing one instance
or Cluster) benefits from exactly this kind of key-pattern scoping to prevent one
application's bug (or compromised credential) from being able to read or corrupt
another application's keyspace, the same blast-radius-containment goal as bulkheads
(Week 2, Day 13) and per-user quotas (Day 16's ClickHouse lesson), applied here at
the credential/permission level rather than the resource-consumption level.

TLS addresses a separate concern (encryption in transit, protecting data from
network-level eavesdropping) — worth keeping distinct from ACLs (which govern
what an *already-connected, authenticated* client can do), the same authentication-
vs-authorization separation as today's Kafka lesson.

## 4. Architecture & Design Pattern Spotlight

**Pattern: command/key-pattern-scoped permissions — fine-grained authorization,
directly analogous to Kafka's topic-level ACLs and ClickHouse's row-level policies
(today's other lessons).** Across all three systems, the same underlying principle
applies: default to minimal necessary permission, scoped as narrowly as the actual
use case requires, rather than broad, all-or-nothing credentials.

## 5. Hands-On Lab

```bash
redis-cli ACL SETUSER app_readonly on >somepassword \
  ~session:* \
  +get +mget +exists \
  -@all

redis-cli ACL LIST
redis-cli -u redis://app_readonly:somepassword@localhost:6379 GET session:abc123
redis-cli -u redis://app_readonly:somepassword@localhost:6379 SET other:key value
# ^ should be DENIED — command not in allowed set

redis-cli -u redis://app_readonly:somepassword@localhost:6379 GET unrelated:key
# ^ should be DENIED — key pattern not allowed
```
Confirm both restrictions independently: the command-permission denial (attempting a
disallowed command on an allowed key) and the key-pattern denial (attempting an
allowed command on a disallowed key).

## 6. Real-World Product Comparison

- **AWS ElastiCache** and **GCP Memorystore** (managed Redis offerings) both support
  and encourage this same ACL model for multi-tenant or multi-application
  deployments — a standard production practice, not an obscure feature.
- This ACL model is directly comparable to **Kafka's** and **ClickHouse's** own
  fine-grained permission systems studied today — recognizing the shared underlying
  principle (scope permissions to the minimum necessary) transfers directly across
  all three.

## 7. Common Production Pitfalls

- Running Redis with only the legacy single-password `requirepass` model in a
  genuinely multi-tenant deployment, missing the fine-grained isolation ACLs would
  provide.
- Granting overly broad command sets "to be safe" (avoiding permission errors),
  which defeats much of the value of fine-grained ACLs in the first place.
- Not enabling TLS for Redis traffic crossing untrusted network segments — ACLs
  control what an authenticated client can do, but don't protect data in transit from
  network-level interception.

## 8. Review Questions
1. What's the difference between the legacy `requirepass` model and v6+ ACLs?
2. Why are command restrictions and key-pattern restrictions independent
   dimensions of an ACL?
3. What does TLS protect against that ACLs don't, and vice versa?
4. How does this ACL model parallel Kafka's and ClickHouse's own permission systems?

## 9. Proficiency Checkpoint
If you can configure and verify a real, narrowly-scoped ACL user, you're at Level
3.5.

## Next
Day 19 covers Redis multi-region active-active replication with CRDTs — the
conflict-free approach to the same problem Kafka's active-active topology
(Week 2, Day 12) required manual conflict resolution for.
