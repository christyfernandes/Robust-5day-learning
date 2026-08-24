# Day 17: Architecture — Observability: Metrics, Logs, Traces & Correlation IDs

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Sketch how a single correlation ID would flow through your own pipeline's 4+ systems
(Kafka → Flink → Redis/Elasticsearch/ClickHouse), end to end.

## 2. Core Concept (basics → advanced)

The **three pillars of observability**, each answering a different question:
- **Metrics**: aggregated, numeric time-series data (Kafka lag, Flink checkpoint
  duration, ClickHouse query count) — good for "is something wrong, and how bad,"
  cheap to store long-term, but low-resolution for any *individual* event.
- **Logs**: discrete, timestamped event records — good for "what exactly happened,
  in detail," but expensive to store at high volume and hard to correlate across
  systems without a shared identifier.
- **Traces**: a **connected sequence of spans** representing one logical operation's
  full journey across multiple systems/services — good specifically for "what
  happened to *this one request/event*, across every system it touched."

**Correlation IDs** are the mechanism that makes distributed tracing possible: a
unique identifier generated when a request/event first enters the system, propagated
through every subsequent hop (attached to every log line, every span, every
downstream message) — letting you reconstruct one logical operation's complete
journey by searching for that one ID across otherwise-disconnected systems' logs and
metrics.

```
Event enters pipeline, tagged with correlation_id=abc123
     │
     ▼ Kafka (message carries correlation_id in headers)
     ▼ Flink (processes, logs correlation_id, may enrich/carry it forward)
     ▼ Redis (cache write logged with correlation_id, if logging that granularly)
     ▼ Elasticsearch/ClickHouse (final write, still tagged)

Searching logs/traces for "abc123" across ALL these systems reconstructs
the event's ENTIRE journey — otherwise, each system's logs are an
isolated island with no way to connect them to the same logical operation
```

## 3. How It Really Works (Internals)

The genuine engineering challenge isn't generating a correlation ID — it's
**consistently propagating it through every hop**, including hops where it's easy to
forget (a Flink job's internal transformation logic, a Redis write that doesn't
naturally carry request context, a batch job that processes many events together and
needs to track *which* correlation ID(s) contributed to a given output). This is
precisely why observability needs to be a deliberate, designed-in property of a
pipeline from the start, not something bolted on after the fact — retrofitting
correlation-ID propagation into an existing multi-system pipeline where it wasn't
designed in requires touching every single hop's code, a substantial undertaking.

## 4. Architecture & Design Pattern Spotlight

**Pattern: the three pillars of observability, connected by correlation IDs across
system boundaries.** This is the natural capstone to this week's monitoring lessons
across every individual system (Spark UI, Kafka lag, Flink metrics, Redis `INFO`,
Elasticsearch cluster health, ClickHouse system tables) — each system's own
monitoring answers "is *this* system healthy," while correlation-ID-based tracing
answers the cross-system question "what happened to *this specific event*, across
everything it touched," which none of the individual systems' own monitoring can
answer alone.

## 5. Hands-On Lab

Sketch your own real pipeline (Kafka → Flink → Redis/Elasticsearch/ClickHouse, or
your actual Sunbird telemetry pipeline) with a single hypothetical event flowing
through it, tagged with one correlation ID at the entry point. For each hop, note
explicitly:
- Is the correlation ID naturally available at this hop today (e.g., a Kafka
  message header), or would propagating it require a code change?
- What would you actually search for (which log fields, which system) to
  reconstruct this event's journey if you needed to debug why it produced an
  unexpected result three systems downstream?
- Where's the weakest link — the hop most likely to silently drop the correlation
  ID today?

## 6. Real-World Product Comparison

- **OpenTelemetry** has become the standard, vendor-neutral framework for
  implementing exactly this pattern (metrics, logs, and traces, connected via
  propagated context) across heterogeneous systems — worth knowing by name as the
  current industry-standard tool for this problem.
- Large-scale distributed systems at companies like **Uber and Netflix** invest
  heavily in exactly this tracing infrastructure specifically because multi-system
  pipelines (very similar in shape to your own Kafka→Flink→storage pipeline) become
  genuinely difficult to debug without it once they exceed a small number of hops.

## 7. Common Production Pitfalls

- Building rich per-system monitoring (this week's earlier lessons) without ever
  connecting them via correlation IDs — leaving "what happened to this specific
  event across the whole pipeline" as an unanswerable question despite good
  per-system observability.
- Retrofitting correlation-ID propagation as an afterthought rather than designing
  it in from a pipeline's inception — a substantially harder and more error-prone
  undertaking.
- Generating correlation IDs but not consistently searching/filtering by them during
  actual incident investigation — the mechanism only has value if it's actually used.

## 8. Review Questions
1. What distinct question does each of metrics, logs, and traces answer?
2. Why is correlation-ID propagation harder in practice than it sounds in theory?
3. Why can't individual systems' own monitoring (Kafka lag, ClickHouse system
   tables) answer the cross-system "what happened to this event" question alone?
4. Where's the weakest link in your own real pipeline's correlation-ID propagation?

## 9. Proficiency Checkpoint
If you can sketch a real, accurate correlation-ID flow through your own multi-system
pipeline and identify its weakest propagation point, you're at Level 3.5 — a
directly actionable finding for improving your team's incident-investigation
capability.

## Next
Day 18 covers security architecture — zero trust, defense in depth — the next
production-hardening layer after monitoring.
