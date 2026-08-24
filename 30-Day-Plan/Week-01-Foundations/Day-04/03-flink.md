# Day 4: Flink — Windowing

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Implement tumbling, sliding, and session windows correctly, and choose between
`ReduceFunction` and `ProcessWindowFunction` for a given aggregation.

## 2. Core Concept (basics → advanced)

A **window** groups an unbounded stream into finite chunks so you can compute
aggregations over it (an unbounded stream has no natural "end" to aggregate over
otherwise). Three main types:

- **Tumbling**: fixed-size, non-overlapping (e.g., every 10 seconds, a fresh window —
  each event belongs to exactly one window).
- **Sliding**: fixed-size, but overlapping — a new window starts at a smaller interval
  than the window's length (e.g., a 10-second window sliding every 5 seconds — each
  event belongs to *multiple* overlapping windows).
- **Session**: dynamic size, defined by a gap of inactivity (e.g., "close the window
  after 30 seconds with no new events for this key") — the natural fit for user-activity
  or clickstream analysis, where "a session" has no fixed duration.

```
Tumbling (10s):   [0-10)[10-20)[20-30)          — each event in exactly ONE window

Sliding (10s/5s): [0-10)                        — each event in MULTIPLE
                       [5-15)                     overlapping windows
                            [10-20)

Session (30s gap): [---events---]  <30s gap>  [---events---]
                    one session                 a NEW session (gap exceeded)
```

## 3. How It Really Works (Internals)

Two ways to compute a window's result, with a real performance/flexibility trade-off:

- **`ReduceFunction`** (or `AggregateFunction`): incrementally combines each new event
  with the running partial result *as it arrives* — Flink never needs to buffer the raw
  events, only the current accumulator (e.g., a running sum). Memory-efficient, but you
  only ever see the aggregated value, never the individual events or window metadata.
- **`ProcessWindowFunction`**: buffers *all* events for the window and gives you the
  full list plus window metadata (start/end time) when the window fires — flexible
  (you can compute anything, including things that need the full event list, like a
  median), but memory cost scales with events-per-window.

The common production pattern when you need both efficiency *and* metadata: combine
them — `.reduce(reduceFn, processWindowFn)` incrementally aggregates (cheap) but still
invokes the process function once at window-fire time with the final aggregated value
plus window metadata (best of both).

## 4. Architecture & Design Pattern Spotlight

**Pattern: windowed aggregation over an unbounded stream — bridging streaming and
batch semantics.** A window is, in effect, a bounded batch carved out of an unbounded
stream on the fly. This is the conceptual bridge between Flink's streaming model and
Spark's batch model, and it's exactly what Spark Structured Streaming's micro-batches
approximate at coarser granularity (Week 2 makes this comparison explicit).

## 5. Hands-On Lab

```python
from pyflink.datastream.window import EventTimeSessionWindows
from pyflink.common import Time

clicks = env.from_collection(your_clickstream_events).assign_timestamps_and_watermarks(watermark_strategy)

sessions = (
    clicks.key_by(lambda e: e.user_id)
          .window(EventTimeSessionWindows.with_gap(Time.seconds(30)))
          .reduce(lambda a, b: a.merge_click_count(b))
)
```
Feed a synthetic clickstream with deliberate gaps: one user with events 5 seconds apart
(one session), then a 40-second gap, then more events (a new session for the same user).
Verify you get exactly 2 session results for that user, with the correct start/end
boundaries.

## 6. Real-World Product Comparison

- **Kafka Streams**' windowed `KTable` aggregations support tumbling, hopping (its term
  for sliding), and session windows too — but its model is tied more tightly to changelog
  topics for fault tolerance, versus Flink's checkpoint-based state (Day 6's direct topic).
- **Uber's** real-time platform uses session windows extensively for trip-related
  event sequences, where a fixed tumbling window would arbitrarily split a single
  logical trip across multiple windows.

## 7. Common Production Pitfalls

- Using `ProcessWindowFunction` alone (without combining with `reduce`/`aggregate`) for
  a large-key-cardinality job — buffering every raw event per window per key can exhaust
  task manager memory well before you'd expect, especially under a traffic spike.
- Choosing sliding windows without realizing each event gets processed once per
  overlapping window — a 10s/1s sliding window processes each event 10 times, not once.
- Setting a session gap too short for the actual user behavior it's meant to model,
  fragmenting what should be one session into several.

## 8. Review Questions
1. Why can a sliding window cause the same event to be processed multiple times?
2. What's the concrete memory trade-off between `ReduceFunction` and
   `ProcessWindowFunction`?
3. Why is a session window's size dynamic rather than fixed?
4. How would you get both incremental efficiency and access to window metadata in one job?

## 9. Proficiency Checkpoint
If you can pick the right window type for a given business requirement (not just
implement whichever one first comes to mind) and justify `reduce` vs.
`process` for it, you're at Level 2 moving into Level 3.

## Next
Day 5 covers Flink state — `ValueState`/`ListState`/`MapState` and the HashMap vs.
RocksDB backend choice — what actually holds a window's (or any stateful operator's)
data between events.
