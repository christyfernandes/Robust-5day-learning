# Day 1: Flink — Stream Processing Foundations

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain the difference between true streaming and micro-batching in concrete
mechanical terms (not just "Flink is faster"), and describe Flink's runtime
architecture well enough to know what a JobManager vs. a TaskManager actually does.

## 2. Core Concept (basics → advanced)

**True streaming vs. micro-batch.** Spark Structured Streaming processes data in small
batches on a timer (e.g., every 1 second, gather what's arrived, run the batch DAG).
Flink processes **one record at a time** as it arrives — there's no artificial batch
boundary. This isn't just a latency difference; it changes how state and windowing
work under the hood, because Flink's engine is fundamentally built around continuous
operators holding state indefinitely, not repeated short-lived batch jobs.

**Architecture:**
```
                    ┌───────────────┐
                    │  JobManager   │  ← coordinates execution, tracks checkpoints,
                    │ (master)      │     handles failure recovery, schedules tasks
                    └───────┬───────┘
              ┌─────────────┼─────────────┐
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │TaskManager│ │TaskManager│ │TaskManager│   ← worker processes, each with
        │  (slots)  │ │  (slots)  │ │  (slots)  │      N "task slots" = parallel
        └───────────┘ └───────────┘ └───────────┘      execution units
```

A **task slot** is a fixed share of a TaskManager's resources where one parallel
instance of an operator pipeline runs. Parallelism in Flink is set per-operator (or
globally as a default), and the total number of slots across all TaskManagers caps how
much parallelism you can actually run concurrently.

**DataStream API basics:**
```python
from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
ds = env.from_collection(["hello flink", "hello stream"])

counts = (
    ds.flat_map(lambda line: line.split())
      .map(lambda w: (w, 1))
      .key_by(lambda x: x[0])
      .sum(1)
)
counts.print()
env.execute("word_count")
```

## 3. How It Really Works (Internals)

Unlike Spark's lazy-DAG-then-action model, a Flink job is a long-running **dataflow
graph** of operators connected by streams, and once you call `.execute()`, it typically
keeps running indefinitely (for unbounded sources) rather than terminating after one
computation. This distinction — **does this job have a natural end, or should it run
forever?** — matters enormously in production and is the exact subject of a real
production issue you'll debug directly in Week 2 (Day 10): a job unexpectedly reaching
a "FINISHED" state when it was supposed to run perpetually, almost always traceable to
a source that Flink considers **bounded** when it was meant to be treated as
**unbounded**.

`key_by()` performs a logical partitioning of the stream — same key always routes to
the same parallel task instance, which is what makes keyed state (Day 5) possible at all.

## 4. Architecture & Design Pattern Spotlight

**Pattern: the dataflow programming model.** Flink (and its ancestor, the Stratosphere
research project) treats a program as a graph of operators processing an unbounded
stream of records — the same conceptual model as Google's Dataflow paper, which is also
what Apache Beam and Google Cloud Dataflow implement. If you've ever seen a Beam
pipeline, the mental model transfers almost directly.

## 5. Hands-On Lab
Run the word-count snippet above locally (`pip install apache-flink`). Then modify it to
read from a Python list that simulates a never-ending stream (a generator), and observe
that the job keeps running — this is your first hands-on encounter with "unbounded"
behavior, which you'll need for Day 10's real-bug lab.

## 6. Real-World Product Comparison

- **Alibaba** invested so heavily in Flink for its Singles' Day real-time analytics that
  it built "Blink," its internal fork, later merged back upstream — a strong signal for
  how seriously true low-latency streaming matters at that scale.
- **Uber and Stripe** use Flink for real-time fraud detection and analytics, where
  sub-second detection genuinely changes outcomes (a fraudulent transaction blocked in
  200ms vs. 5 seconds later is a different product).
- Contrast with **Kafka Streams**: also true per-record streaming, but it's a *library*
  embedded in your JVM application rather than a separate cluster — simpler
  operationally, but you lose Flink's dedicated resource management, sophisticated
  windowing, and CEP capabilities.

## 7. Common Production Pitfalls
- Treating "the job finished" as always a bug signal or always fine — it depends
  entirely on whether the source was meant to be bounded. This ambiguity is exactly
  what causes real incidents (yours included) and is worth internalizing now, before
  Week 2's deep dive.
- Setting parallelism higher than available task slots — the job simply won't start,
  with a scheduling error that's easy to misread as something more exotic.
- Assuming Flink's low latency is "free" — it comes from operators holding state
  continuously, which has real memory/checkpointing cost (Day 5–6).

## 8. Review Questions
1. Mechanically, what's different between how Flink and Spark Structured Streaming
   process each new record?
2. What does a task slot actually represent?
3. Why does `key_by()` matter for later stateful operations?
4. What are the two very different meanings a Flink job reaching "FINISHED" could have?

## 9. Proficiency Checkpoint
If you can explain JobManager vs. TaskManager vs. task slot, and articulate the
true-streaming-vs-micro-batch distinction mechanically (not just "faster/slower"),
you're at Level 2.

## Next
Day 2 covers the DataStream API's core transformations and parallelism in more depth —
the building blocks you'll need before windowing (Day 4) and state (Day 5) make sense.
