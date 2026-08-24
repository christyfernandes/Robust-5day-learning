# Day 5: Flink — State: ValueState, ListState, MapState & Backends

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Implement a stateful deduplication operator using `ValueState` with TTL, and explain
the trade-off between the HashMap and RocksDB state backends.

## 2. Core Concept (basics → advanced)

Any operator that needs to remember something between events (a running count, a
dedup set, a "have I seen this key before" flag) needs **keyed state** — state that's
automatically partitioned alongside the keyed stream (via `key_by`), so each key's state
lives with whichever parallel task instance handles that key.

Three common state primitives:
- **`ValueState<T>`**: a single value per key (e.g., "last seen timestamp for this
  user").
- **`ListState<T>`**: an append-friendly list per key.
- **`MapState<K,V>`**: a per-key hash map — useful when you need sub-keyed lookups
  within a single stream key (e.g., per-user, per-product counts).

```
key_by(user_id) ──▶ Task instance 1 ──▶ holds ValueState for users hashed here
                ──▶ Task instance 2 ──▶ holds ValueState for users hashed here
                ──▶ Task instance 3 ──▶ holds ValueState for users hashed here

(state is co-located with its key's stream partition — no cross-task lookups needed)
```

## 3. How It Really Works (Internals)

State lives in a **state backend**, and the choice has real production consequences:
- **HashMap backend**: state lives as actual Java objects on the JVM heap. Fast (no
  serialization on access), but bounded by available heap memory and subject to GC
  pressure at large state sizes — the same GC-pressure concern from today's PySpark
  lesson, in a different framework.
- **RocksDB backend**: state is serialized and stored in an embedded RocksDB instance
  (an LSM-tree key-value store) on local disk, with a hot cache in memory. Scales to
  state sizes far larger than available RAM, at the cost of serialization overhead on
  every state access.

**TTL (time-to-live)** on state entries is essential for any long-running job with
unbounded key cardinality (e.g., a dedup-by-user-ID stream, where users eventually stop
being active) — without TTL, state grows forever, since Flink has no way to know a key
is "done" on its own. TTL configuration also interacts with checkpointing: expired-but-
not-yet-cleaned-up state still gets checkpointed until Flink's background cleanup runs,
which is worth knowing when reasoning about checkpoint size growth over time.

## 4. Architecture & Design Pattern Spotlight

**Pattern: keyed state colocated with keyed stream partitioning.** This is precisely
what makes Flink's stateful processing scale horizontally without a separate
distributed state store — state moves with its key during rescaling, rather than living
in a shared external system every task must round-trip to. Compare this to using
**Redis as external state** instead: simpler mental model, but now every state
access is a network round-trip, and consistency between "the stream's position" and
"the external state's value" during a failure/restart becomes your problem to solve,
not Flink's.

## 5. Hands-On Lab

```python
from pyflink.datastream.state import ValueStateDescriptor, StateTtlConfig
from pyflink.common import Time
from pyflink.datastream.functions import KeyedProcessFunction

class DedupFunction(KeyedProcessFunction):
    def open(self, runtime_context):
        ttl_config = StateTtlConfig.new_builder(Time.minutes(10)) \
            .set_update_type(StateTtlConfig.UpdateType.OnCreateAndWrite) \
            .build()
        descriptor = ValueStateDescriptor("seen", Types.BOOLEAN())
        descriptor.enable_time_to_live(ttl_config)
        self.seen_state = runtime_context.get_state(descriptor)

    def process_element(self, value, ctx):
        if self.seen_state.value() is None:
            self.seen_state.update(True)
            yield value   # first time seeing this key — pass it through
        # else: duplicate, drop it
```
Feed a stream with deliberate duplicate keys (some within the TTL window, some spaced
out beyond it) and verify: duplicates within the window are dropped, but the same key
reappearing *after* TTL expiry is treated as "new" again.

## 6. Real-World Product Comparison

- **RocksDB** as an embedded state backend is the same underlying storage engine used
  standalone by many systems (originally derived from Google's LevelDB) — recognizing
  it here connects directly to Week 2's LSM-tree-family discussion.
- **Redis-as-external-state** is a legitimate pattern too (some teams prefer it for
  cross-job state sharing, or when state needs to survive a full job redeployment more
  simply) — but it trades Flink's exactly-once state/stream consistency guarantee for
  operational simplicity, a trade-off worth naming explicitly rather than defaulting to.

## 7. Common Production Pitfalls

- Using `ListState` for an unbounded, ever-growing list without any eviction or TTL
  strategy — this is a slow, silent state-size leak that eventually shows up as
  checkpoint duration growing over weeks.
- Choosing the HashMap backend for a job with genuinely large per-key state (or very
  high key cardinality) — works fine until it doesn't, then fails as an OOM with little
  warning.
- Forgetting that RocksDB backend state access has real serialization cost — a job that
  does many small state reads/writes per event can be meaningfully slower on RocksDB
  than HashMap, even though RocksDB "scales better."

## 8. Review Questions
1. Why does keyed state need to be colocated with its key's stream partition?
2. What's the concrete trade-off between the HashMap and RocksDB state backends?
3. Why is TTL essential for state with unbounded key cardinality?
4. What consistency guarantee do you give up by moving state out to Redis instead of
   keeping it in Flink's own state backend?

## 9. Proficiency Checkpoint
If you can choose the right state backend for a given state-size/access-pattern
scenario and implement TTL correctly, you're at Level 2 moving into Level 3.

## Next
Day 6 covers checkpointing itself — the Chandy-Lamport algorithm that makes this state
recoverable after a failure, and the exact mechanism behind your real JobManager
debugging.
