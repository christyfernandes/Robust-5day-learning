# Day 19: Elasticsearch — Resiliency: Split-Brain Prevention & Snapshot/Restore

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Configure and run a snapshot to a repository, then restore it — and explain how
quorum-based master election prevents split-brain.

## 2. Core Concept (basics → advanced)

**Split-brain** is the scenario where a network partition causes two disjoint
groups of nodes to each independently believe *they* are the legitimate cluster,
potentially both accepting writes independently — a serious correctness hazard
(exactly the same class of problem Week 1 Day 4's Raft lesson and Redis Sentinel's
quorum logic, Week 2 Day 9, are designed to prevent). Elasticsearch prevents this via
requiring master elections to achieve a **quorum** of master-eligible nodes (the
same "majority of an odd-sized set" reasoning studied throughout this month) —
a minority partition can never elect its own master, so it correctly becomes
unavailable rather than risking a second, conflicting "cluster" accepting writes.

**Snapshot/restore** is Elasticsearch's backup mechanism — a snapshot captures a
point-in-time copy of one or more indices to a configured repository (commonly
S3/GCS-backed), incrementally (only new/changed segments since the last snapshot are
actually copied, keeping subsequent snapshots fast and storage-efficient) — restore
recreates the indices from a chosen snapshot, the last line of defense against data
loss that replication and quorum-based consensus alone don't fully cover (e.g.,
application-level data corruption or accidental deletion, which is faithfully
replicated to every replica just as much as legitimate data).

## 3. How It Really Works (Internals)

The quorum requirement for master election is precisely why running an
**even** number of master-eligible nodes is a common misconfiguration mistake (Week
1, Day 4's odd-node-count reasoning applies identically here) — with an even split,
neither half of a partition can achieve a majority, which is actually the *safe*
outcome (no split-brain), but means the whole cluster becomes unavailable rather
than at least the majority-side continuing to serve — worth understanding precisely
why odd counts specifically avoid this "everyone stuck" scenario in most partition
shapes.

Snapshot's incremental nature works because segments (Week 1, Day 6) are immutable —
a snapshot only needs to copy segments that didn't exist in the previous snapshot,
the same "immutable, append-only, incrementally-copyable" property that makes
several other systems' incremental backup strategies efficient (directly comparable
to ClickHouse's own backup approach, today's ClickHouse lesson).

## 4. Architecture & Design Pattern Spotlight

**Pattern: quorum-based master election preventing split-brain — the direct
application of Week 1 Day 4's Raft/consensus reasoning to Elasticsearch's own
cluster-state management,** paired with **snapshot/restore as the independent,
replication-orthogonal backup layer** — the same two-layer resilience structure
(consensus for coordination correctness, separate backup for data-loss protection
beyond what replication covers) recurring across every system this curriculum
studies.

## 5. Hands-On Lab

```json
PUT _snapshot/backup_repo
{ "type": "fs", "settings": { "location": "/mnt/es_backups" } }

PUT _snapshot/backup_repo/snapshot_1
{ "indices": "products,events", "include_global_state": false }

GET _snapshot/backup_repo/snapshot_1/_status
```
Once complete, delete or corrupt one of the snapshotted indices, then restore:
```json
POST _snapshot/backup_repo/snapshot_1/_restore
{ "indices": "products" }
```
Confirm the restored index matches the pre-deletion state. Then take a *second*
snapshot after adding more documents, and confirm (via repository storage
inspection, or the snapshot status API) that it's meaningfully smaller/faster than
the first, reflecting its incremental nature.

## 6. Real-World Product Comparison

- Every serious production Elasticsearch deployment runs scheduled snapshots to
  S3/GCS-backed repositories as standard, non-optional operational practice —
  replication alone (Week 1, Day 5) protects against node failure, not against
  logical/application-level data corruption or accidental deletion.
- This is directly comparable to **ClickHouse's `clickhouse-backup`** (today's
  ClickHouse lesson) — both systems recognize that replica-based durability and
  snapshot-based backup solve genuinely different failure classes and need both,
  not either-or.

## 7. Common Production Pitfalls

- Relying on replication alone as a complete backup strategy — replication
  faithfully propagates accidental deletions and corruption just as reliably as
  legitimate writes.
- Running an even number of master-eligible nodes, creating exactly the "everyone
  stuck during a partition" scenario described above.
- Never testing a real restore — confirming snapshots complete successfully isn't
  the same as confirming a restore actually works and produces usable data.

## 8. Review Questions
1. Why does quorum-based master election prevent split-brain rather than just
   reduce its likelihood?
2. Why is an even master-eligible node count a real misconfiguration, not just a
   style preference?
3. Why does replication alone not substitute for snapshot-based backup?
4. Why are Elasticsearch snapshots efficient to take incrementally?

## 9. Proficiency Checkpoint
If you can configure real snapshot/restore and correctly explain quorum-based
split-brain prevention, you're at Level 3.5.

## Next
Day 20 covers Elasticsearch's licensing landscape and alternatives — OpenSearch,
Typesense, Meilisearch, Algolia.
