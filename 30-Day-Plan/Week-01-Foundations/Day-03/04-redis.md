# Day 3: Redis — Persistence: RDB vs. AOF

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain the durability/performance trade-off between RDB and AOF, and correctly predict
what survives a hard crash under each configuration.

## 2. Core Concept (basics → advanced)

Redis is in-memory, so persistence is entirely about **surviving a restart**, not about
where data "lives" day to day. Two independent mechanisms, often used together:

- **RDB (Redis Database)**: a point-in-time binary snapshot of the entire dataset,
  written on a schedule (e.g., "save if ≥100 keys changed in 60s") or on demand. Fast to
  load on restart (it's just a memory image), but anything written *since* the last
  snapshot is lost on crash.
- **AOF (Append-Only File)**: every write command is appended to a log, replayed in
  order on restart to rebuild state. Far less data loss potential (configurable fsync
  policy — see below), but the file grows continuously and replay-on-restart is slower
  than loading an RDB snapshot.

```
RDB:  [snapshot@t0] ---- writes happen, not persisted ---- [snapshot@t1] --- CRASH
                                                                              ↑
                                                            lose everything since t1

AOF:  [write1][write2][write3][write4][write5] --- CRASH
                                                     ↑
                                        lose only what wasn't fsynced yet
```

## 3. How It Really Works (Internals)

RDB snapshotting uses `fork()` to create a child process that shares the parent's memory
pages via **copy-on-write (COW)**: the child writes the snapshot from a frozen view of
memory, while the parent keeps serving writes. Only pages that get *modified* during the
snapshot are actually copied (one page at a time, by the OS) — meaning RDB's memory
overhead during a snapshot is proportional to write volume during that window, not to
total dataset size. On a write-heavy instance with a large dataset, this can still cause
a real memory spike and is a common cause of unexpected OOM during scheduled snapshots.

AOF's actual data-loss window is governed by its **fsync policy**:
- `always` — fsync after every write (safest, slowest — a network round-trip's worth of
  disk latency added to every command).
- `everysec` (the practical default) — fsync once per second in a background thread; you
  can lose at most ~1 second of writes on a hard crash.
- `no` — let the OS decide when to flush; fastest, but a crash can lose an
  OS-buffer's-worth of writes (potentially many seconds).

Redis can also periodically **rewrite** the AOF file (compacting it to the minimal set
of commands that reproduce current state) — itself another `fork()`+COW operation, with
the same memory-spike consideration as RDB snapshotting.

## 4. Architecture & Design Pattern Spotlight

**Pattern: log-structured durability (AOF) vs. point-in-time snapshot (RDB) — the exact
same trade-off as a database's WAL vs. periodic checkpoint.** Using both together (RDB
for fast restart + AOF for minimal data loss, the common production configuration) is
itself a recognizable pattern: cheap coarse recovery point + fine-grained recent-history
replay, also seen in how many databases combine periodic checkpoints with WAL replay
since the last checkpoint.

## 5. Hands-On Lab

```bash
# redis.conf
save 60 100
appendonly yes
appendfsync everysec
```
Start Redis with this config, write ~50 keys, then:
```bash
kill -9 $(pgrep redis-server)      # simulate a hard crash, no clean shutdown
redis-server /path/to/redis.conf   # restart
redis-cli DBSIZE                   # how many keys survived?
```
Now repeat with `appendonly no` (RDB-only) and compare `DBSIZE` after the same kill.
The gap between the two numbers *is* your durability window, made concrete.

## 6. Real-World Product Comparison

- Redis's `everysec` default is a deliberate, explicit trade — the same choice
  Postgres offers via `synchronous_commit=off`: bound the durability window instead of
  paying a disk-sync cost on every single write.
- Compare to **Postgres's WAL**: conceptually the same idea as AOF (append every change,
  replay on recovery), but Postgres additionally uses the WAL for point-in-time recovery
  and replication — Redis's AOF is restart-recovery only, not a general-purpose
  replication transport (that's a separate mechanism, covered later this week).

## 7. Common Production Pitfalls

- Running AOF rewrite or RDB snapshot on an instance close to its memory limit —  the
  COW memory spike during a write-heavy period can push it over and trigger an OOM-kill,
  taking down the *whole* instance, not just the persistence job.
- Assuming `appendonly yes` alone means "no data loss" without checking the actual
  `appendfsync` policy — `no` is not meaningfully safer than plain RDB under a hard crash.
- Forgetting that RDB+AOF together means *slower* restarts under some configurations
  (Redis may need to reconcile both) — test actual restart time, don't just assume more
  persistence mechanisms is strictly safer with no cost.

## 8. Review Questions
1. Why does `fork()` + copy-on-write make RDB snapshotting fast without blocking writes?
2. What's the real difference in data-loss window between `always`, `everysec`, and `no`?
3. Why can a fork-based snapshot cause a memory spike proportional to write volume, not
   dataset size?
4. When would you choose RDB-only over RDB+AOF, despite the extra data-loss risk?

## 9. Proficiency Checkpoint
If you can predict, for a given fsync policy and a given crash timing, roughly how much
data you'd lose, you're at Level 2 on Redis durability.

## Next
Day 4 moves from persistence to messaging: Pub/Sub vs. Redis Streams, and when Streams
is "enough" instead of reaching for Kafka.
