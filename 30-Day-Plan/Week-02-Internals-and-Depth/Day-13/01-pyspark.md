# Day 13: PySpark — Lakehouse: Delta Lake / Iceberg / Hudi

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Create an Iceberg (or Delta) table, perform a `MERGE`, then time-travel query an
earlier version — directly connecting to your own S6 benchmark's use of Iceberg.

## 2. Core Concept (basics → advanced)

Plain Parquet files on object storage (Day 12) have no built-in concept of
transactions — concurrent writers can corrupt each other's work, there's no atomic
"this set of file changes either all happened or none did," and no way to safely read
a consistent view while a write is in progress. **Lakehouse table formats** (Delta
Lake, Apache Iceberg, Apache Hudi) solve this by adding a **transaction log** layer on
top of plain Parquet files — every write (insert, update, delete, schema change) is
recorded as an atomic, ordered entry in this log, and readers see a consistent
snapshot defined by "the log entries up to some point," never a half-written state.

```
Plain Parquet on object storage:      Lakehouse table (Delta/Iceberg/Hudi):

file1.parquet                         file1.parquet, file2.parquet, ...
file2.parquet                         + TRANSACTION LOG:
(no atomicity across files,             v1: created with file1
 no schema enforcement,                 v2: MERGE added file2, marked file1 partially superseded
 no history)                            v3: schema evolved, added column X
                                       (readers can query AS OF any version — time travel)
```

## 3. How It Really Works (Internals)

`MERGE` (upsert) semantics — impossible safely on plain immutable Parquet files without
this log — become straightforward: the operation is recorded as a new, atomic log
entry describing which files are added and which existing files are now superseded (the
underlying Parquet files themselves are still immutable; the log tracks which files
are "current" as of which version, rather than mutating file contents in place). This
is precisely the same **transactional log pattern** as Kafka's own log (an
append-only, ordered sequence of changes that defines current state) — applied here to
table metadata and file references instead of application-level events.

**Time travel** (`SELECT * FROM table VERSION AS OF 5` or `TIMESTAMP AS OF ...`) is a
direct consequence of this log-based design: since every version's exact file-set is
recorded, querying "the table as it looked at version 5" just means resolving which
files were current at that log entry — no separate backup/restore mechanism needed.

## 4. Architecture & Design Pattern Spotlight

**Pattern: transactional log pattern — the exact same underlying idea as Kafka's own
append-only log (Week 1, Day 1), applied to file-based table storage instead of a
message broker.** Recognizing "an ordered, append-only log of changes, with current
state derived by replaying/resolving it" as one pattern that recurs across Kafka
topics, lakehouse table formats, and even ClickHouse's replication queue (Week 1, Day
5) is exactly the kind of cross-system pattern recognition this curriculum has been
building toward.

## 5. Hands-On Lab

```sql
CREATE TABLE local.db.events (
    event_id BIGINT, org_id INT, amount DOUBLE, event_time TIMESTAMP
) USING ICEBERG;

INSERT INTO local.db.events VALUES (1, 10, 99.5, current_timestamp());
-- note the snapshot/version created

MERGE INTO local.db.events t
USING (SELECT 1 AS event_id, 10 AS org_id, 150.0 AS amount, current_timestamp() AS event_time) s
ON t.event_id = s.event_id
WHEN MATCHED THEN UPDATE SET amount = s.amount;

-- inspect version history
SELECT * FROM local.db.events.snapshots;

-- time-travel query to BEFORE the merge
SELECT * FROM local.db.events VERSION AS OF <snapshot_id_before_merge>;
```
Confirm the time-travel query returns the original `amount=99.5`, while a normal query
against the table now returns the merged `150.0` — this is the transaction log making
both views simultaneously valid and queryable.

## 6. Real-World Product Comparison

- **Databricks' Lakehouse** is built specifically around Delta Lake, its own
  implementation of this pattern; **Snowflake** achieves similar transactional/time-
  travel guarantees within its own proprietary storage format rather than an open
  table format; **BigQuery** offers some time-travel capability natively but not via
  an open, portable table format the way Delta/Iceberg/Hudi are designed to be.
- Your own **S6 benchmark** used **Iceberg** specifically as the open table format of
  choice for a greenfield modern architecture — worth revisiting that benchmark's
  actual configuration through today's lens (which specific Iceberg features —
  schema evolution, time travel, `MERGE` — did that benchmark exercise, and were the
  results consistent with what today's lesson would predict?).

## 7. Common Production Pitfalls

- Treating a lakehouse table format as "just Parquet" and manually manipulating the
  underlying files directly — this bypasses the transaction log entirely and can
  corrupt the table's consistency guarantees.
- Not understanding that time-travel history has a retention policy — old snapshots
  are eventually vacuumed/expired to reclaim storage, meaning "time travel" has a
  practical, configurable retention window, not infinite history by default.
- Choosing between Delta/Iceberg/Hudi based on hype rather than actual ecosystem fit
  (which query engines, which cloud storage, which existing tooling your team already
  uses) — all three solve the same core problem with different ecosystem trade-offs.

## 8. Review Questions
1. What specific problem does the transaction log solve that plain Parquet files
   don't?
2. Why is time travel a natural consequence of this design, rather than a separately
   built feature?
3. How is this the same underlying pattern as Kafka's own log?
4. What did your own S6 benchmark's use of Iceberg actually exercise, in these terms?

## 9. Proficiency Checkpoint
If you can perform a `MERGE` and a time-travel query, and explain precisely why the
transaction log makes both safe, you're at Level 3 — and can speak concretely to your
own S6 benchmark's architecture.

## Next
Day 14 is this week's lab + review — reproducing your real PySpark, Flink, and
ClickHouse incidents end to end, and diagramming your BigQuery→ClickHouse target state.
