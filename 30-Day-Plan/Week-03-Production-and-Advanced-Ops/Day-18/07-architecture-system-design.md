# Day 18: Architecture — Security Architecture: Zero Trust & Defense in Depth

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Map your own platform's current trust boundaries — who can reach what, directly —
and identify where zero-trust principles are and aren't currently applied.

## 2. Core Concept (basics → advanced)

**Zero trust** rejects the traditional "trusted internal network, untrusted
external network" model — instead, every request is authenticated and authorized
explicitly, regardless of whether it originates from inside or outside a
traditionally-trusted network boundary. This is precisely the authentication +
authorization discipline studied today across Kafka, Redis, Elasticsearch, and
ClickHouse — zero trust is the *architectural philosophy* that makes "always check
identity and permission, never assume trust by network location" a deliberate,
consistent design principle rather than a per-system afterthought.

**Defense in depth** is the complementary principle: layer multiple independent
security controls, so a failure or bypass of any single layer doesn't mean total
compromise — network segmentation, authentication, authorization, encryption, and
monitoring/detection all as independent layers, each catching what a previous layer
might miss.

```
Traditional "castle and moat":       Zero trust + defense in depth:

[Trusted internal network]           Every request, every layer, checked:
  → anything inside is trusted         Network segmentation (limit blast radius)
  → one breach = broad access              +
[Firewall = the only real check]     Authentication (who are you, always)
                                           +
                                      Authorization (what are you allowed, always)
                                           +
                                      Encryption (protect data in transit/at rest)
                                           +
                                      Monitoring (detect anomalies even if bypassed)
```

## 3. How It Really Works (Internals)

Today's per-system security lessons (Kafka SASL/SSL+ACLs, Redis ACLs+TLS,
Elasticsearch RBAC+DLS/FLS, ClickHouse RBAC+row policies) are each **one layer** in a
defense-in-depth strategy for your overall platform — no single system's security
configuration should be relied upon as the *only* protection; network-level
segmentation (which systems can even attempt to reach which other systems),
application-level authentication, and monitoring/alerting for anomalous access
patterns all need to work together. **Secrets management** (not hardcoding
credentials, rotating them, using a dedicated secrets store rather than
environment variables or config files checked into version control) is the
often-overlooked practical layer that underlies all the authentication mechanisms
studied today — every ACL/RBAC system is only as secure as the credentials
protecting access to configure and use it.

## 4. Architecture & Design Pattern Spotlight

**Pattern: layered trust boundaries — the architectural philosophy unifying every
system-specific security mechanism studied today.** Zero trust and defense in depth
aren't separate from Kafka's ACLs or ClickHouse's row policies — they're the
organizing principle explaining *why* each of those system-specific mechanisms
exists and how they should compose together into one coherent platform-wide
security posture, rather than being independently-configured, disconnected controls.

## 5. Hands-On Lab

Map your own platform's actual current trust boundaries: for each pair of systems
that communicate (Kafka→Flink, Flink→Redis/Elasticsearch/ClickHouse, any
application layer→any of these), document explicitly:
- Is authentication currently required for this connection, or is it currently
  trusted purely by network location (e.g., "it's on the internal network, so no
  auth")?
- If a credential for one of these connections were compromised, what's the actual
  blast radius — what else could an attacker reach using it?
- Where's the biggest gap between your current setup and a genuine zero-trust
  posture, and what would closing it require?

## 6. Real-World Product Comparison

- **Google's BeyondCorp** is the widely-cited origin case study for zero trust at
  scale — explicitly designed around "don't trust the network, verify every
  request" after recognizing that traditional perimeter security models don't hold
  up against sophisticated threats or simple internal misconfiguration.
- Every system studied today (Kafka, Redis, Elasticsearch, ClickHouse) increasingly
  ships with the authentication/authorization primitives needed to support a zero-
  trust posture — but achieving it requires deliberately *using* those primitives
  consistently across your whole platform, not just where convenient.

## 7. Common Production Pitfalls

- Relying entirely on network segmentation ("it's internal, so it's safe") as the
  sole security control, with no per-system authentication/authorization —
  precisely the traditional model zero trust exists to move past.
- Configuring strong access control on some systems (per today's lessons) while
  leaving others on default/permissive settings, creating an inconsistent security
  posture with real gaps.
- Storing credentials in configuration files, environment variables, or version
  control rather than a dedicated secrets-management system — undermining every
  authentication mechanism regardless of how well-configured it is.

## 8. Review Questions
1. What's the core difference between the traditional "trusted internal network"
   model and zero trust?
2. How do today's per-system security lessons (Kafka, Redis, Elasticsearch,
   ClickHouse) each serve as one layer of defense in depth?
3. Why is secrets management the practical foundation underlying every
   authentication mechanism studied today?
4. What's the actual blast radius of a compromised credential in your own platform
   today?

## 9. Proficiency Checkpoint
If you can map your own platform's real trust boundaries and identify concrete,
specific gaps relative to a zero-trust posture, you're at Level 3.5 — a genuinely
useful security-hardening artifact for your team.

## Next
Day 19 covers multi-region disaster recovery and RPO/RTO framing — the next
production-hardening dimension beyond security.
