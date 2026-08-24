# Day 10: Flink — Bounded vs. Unbounded Sources (Your Live JobManager Issue)

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Deliberately misconfigure a source as bounded on a job meant to run forever, watch it
reach `FINISHED`, and fix it — a direct, deliberate rehearsal of your real production
incident.

## 2. Core Concept (basics → advanced)

Every Flink source is either **bounded** (has a known end — a file, a fixed database
snapshot, a Kafka topic read with an explicit end offset) or **unbounded** (runs
forever — a live Kafka topic with no end offset configured). This isn't just metadata:
it changes how the **entire job** behaves, because a job's overall boundedness is
derived from its sources — if *every* source is bounded, Flink treats the whole job as
a **batch job** that runs to completion and then terminates; if *any* source is
unbounded, the job runs as a genuine **streaming job** that never terminates on its own.

```
Unbounded source (intended):        Bounded source (misconfigured):

Kafka topic, no end offset          Kafka topic with an explicit end offset,
  → job runs FOREVER                  or a connector defaulting to bounded mode
  → JobManager stays RUNNING           → job processes available data, then
                                       → transitions to FINISHED
                                       → JobManager considers the job DONE
                                       → any downstream consumer waiting on
                                         continuous output just... stops getting it
```

This is precisely the shape of a JobManager cycling to `FINISHED` unexpectedly on a job
meant to run forever: the job isn't crashing — it's **completing**, because something
in its source configuration told Flink "this is bounded," and Flink correctly (from its
own point of view) ran it to completion and stopped.

## 3. How It Really Works (Internals)

For the Kafka connector specifically, boundedness is controlled by the configured
**stopping offset behavior** — `setBounded(OffsetsInitializer...)` (or, in older/table
API configuration, options that imply a bounded read) tells Flink exactly where to
stop reading, at which point the source signals "no more splits" and the job's overall
execution mode resolves to batch/bounded, triggering a clean shutdown once all buffered
data is processed. A job silently sliding into this mode usually traces back to one of:
a connector default that assumes bounded unless told otherwise, a configuration value
copied from a batch/backfill job template without updating it for streaming use, or an
explicit (but forgotten) end-offset setting left over from an earlier one-time
backfill run of the same job.

Consumer lag then accumulates for the entirely mundane reason that **nothing is reading
new messages anymore** — the JobManager isn't unhealthy, it did exactly what its
configuration told it to do; the actual bug is upstream of any Flink runtime behavior,
in the source configuration itself.

## 4. Architecture & Design Pattern Spotlight

**Pattern: source boundedness as a first-class execution-mode decision, not a side
detail.** Contrast this with **Spark's** explicit API-level split (`spark.read` for
batch vs. `spark.readStream` for streaming, Week 1 Day 6) — Spark forces you to choose
your execution mode up front, syntactically, making an accidental batch-vs-streaming
mix-up much harder to fall into by mistake. Flink's unified API is more elegant (one
set of operators work for both modes) but pushes the boundedness decision down into
source configuration, exactly where your real incident originated — a genuine
trade-off between API elegance and this specific class of misconfiguration risk.

## 5. Hands-On Lab

```python
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer

# MISCONFIGURED — bounded, will FINISH after reading existing data:
source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("events") \
    .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
    .set_bounded(KafkaOffsetsInitializer.latest()) \
    .build()
```
Run a job with this source and a simple counting operator against a topic with a
continuous producer running alongside it. Watch the Flink Web UI — the job should
transition to `FINISHED` once it catches up to `latest()` at start time, even while the
producer keeps sending new messages. Confirm consumer lag (via
`kafka-consumer-groups.sh --describe`) starts climbing on that topic once the job is
`FINISHED`. Now fix it:
```python
source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("events") \
    .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
    .build()   # no .set_bounded(...) at all — unbounded, runs forever
```
Confirm the job now stays `RUNNING` indefinitely and lag stays flat.

## 6. Real-World Product Comparison

- This is **directly** the mechanism behind your production JobManager-instability
  investigation — what looked like instability was very plausibly a job correctly
  reaching a designed completion state that shouldn't have been reachable for a
  perpetual streaming job.
- **Uber and Alibaba** (heavy Flink operators) both maintain explicit internal
  conventions/linting to prevent exactly this class of misconfiguration — treating
  "does this job's source configuration match its intended execution mode" as a
  reviewable, checkable property of a job definition, not something to catch only in
  production.

## 7. Common Production Pitfalls

- Copying a source configuration from a one-time backfill job (which correctly uses a
  bounded read) into a job meant to run perpetually, without removing the bounded
  configuration.
- Monitoring "is the JobManager up" without also monitoring "is the job in `RUNNING`
  state, actively consuming" — a `FINISHED` job can leave its JobManager process
  healthy while producing zero ongoing work.
- Not correlating consumer lag growth with job *state* transitions in the same
  investigation — lag graphs and job-state graphs are often checked by different
  people/dashboards, delaying the actual root-cause connection.

## 8. Review Questions
1. Why does a job's overall execution mode depend on the boundedness of *every* source?
2. What specifically causes a Kafka source to behave as bounded rather than unbounded?
3. Why is monitoring job *state* (not just JobManager process health) essential for
   catching this failure mode?
4. Why does Spark's batch/streaming API split make this specific mistake structurally
   harder than Flink's unified API does?

## 9. Proficiency Checkpoint
If you can look at a real Flink job's source configuration and definitively state
whether it will run forever or eventually `FINISH`, you're at Level 3.5+ — this is
precisely the root-cause skill your live incident required.

## Next
Day 11 covers backpressure — credit-based flow control — the other major reason a
healthy-looking Flink job can silently fall behind.
