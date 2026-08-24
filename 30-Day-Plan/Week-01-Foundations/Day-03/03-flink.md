# Day 3: Flink — Event Time, Watermarks & Late Data

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Distinguish event time, processing time, and ingestion time; explain what a watermark
actually is; and configure allowed lateness for a windowed job with out-of-order data.

## 2. Core Concept (basics → advanced)

Three different notions of "when" an event happened:
- **Event time**: when the event actually occurred, per a timestamp embedded in the data
  itself (e.g., a mobile app's local clock when a tap happened).
- **Ingestion time**: when the event entered Flink (e.g., when it was read from Kafka).
- **Processing time**: the wall-clock time on the machine doing the processing, right now.

For anything that needs correct results regardless of network delay or out-of-order
delivery — which is most real analytics — **event time is the only correct choice**.
Processing time is fast and simple but gives different answers on every replay, since
"now" depends on when you happened to run the job.

The problem: with event time, how does the system know when it's "seen everything" for
a given time window if events can arrive late and out of order? That's what a
**watermark** answers — it's a special marker flowing through the stream asserting "no
event with a timestamp earlier than T will arrive from here on" (an assertion, not a
guarantee — late events can still violate it, which is exactly why "allowed lateness"
exists as a safety valve).

```
Events arriving:  E(t=10)  E(t=12)  E(t=9, LATE!)  Watermark(t=11)  E(t=15)
                                        ↑
                            arrives after the watermark already
                            passed t=11 — handled by "allowed lateness"
                            window config, or dropped if past that too
```

## 3. How It Really Works (Internals)

Watermarks are generated at the source (or shortly after) based on a **watermark
strategy** — commonly "bounded out-of-orderness": `watermark = max_event_time_seen -
allowed_delay`. This watermark then flows downstream through every operator. A windowed
operator only **fires** (emits a result) once the watermark passes the window's end —
this is the mechanism that decides *when* a tumbling/sliding/session window is
considered "closed enough" to compute.

With multiple parallel source partitions (e.g., multiple Kafka partitions), each
partition-reading task generates its own watermark, and a downstream operator takes the
**minimum** watermark across all its input partitions — a single slow or stalled
partition holds back the watermark (and therefore window firing) for the whole operator,
which is a common real production cause of "why is my streaming job's output delayed"
that has nothing to do with compute capacity.

## 4. Architecture & Design Pattern Spotlight

**Pattern: watermark propagation as a distributed progress-tracking protocol.** Rather
than a global clock, Flink lets *correctness* progress be inferred locally and combined
via a simple min-aggregation rule. This same "infer global progress from local
minimums" idea appears in distributed checkpoint barriers (Day 6) and in Kafka consumer
lag monitoring (min offset across partitions = true group lag).

## 5. Hands-On Lab

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common import Duration, Time
from pyflink.datastream.window import TumblingEventTimeWindows

env = StreamExecutionEnvironment.get_execution_environment()

# assign timestamps from your event's own field + bounded-out-of-orderness watermarks
watermark_strategy = (
    WatermarkStrategy
    .for_bounded_out_of_orderness(Duration.of_seconds(5))
    .with_timestamp_assigner(lambda event, ts: event.event_time_ms)
)

stream = env.from_collection(your_out_of_order_events).assign_timestamps_and_watermarks(watermark_strategy)

windowed = (
    stream.key_by(lambda e: e.user_id)
          .window(TumblingEventTimeWindows.of(Time.seconds(10)))
          .allowed_lateness(Time.seconds(30))  # <- accept events up to 30s late
          .reduce(lambda a, b: a.merge(b))
)
```
Feed in a handful of events with timestamps deliberately out of arrival order (including
one arriving well after its window "should" have closed) and observe: does it land in
the right window because of allowed lateness, or get dropped because it's later than
that?

## 6. Real-World Product Comparison

- Flink's watermark model is the reference implementation of the **Dataflow Model**
  (Google's paper) — the same conceptual model behind Google Cloud Dataflow/Apache Beam.
- **Spark Structured Streaming** has a simpler watermark model tied directly to its
  micro-batch triggers — correctness-wise similar, but coarser-grained since it's bound
  to batch boundaries rather than continuous per-record watermark advancement.
- **Uber's real-time platform** relies heavily on precise event-time semantics for
  pricing and ETA calculations, where using processing time instead would produce
  systematically wrong results whenever there's network delay — a correctness
  requirement, not a performance one.

## 7. Common Production Pitfalls

- Using processing time "because it's simpler" for a job where correctness actually
  depends on true event ordering — the classic mistake for teams new to streaming.
- Setting allowed lateness to 0 by default, silently dropping legitimately late (but
  still valuable) data with no error or warning.
- Not accounting for one stalled/idle Kafka partition holding back the watermark (and
  therefore all window results) for an entire operator — a job can look "stuck" when
  really one partition just isn't producing events.

## 8. Review Questions
1. Why is event time the only option for correctness under out-of-order arrival?
2. What does a watermark of value T actually assert?
3. Why does one slow partition hold back window firing for the whole downstream operator?
4. What's the practical difference between "dropped" and "handled via allowed lateness"?

## 9. Proficiency Checkpoint
If you can explain why a downstream operator's watermark is the *minimum* across its
inputs, and why that matters operationally, you're at Level 2 moving into Level 3.

## Next
Day 4 covers windowing types (tumbling/sliding/session) in depth — the thing watermarks
exist to make correct in the first place.
