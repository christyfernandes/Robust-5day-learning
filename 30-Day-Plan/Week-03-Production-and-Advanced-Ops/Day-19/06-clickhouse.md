# Day 19: ClickHouse — Backup & DR: clickhouse-backup

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Run a `clickhouse-backup create` + `restore` cycle locally, and explain why
replica-based and snapshot-based DR are complementary, not substitutes.

## 2. Core Concept (basics → advanced)

Your cluster's **replication** (Week 1, Day 5's `ReplicatedMergeTree` + Keeper)
protects against **node failure** — lose a replica, the data still exists on other
replicas. It does **not** protect against **logical errors** — an accidental `DROP
TABLE`, a bad `ALTER` that corrupts data, or an application bug that writes garbage
— since replication faithfully propagates these mistakes to every replica just as
reliably as legitimate writes, exactly the same limitation studied in today's
Elasticsearch snapshot lesson.

**`clickhouse-backup`** (a widely-used open-source tool, not a built-in ClickHouse
feature) provides the complementary layer: point-in-time backups of table data and
metadata, stored to S3/GCS-compatible object storage, restorable independently of
your live cluster's current (possibly corrupted) state.

```
Replication (Week 1, Day 5):        Snapshot/backup (clickhouse-backup):

Protects against:                    Protects against:
  - node failure                       - accidental DROP TABLE
  - disk failure                       - bad ALTER / data corruption
  - network partition                  - application bugs writing garbage

Does NOT protect against:            Complementary — NOT a replacement
  logical errors (they replicate      for replication (doesn't help with
  everywhere, faithfully)             a simple node/disk failure recovery,
                                       which replication handles faster)
```

## 3. How It Really Works (Internals)

`clickhouse-backup` typically leverages ClickHouse's own `FREEZE` mechanism
internally — creating hard links to existing immutable parts (Week 1, Day 1) rather
than copying data at backup time, making the *local* backup step nearly instant
regardless of table size (since it's just creating links to already-immutable
files, not duplicating bytes) — the actual data upload to S3/GCS happens as a
separate, genuinely I/O-bound step. This hard-link-based approach is only possible
*because* MergeTree parts are immutable (Week 1, Day 1) — the same immutability
property that enables efficient replication and efficient incremental snapshots in
Elasticsearch (today's other lesson) also enables efficient local backup snapshots
here.

## 4. Architecture & Design Pattern Spotlight

**Pattern: replica-based DR (node failure) + snapshot-based DR (logical errors) —
two complementary layers, exactly the same two-layer resilience structure as
today's Elasticsearch lesson, and worth recognizing as a general principle: no
single durability mechanism covers every failure class, and mature systems combine
multiple, purpose-fit mechanisms rather than relying on one.**

## 5. Hands-On Lab

```bash
clickhouse-backup create my_backup_1
clickhouse-backup upload my_backup_1   # to configured S3/GCS remote storage

# simulate a disaster — drop a table
clickhouse-client --query "DROP TABLE events"

# restore
clickhouse-backup download my_backup_1
clickhouse-backup restore my_backup_1
```
Confirm the `events` table and its data are fully recovered after the restore.
Time the local `create` step versus the `upload` step separately — confirm `create`
is nearly instant (hard-link based) while `upload` takes time proportional to actual
data volume, directly observing the mechanism described above.

## 6. Real-World Product Comparison

- **`clickhouse-backup`** is the de facto standard tool for this in the ClickHouse
  operator community — not part of ClickHouse itself, but widely adopted as the
  practical answer to backup/DR for exactly this reason.
- Contrast with **BigQuery**, where this entire concern (backup, restore,
  point-in-time recovery) is handled transparently by the managed service —
  another concrete instance of the "more control, more operational responsibility"
  trade-off inherent in your self-hosted migration, worth flagging explicitly to
  stakeholders evaluating the migration's operational cost.

## 7. Common Production Pitfalls

- Relying on replication alone and assuming it covers backup/DR needs — it
  explicitly does not protect against logical errors.
- Never testing a real restore from a real backup — the same "untested backup is
  not a real safety net" principle from Week 2 Day 12's Redis lesson applies
  identically here.
- Not accounting for the genuinely time-consuming `upload` step when planning
  backup frequency/retention — the local `create` step being fast can create a
  false sense that the entire backup process is equally fast.

## 8. Review Questions
1. What specific failure class does replication not protect against, and why?
2. Why is the local `create` step nearly instant regardless of table size?
3. Why are replica-based and snapshot-based DR complementary rather than
   substitutable?
4. What operational responsibility does self-hosting take on that BigQuery handles
   transparently?

## 9. Proficiency Checkpoint
If you can run a real backup/restore cycle and explain precisely which failure
classes it covers versus replication, you're at Level 3.5 — a genuinely necessary
operational practice for your production cluster.

## Next
Day 20 covers the actual cost-modeling framework — self-hosted ClickHouse vs.
BigQuery TCO — your live POC's central deliverable.
