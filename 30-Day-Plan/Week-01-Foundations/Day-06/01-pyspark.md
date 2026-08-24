# Day 6: PySpark — Structured Streaming

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Run a Structured Streaming job with a processing-time trigger, inspect its checkpoint
directory, and explain precisely what "micro-batch" means as an execution model.

## 2. Core Concept (basics → advanced)

**Structured Streaming** lets you write the same DataFrame API you already know, but
against an unbounded input — Spark treats the stream as "a table that keeps growing,"
and re-runs (conceptually) your query against each new increment of data. Under the
hood, it's still fundamentally **micro-batch**: Spark accumulates newly-arrived data
for a bounded interval (or trigger condition), processes it as a small batch job (with
the full Catalyst-optimized batch execution engine you already know from Days 1-2), then
moves to the next micro-batch.

```
True streaming (Flink):     event → processed individually, continuously

Micro-batch (Spark):        [batch of events] → processed as one small batch job
                             [batch of events] → processed as one small batch job
                             [batch of events] → processed as one small batch job
                             (each micro-batch is a real, if small, Spark job —
                              with all the DAG/stage/task machinery from Day 3)
```

**Triggers** control the micro-batch cadence: `trigger(processingTime="10 seconds")`
runs a new micro-batch every 10 seconds (even if there's no new data — an empty batch);
`trigger(availableNow=True)` processes all currently-available data as a finite batch
then stops (useful for backfills); Spark also supports a `continuous` processing mode
for lower latency, though with a narrower operator feature set than micro-batch mode.

## 3. How It Really Works (Internals)

**Checkpointing** in Structured Streaming stores two things persistently: the
**offsets** already processed (so a restart resumes exactly where it left off, not from
the beginning) and **state** for stateful operations (aggregations, joins — a running
count needs to survive a restart too). This checkpoint directory is what makes
Structured Streaming's fault tolerance work: on restart after a failure, Spark reads the
last committed offsets and state, and resumes the micro-batch loop from there — exactly
once semantics for the output, provided your sink is idempotent or transactional.

**Watermarking** here plays a similar role to Flink's (Day 3), but at micro-batch
granularity: Spark tracks the maximum event-time seen so far, subtracts your configured
delay threshold, and uses that watermark to decide when to drop old state for
stateful aggregations (so a windowed aggregation's state doesn't grow forever) —
conceptually the same idea as Flink's watermark, but advancing once per micro-batch
rather than continuously per-record.

## 4. Architecture & Design Pattern Spotlight

**Pattern: micro-batch as an approximation of continuous processing.** Micro-batch
reuses an existing, mature batch engine (Catalyst, the whole DAG scheduler) rather than
building a separate continuous-processing runtime from scratch — a real engineering
trade-off (simpler implementation, slightly higher latency floor) versus Flink's
purpose-built continuous dataflow engine. This exact contrast is the foundation for Week
4's Lambda vs. Kappa architecture discussion — micro-batch streaming is, in a real
sense, "the batch and speed layers converging into one API," while true streaming asks
"why have two layers at all?"

## 5. Hands-On Lab

```python
stream_df = spark.readStream.format("rate").option("rowsPerSecond", 5).load()

query = (
    stream_df.groupBy(F.window("timestamp", "10 seconds")).count()
    .writeStream
    .outputMode("update")
    .trigger(processingTime="10 seconds")
    .option("checkpointLocation", "/tmp/day6_checkpoint")
    .format("console")
    .start()
)
query.awaitTermination(60)
```
While it's running, inspect `/tmp/day6_checkpoint/` — find the `offsets/` and
`commits/` subdirectories. Stop the query, restart it with the *same* checkpoint
location, and confirm it resumes rather than reprocessing from scratch (check the
offset numbers in the new files against the old ones).

## 6. Real-World Product Comparison

- Structured Streaming's micro-batch model is a deliberate design choice by Databricks
  to let existing Spark batch expertise and tooling (the entire Catalyst optimizer)
  apply directly to streaming, rather than requiring a separate streaming-specific skill
  set — a real organizational/adoption argument, not just a technical one.
- Contrast directly with **Flink's** continuous, record-at-a-time model (Day 3) — this
  is the exact comparison Week 4's Lambda/Kappa architecture day will revisit using your
  own S6 benchmark as the case study.

## 7. Common Production Pitfalls

- Choosing a `processingTime` trigger interval shorter than your actual micro-batch
  processing time — batches start queueing up behind each other, and latency grows
  unboundedly rather than staying bounded.
- Deleting or moving the checkpoint directory between deployments without understanding
  the consequence — this discards all offset/state history, meaning the job effectively
  restarts "from the beginning" (or from whatever `startingOffsets` default applies).
- Assuming Structured Streaming and true streaming (Flink) have identical latency
  characteristics — the micro-batch model has an inherent latency floor tied to the
  trigger interval, which matters for genuinely latency-sensitive use cases.

## 8. Review Questions
1. What specifically does the checkpoint directory store, and why does that make exactly
   -once semantics possible?
2. Why is Structured Streaming still fundamentally micro-batch, even though the API
   looks continuous?
3. What happens if your trigger interval is shorter than actual processing time per
   batch?
4. Why does watermarking matter even in a micro-batch model, not just in true streaming?

## 9. Proficiency Checkpoint
If you can explain Structured Streaming's execution model accurately (not just "it's
like Flink but for Spark") and correctly predict checkpoint behavior across a restart,
you're at Level 2 moving into Level 3.

## Next
Day 7 is this week's lab + review — you'll stand up multiple systems together and write
your first ADR, applying everything from Days 1-6 in one sitting.
