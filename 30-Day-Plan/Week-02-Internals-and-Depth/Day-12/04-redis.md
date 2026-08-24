# Day 12: Redis — As Primary Store vs. Cache-Only Trade-offs

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
List what you'd need to add to trust Redis as a primary store (not just a cache) for
one real use case, and explain the durability trade-offs involved.

## 2. Core Concept (basics → advanced)

Most of this month has treated Redis as a cache or an ancillary system (Pub/Sub,
Streams, a fast lookup layer) — sitting *alongside* a "real" durable database. But
Redis can also serve as a **primary store** (a system of record with no separate
backing database) for use cases where its data model and performance profile fit well
and its durability characteristics can be made adequate for the requirement.

The core question when considering this: **what happens if this specific data is
lost, and is that actually acceptable?** For a cache, the answer is trivially "no
problem, just repopulate from the source" — that's the entire premise of caching. For
a primary store, data loss is a real, permanent loss with no fallback, so the
durability mechanisms studied earlier this curriculum (RDB, AOF, replication,
Sentinel/Cluster) move from "nice to have" to "the actual thing standing between you
and permanent data loss."

## 3. How It Really Works (Internals)

Trusting Redis as a primary store for a given use case requires deliberately
assembling the durability stack studied piecemeal earlier: **AOF with
`appendfsync=always` or `everysec`** (Week 1, Day 3) for acceptable data-loss windows
on a hard crash, **replication with `min-replicas-to-write`** configured (analogous to
Kafka's `min.insync.replicas`, Week 1, Day 4) so writes aren't acknowledged unless a
minimum number of replicas have them, **Sentinel or Cluster** (Week 2, Days 9-10) for
automated failover so a primary failure doesn't mean an extended outage, and a genuine
**backup strategy** (periodic RDB snapshots shipped to durable, separate storage) as a
last line of defense against a scenario the above mechanisms don't cover (e.g.,
application-level data corruption, not just node failure).

This is the same set of decisions any "durable data store" needs to make explicitly —
Redis just requires you to assemble and configure them yourself, rather than getting
them by default the way a traditional RDBMS's out-of-the-box durability guarantees
might suggest.

## 4. Architecture & Design Pattern Spotlight

**Pattern: durability trade-offs of an in-memory system-of-record — the general
question of "what's my actual acceptable data-loss window, and what mechanisms
guarantee it" applied to a use case beyond caching.** This connects directly back to
every durability mechanism studied earlier (AOF/RDB, replication quorums, Sentinel/
Cluster failover) — today's lesson is really about *composing* those pieces
deliberately for a specific trust requirement, rather than introducing new mechanisms.

## 5. Hands-On Lab

Pick one real (or realistic) use case at your work that currently uses Redis
peripherally, and evaluate whether it could become a primary store. For your chosen
use case, write down explicitly:
- What's the actual acceptable data-loss window if the Redis instance crashes hard,
  right now? (Seconds? Zero, ever?)
- Which specific durability configuration (fsync policy, replication quorum,
  failover mechanism) would need to be in place to meet that requirement?
- What's your backup/restore story if data is lost or corrupted despite the above —
  and how would you actually test that restore process works, rather than assuming it
  does?

## 6. Real-World Product Comparison

- **Twitter** historically used Redis for parts of its timeline delivery
  infrastructure in a near-primary-store role, with careful attention to the exact
  durability configuration described above — a well-known real-world example of
  treating Redis as more than "just a cache" for a specific, carefully-scoped use case.
- Contrast with **DragonflyDB/Valkey** (Day 13) — API-compatible alternatives that some
  teams evaluate specifically when Redis's single-threaded architecture becomes a
  genuine throughput ceiling for a primary-store use case at scale.

## 7. Common Production Pitfalls

- Treating Redis as a durable primary store "by default" without explicitly
  configuring AOF, replication quorums, and failover — the out-of-the-box
  configuration (as with many systems) prioritizes performance/simplicity over maximum
  durability, and needs deliberate tuning for this use case.
- Never testing the actual backup/restore process — a backup strategy that's never
  been exercised end to end is an untested assumption, not a real safety net.
- Underestimating the operational discipline required (monitoring replication lag,
  AOF rewrite health, Sentinel/Cluster quorum health) once Redis becomes a genuine
  system of record rather than a disposable cache.

## 8. Review Questions
1. What's the core question to ask before trusting Redis as a primary store for a
   given use case?
2. What durability mechanisms need to be deliberately assembled, and from where in
   this curriculum does each come?
3. Why is an untested backup/restore process not a real safety net?
4. What's a concrete real-world example of Redis being trusted as a near-primary
   store?

## 9. Proficiency Checkpoint
If you can evaluate a real use case and specify exactly which durability mechanisms
would need to be configured to trust Redis as its primary store, you're at Level 3.

## Next
Day 13 covers DragonflyDB, Valkey, and KeyDB — modern, API-compatible alternatives
directly on your radar for cost/performance evaluation work.
