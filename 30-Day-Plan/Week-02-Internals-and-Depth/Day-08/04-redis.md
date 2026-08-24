# Day 8: Redis — Replication Internals: PSYNC2

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Disconnect a replica briefly, reconnect it, and confirm a **partial** (not full) resync
in the logs — and explain the mechanism that makes that possible.

## 2. Core Concept (basics → advanced)

Redis replication works by a replica requesting a **sync** from its primary. The naive
approach (**full resync**) has the primary generate a fresh RDB snapshot, send the
entire dataset to the replica, then stream new writes from that point forward — correct,
but expensive for large datasets, especially for a *brief* disconnection where almost
nothing actually changed.

**PSYNC2** (partial resynchronization) avoids this for short disconnections: the
primary maintains a **replication backlog** — a bounded, in-memory circular buffer of
recently-written commands — and each replica remembers its own **replication offset**
(how far into the primary's command stream it had already applied). On reconnect, if
the replica's last-known offset is still present in the primary's backlog, the primary
sends **only the commands the replica missed**, not a full dataset resync.

```
Full resync (backlog exhausted, or first connection):
  Primary ──▶ full RDB snapshot ──▶ Replica  (expensive, proportional to dataset size)

Partial resync (backlog still has the missing commands):
  Primary ──▶ just the missed commands since replica's last offset ──▶ Replica
  (cheap, proportional to how much was missed, not total dataset size)
```

## 3. How It Really Works (Internals)

The replication backlog has a fixed size (`repl-backlog-size`, default 1MB, commonly
tuned much larger in production) — if a replica is disconnected longer than it takes
for the backlog to "wrap around" and overwrite the offset the replica needs, partial
resync becomes impossible and Redis falls back to a full resync. This means backlog
sizing is a genuine operational trade-off: too small, and even brief network blips
force expensive full resyncs under any real write load; appropriately sized, and
transient network issues (the far more common real-world failure) recover cheaply.

Each replica and primary also track a **replication ID** — after a failover (a replica
promoted to primary, Day 9's Sentinel lesson), the new primary gets a new replication
ID, but Redis retains the *previous* ID for a window, specifically so that other
replicas that were following the old primary can still partially resync against the
newly-promoted one instead of being forced into a full resync purely because of the
leadership change.

## 4. Architecture & Design Pattern Spotlight

**Pattern: replication log with partial-resync optimization — the same underlying idea
as Kafka's replica fetch protocol (Day 4), where a follower catches up from its last
known offset rather than re-copying the entire log from scratch.** Both systems
recognize that "catch up from where you left off" is dramatically cheaper than
"start over," provided the source retains enough recent history to make that possible —
a recurring theme in every replicated log-structured system you'll study this month.

## 5. Hands-On Lab

```bash
# redis.conf on primary
repl-backlog-size 10mb

# start replica, confirm full sync in logs (first connection)
redis-cli -p 6380 REPLICAOF localhost 6379
tail -f /var/log/redis-replica.log   # should show "Full resync"

# briefly disconnect
redis-cli -p 6380 REPLICAOF NO ONE
# (write a few commands to the primary during the disconnect)
redis-cli -p 6380 REPLICAOF localhost 6379
tail -f /var/log/redis-replica.log   # should now show "Partial resynchronization accepted"
```
Now repeat, but write enough data to the primary during the disconnect to exceed
`repl-backlog-size` — confirm the log now shows a full resync instead, and reason
about why.

## 6. Real-World Product Comparison

- This is architecturally the same problem **Kafka's replica fetch protocol** solves
  (Day 4) — a follower/replica resuming from a specific offset rather than
  re-transferring everything — implemented independently in two different systems
  because both face the identical "network blips shouldn't be catastrophically
  expensive" requirement.
- Production Redis deployments at scale (GitHub, Twitter-era Redis usage) tune
  `repl-backlog-size` explicitly based on observed write throughput and expected
  network blip duration — a concrete, measurable operational decision, not a
  default-and-forget setting.

## 7. Common Production Pitfalls

- Leaving `repl-backlog-size` at its small default on a high-write-throughput
  instance — even brief, routine network hiccups end up forcing full resyncs, each one
  a real load spike on the primary.
- Not monitoring resync type (full vs. partial) in production — a pattern of frequent
  full resyncs is a strong signal of either backlog undersizing or a deeper network
  reliability problem worth investigating.
- Assuming replication lag is zero — asynchronous replication (Redis's default) always
  has some lag window; reads from a replica can return slightly stale data, a real
  consideration for read-scaling use cases.

## 8. Review Questions
1. What specifically does the replication backlog store, and why is it bounded in size?
2. What determines whether a reconnecting replica gets a partial or full resync?
3. Why does Redis retain a previous replication ID after a failover?
4. Why is this the same underlying pattern as Kafka's replica fetch protocol?

## 9. Proficiency Checkpoint
If you can predict, for a given disconnect duration and write rate, whether a resync
will be partial or full, you're at Level 3.

## Next
Day 9 covers Redis Sentinel — quorum-based automated failover, and where the
"previous replication ID" mechanism from today becomes operationally important.
