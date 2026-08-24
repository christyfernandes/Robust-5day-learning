# Day 2: Flink — DataStream API Core & Parallelism

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Chain the core DataStream transformations correctly, and explain how parallelism and
operator chaining together determine how many actual OS threads/tasks your job runs as.

## 2. Core Concept (basics → advanced)

**Core transformations:**
```python
ds.map(fn)            # 1-to-1 transform
ds.filter(predicate)  # keep/drop records
ds.flat_map(fn)       # 1-to-many transform
ds.key_by(fn)         # logical partition by key (required before most stateful ops)
ds.reduce(fn)         # incremental aggregation per key
```

```python
from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)   # default parallelism for every operator, unless overridden

orders = env.from_collection([
    {"customer": "alice", "amount": 100},
    {"customer": "bob", "amount": 50},
    {"customer": "alice", "amount": 30},
])

totals = (
    orders.key_by(lambda o: o["customer"])
          .reduce(lambda a, b: {"customer": a["customer"], "amount": a["amount"] + b["amount"]})
)
totals.print()
env.execute("running_totals")
```

**Parallelism.** Setting `parallelism=4` means Flink runs up to 4 parallel instances of
each operator, each handling a subset of the keyspace (for keyed operators) or a subset
of the incoming records (for non-keyed ones). You can override parallelism per-operator,
not just globally.

## 3. How It Really Works (Internals)

**Operator chaining.** When possible, Flink fuses a sequence of operators (e.g.,
`map → filter → map`) into a **single task** that runs in one thread with no
serialization or network hop between the fused steps — this is a major performance
optimization, avoiding the overhead of passing each record through separate task
boundaries. A chain breaks (becomes separate tasks) at a `key_by()` (because that's a
genuine repartitioning — data must potentially move to a different parallel instance)
or when parallelism changes between operators.

```
map → filter → map                    map → keyBy → reduce
  (fused into ONE task,                  (map fused with keyBy's upstream side,
   if parallelism matches)                but reduce runs as a SEPARATE task —
                                          keyBy causes real network shuffle)
```

`key_by()` is doing real work here: it determines, for every record, which parallel
task instance should own that key going forward — via a hash of the key, similar in
spirit to how Kafka picks a partition from a message key (Day 1). This is precisely why
keyed state (Week 1, Day 5) is safe: the same key always lands on the same task
instance, so that instance's local state for that key is always consistent.

## 4. Architecture & Design Pattern Spotlight

**Pattern: operator fusion for pipeline efficiency**, paired with **key-based logical
partitioning** for safe distributed state. You'll see the key-based partitioning half
of this pattern again explicitly in Kafka's partitioning (Day 1, already seen), Redis
Cluster's hash slots, and ClickHouse's sharding key — it's the same underlying idea
of "route by key so related data/work always co-locates," applied at four different
layers of the stack.

## 5. Hands-On Lab
Take the running-totals snippet above and:
1. Run it with `parallelism=1`, then `parallelism=4` — same logical result, different
   physical execution.
2. Insert a `.map(lambda x: x)` between two other maps and confirm (via the Flink Web
   UI's job graph, if running on a real cluster/session) whether it got fused into a
   single task or not.

## 6. Real-World Product Comparison

- **Uber's real-time platform** builds heavily keyed pipelines (keyed by driver ID,
  trip ID, etc.) for exactly this reason — keyed state per entity is a natural fit for
  "track this driver's live status" style problems.
- Contrast with **Kafka Streams**: conceptually the same `map`/`filter`/`groupByKey`
  vocabulary, but embedded directly in your application's JVM process rather than
  submitted to a separate Flink cluster — a real operational trade-off (simpler
  deployment vs. losing Flink's cluster-level resource management and advanced
  windowing).

## 7. Common Production Pitfalls
- Calling `key_by()` on a field with very few distinct values (e.g., a boolean) when
  you have high parallelism — most of your parallel task instances sit idle while a
  couple handle all the data, a form of skew directly analogous to Spark's join skew
  (Week 1, Day 4) and Kafka's uneven key distribution (Day 1).
- Assuming a chain of `.map()` calls always fuses — a parallelism change or explicit
  `.disableChaining()` (or certain operator types) breaks the chain, adding real
  serialization overhead you might not expect.
- Forgetting that `.reduce()` needs a **keyed** stream — calling it on a non-keyed
  stream is a compile/runtime error, a common early mistake.

## 8. Review Questions
1. What does operator chaining actually save you, mechanically?
2. Why does `key_by()` break a chain when a plain `.map()` doesn't?
3. What's the practical symptom of choosing a `key_by()` field with very low
   cardinality under high parallelism?
4. Contrast Flink's cluster-based deployment with Kafka Streams' embedded-library
   approach — what's the real operational trade-off?

## 9. Proficiency Checkpoint
If you can predict whether a given transformation chain will fuse into one task or
break into several, and explain why, you're at Level 2, moving into Level 3.

## Next
Day 3 covers time semantics — event time vs. processing time vs. ingestion time, and
watermarks — the concepts you'll need before windowing makes sense on Day 4.
