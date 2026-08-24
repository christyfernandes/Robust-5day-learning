# Day 18: Kafka — Security: SASL/SSL & ACLs

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Configure a topic-level ACL restricting one principal to read-only access, and
explain the distinction between authentication and authorization.

## 2. Core Concept (basics → advanced)

Two genuinely separate security layers, easy to conflate but solving different
problems:
- **Authentication (SASL/SSL)**: *who are you* — verifying a client's identity
  before allowing any connection at all. **SSL/TLS** (mutual TLS, specifically)
  authenticates via certificates; **SASL** supports various mechanisms (SCRAM,
  Kerberos/GSSAPI, OAuth) for username/password or token-based authentication.
- **Authorization (ACLs)**: *what are you allowed to do, now that we know who you
  are* — Access Control Lists specify which authenticated principals can perform
  which operations (read, write, create, describe) on which specific resources
  (topics, consumer groups, the cluster itself).

```
Client connects ──▶ SASL/SSL: "prove who you are" ──▶ AUTHENTICATED as principal X
                                                              │
                                                              ▼
                                    ACL check: "is principal X allowed to
                                     READ topic 'orders'?" ──▶ AUTHORIZED or DENIED
```

## 3. How It Really Works (Internals)

These layers are independently configurable and independently necessary — a client
can be perfectly authenticated (Kafka knows exactly who they are) and still be
denied every operation if no ACL grants them permission (the default-deny posture
most production clusters should run with, rather than default-allow). This
two-layer separation (identity, then permission) is the same structural pattern as
Elasticsearch's RBAC (today's Elasticsearch lesson) and ClickHouse's RBAC (today's
ClickHouse lesson) — worth recognizing as one recurring security architecture
pattern applied consistently across every system this curriculum studies, not three
unrelated configuration systems to memorize separately.

## 4. Architecture & Design Pattern Spotlight

**Pattern: authentication + authorization as two separate, composable layers.**
This maps directly onto the general **zero trust** framing from today's Architecture
lesson — never assume a connection is trustworthy by network location alone; always
verify identity explicitly (authentication), and never assume identity implies
unlimited permission (authorization) — both checks, every time, for every operation.

## 5. Hands-On Lab

```bash
# server.properties: enable SASL_SSL listener with SCRAM
# (full broker-side SASL/SSL setup is involved; today's lab focuses on the ACL layer,
#  assuming authentication is already configured)

kafka-acls.sh --bootstrap-server localhost:9092 --command-config admin.properties \
  --add --allow-principal User:readonly-app \
  --operation Read --topic orders

kafka-acls.sh --bootstrap-server localhost:9092 --command-config admin.properties \
  --list --topic orders
```
Confirm the `readonly-app` principal can consume from `orders` but is denied when
attempting to produce to it — verify the specific denial error, and confirm it's an
authorization failure (identity accepted, operation denied), not an authentication
failure (identity rejected outright).

## 6. Real-World Product Comparison

- **Confluent's RBAC** (built on top of ACLs) offers role-based grouping of
  permissions for easier management at scale — the same underlying ACL mechanism,
  wrapped in more manageable role abstractions once permission counts grow large.
- Every serious production Kafka deployment runs with authentication enabled and a
  default-deny ACL posture — an unauthenticated, unrestricted Kafka cluster
  (acceptable for local development, as used throughout this curriculum) is a
  genuine security risk in any real production environment.

## 7. Common Production Pitfalls

- Conflating "authenticated" with "authorized" when debugging an access issue —
  the fix for each is completely different (authentication config vs. ACL grants).
- Running with a default-allow ACL posture "for convenience," effectively
  negating the value of having authentication at all.
- Not auditing ACLs periodically as team membership and topic ownership change —
  stale, overly broad grants accumulate over time without active review.

## 8. Review Questions
1. What's the precise difference between authentication and authorization?
2. Why can a client be authenticated but still denied every operation?
3. How does this two-layer pattern recur in Elasticsearch's and ClickHouse's
   security models?
4. Why is default-deny (rather than default-allow) the safer starting posture?

## 9. Proficiency Checkpoint
If you can configure and verify a real topic-level ACL and correctly distinguish
authentication from authorization failures, you're at Level 3.5.

## Next
Day 19 covers Kafka disaster recovery and multi-region geo-replication patterns —
building on MirrorMaker 2 from Week 2.
