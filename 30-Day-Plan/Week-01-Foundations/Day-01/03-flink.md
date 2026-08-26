# Day 1: Flink — Stream Processing Foundations

## Time: ~30 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain the difference between true streaming and micro-batching in concrete
mechanical terms (not just "Flink is faster"), and describe Flink's runtime
architecture well enough to know what a JobManager vs. a TaskManager actually does.

## 2. Core Concept (basics → advanced)

**Start here if Flink is genuinely new to you.** Flink is a system for processing data
that arrives continuously and potentially never stops (a **stream** — think a live
feed of events, like clicks or sensor readings, rather than a fixed file sitting on
disk). You write a program describing a chain of operations (filter this, transform
that, sum this up per key), and Flink runs that chain continuously against every
record as it arrives, for as long as the job keeps running — which, for a genuine live
data source, can be forever.

**True streaming vs. micro-batch — the core distinction, explained plainly first.**
Spark Structured Streaming (Week 1, Day 6) fakes continuous processing by running many
small, repeated *batch* jobs on a timer — e.g., every 1 second, gather whatever new
records arrived in that window, and run a normal (small) batch computation over just
that chunk. Flink does something genuinely different: it processes **one record at a
time**, the instant it arrives, with no artificial "wait and gather a batch" step at
all. This isn't just a speed difference — it changes how the underlying engine has to
be built: Flink's operators are long-lived and hold their own state continuously
across the entire life of the job, rather than being freshly recreated for each new
mini-batch the way Spark's approach works.

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

In plain terms: the **JobManager** is the one coordinating brain of the cluster (there's
one active JobManager per cluster) — it never touches your actual data, only decides
what work goes where and tracks whether everything is healthy. A **TaskManager** is a
worker process (there are usually several, often on separate machines) that actually
runs your operators against real data. A **task slot** is a fixed share of one
TaskManager's resources, sized so that exactly one parallel instance of your operator
pipeline can run in it — if you ask for parallelism of 4, Flink needs 4 available task
slots (possibly spread across several TaskManagers) to actually run your job at that
parallelism.

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
**unbounded**. (The word-count example above, run against a fixed Python list, *is*
bounded — it will finish and print its results, unlike a real production Flink job
reading from a live Kafka topic.)

`key_by()` performs a logical partitioning of the stream — same key always routes to
the same parallel task instance, which is what makes keyed state (Day 5) possible at
all. Crucially, `key_by()` does **not** wait to gather all records for a key before
doing anything — each record still flows through and gets processed the instant it
arrives; it's the routing (which task instance handles it) and the per-key state
tracking (running sums, etc.) that key_by makes possible.

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

### Sample Output

Running the snippet exactly as written above prints:

```
('hello', 1)
('flink', 1)
('hello', 2)
('stream', 1)
```

Reading this line by line — and this is the single clearest illustration of
"true streaming" you'll see all day:

- `flat_map` turns the two input lines into four individual words, in arrival order:
  `hello`, `flink` (from line 1), then `hello`, `stream` (from line 2).
- `map` turns each into a `(word, 1)` pair, still in that same order.
- `key_by(word).sum(1)` keeps a **running total per key**, and — this is the important
  part — **emits an updated result the instant each record is processed**, not just
  one final answer at the end. Watch what happens to `hello` specifically: the first
  time it's seen, Flink immediately emits `('hello', 1)`. Two records later, the
  *second* `hello` arrives, its running sum becomes 2, and Flink immediately emits
  `('hello', 2)` — a second, updated line for the same key.
- If this were a Spark Structured Streaming micro-batch instead, and both `hello`
  records happened to land in the same micro-batch window, you would only ever see one
  combined output line, `('hello', 2)` — never the intermediate `('hello', 1)`. Seeing
  **both** the intermediate and the final value, as separate emitted records, is
  exactly what "process one record at a time, continuously" looks like from the
  outside, versus "gather a batch, then compute."
- `flink` and `stream` each appear once in the input, so each only ever gets one
  output line, at count 1 — nothing surprising there, but it's worth noticing they
  interleave with `hello`'s updates in strict arrival order, not grouped together by
  key in the output.

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
<details><summary>Show answer</summary>

Flink processes each record individually, the instant it arrives, through a
long-lived chain of operators that hold their state continuously. Spark Structured
Streaming instead waits, gathers whatever records arrived within a fixed time window
(a micro-batch), and then runs a normal short-lived batch computation over that whole
chunk at once. This is why Flink can emit an intermediate result mid-key (like
`('hello', 1)` before `('hello', 2)`) that a micro-batch engine would typically
collapse into a single combined output.

</details>

2. What does a task slot actually represent?
<details><summary>Show answer</summary>

A fixed share of one TaskManager's resources, sized to run exactly one parallel
instance of your job's operator pipeline. If your job's parallelism is 4, Flink needs
4 available task slots (on one or several TaskManagers) to actually execute it at
that parallelism — it's the concrete unit of "how much of this job can run at once."

</details>

3. Why does `key_by()` matter for later stateful operations?
<details><summary>Show answer</summary>

`key_by()` guarantees that every record with the same key is always routed to the
same parallel task instance — without that guarantee, you couldn't safely keep
per-key state (like a running sum, Day 5's topic) local to one task, since the state
for a given key could otherwise be scattered across different instances with no
single place holding the full picture.

</details>

4. What are the two very different meanings a Flink job reaching "FINISHED" could have?
<details><summary>Show answer</summary>

It can mean the job correctly finished processing a genuinely bounded source (like
today's word-count example, which reads a fixed Python list and has nothing left to
process) — completely normal and expected. Or, it can mean a job that was *meant* to
run forever against a live, unbounded source (like a Kafka topic) was misconfigured
in a way that made Flink treat that source as bounded, causing it to stop
prematurely — this second case is a real production bug, and the exact subject of
Week 2 Day 10's investigation.

</details>

## 9. Proficiency Checkpoint

**Quick Recap:**
- **JobManager** = the one coordinating brain of the cluster; schedules work, tracks
  checkpoints, handles failure recovery — never touches your actual data.
- **TaskManager** = a worker process that actually runs your operators against data;
  usually several, often on different machines.
- **Task slot** = a fixed resource share on a TaskManager sized for exactly one
  parallel operator-pipeline instance; total slots across all TaskManagers caps your
  achievable parallelism.
- **True streaming (Flink)**: one record processed at a time, continuously, by
  long-lived stateful operators.
- **Micro-batch (Spark Structured Streaming)**: small batch jobs re-run on a timer,
  each one a short-lived computation over whatever arrived in that window.
- **`key_by()`**: routes same-key records to the same task instance, always — the
  prerequisite for safe per-key state.
- **Bounded vs. unbounded**: a bounded source (a fixed list, a file) naturally
  finishes; an unbounded source (a live Kafka topic) should run forever — treating one
  as the other is a real, common production bug (Week 2, Day 10).

If you can explain JobManager vs. TaskManager vs. task slot, and articulate the
true-streaming-vs-micro-batch distinction mechanically (not just "faster/slower"),
you're at Level 2.

## Next
Day 2 covers the DataStream API's core transformations and parallelism in more depth —
the building blocks you'll need before windowing (Day 4) and state (Day 5) make sense.
