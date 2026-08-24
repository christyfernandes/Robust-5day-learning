# Day 12: Flink — Complex Event Processing (CEP)

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Write a CEP pattern detecting 3 failed logins within 1 minute, and explain how pattern
matching differs from ordinary windowed aggregation.

## 2. Core Concept (basics → advanced)

Everything covered so far this month aggregates or transforms events — CEP asks a
different question: **does a specific sequence/pattern of events occur, in a specific
order, within a specific time constraint?** Flink's CEP library lets you define a
pattern (e.g., "event A, followed by event B within 10 seconds, not followed by event
C") declaratively, and Flink continuously matches incoming events against it, emitting
a result whenever the full pattern is satisfied.

```
Ordinary windowed count:            CEP pattern:

"how many login-failed events       "3 login-failed events for the SAME user,
 in this 1-minute window?"           each within 1 minute of the FIRST one" —
 (aggregate — order doesn't          a specific temporal SEQUENCE that must
  matter, just the count)            match, not just a count within a window
```

This distinction matters: a plain windowed count of "3+ failures in a window" can
false-positive on 3 failures spread awkwardly across a fixed window boundary (2 near
the end of window N, 1 near the start of window N+1, split across two windows and
never counted together) — CEP's pattern matching is defined relative to the *events
themselves* (sliding, event-relative timing), not fixed window boundaries, avoiding
this specific false-negative.

## 3. How It Really Works (Internals)

A CEP pattern compiles into an internal **non-deterministic finite automaton (NFA)** —
conceptually similar to how a regular expression engine matches a string, but operating
over a stream of events with time constraints instead of characters. Each partial
match-in-progress consumes state (Week 1, Day 5) to track "which events have matched so
far, for which candidate sequence" — this is why CEP jobs with very loose patterns
(matching many candidate partial sequences simultaneously) or very long time windows
can accumulate substantial state, the same operational consideration from any other
stateful Flink job.

## 4. Architecture & Design Pattern Spotlight

**Pattern: pattern-matching over event sequences, using an automaton-based matching
engine.** This is a genuinely distinct processing paradigm from windowed aggregation
(Week 1, Day 4) — recognizing when a problem is actually "does this sequence occur"
rather than "what's the aggregate over this time period" is the key modeling skill;
CEP is the right tool specifically for the former, and a poor, awkward fit for the
latter (and vice versa).

## 5. Hands-On Lab

```python
from pyflink.cep import Pattern, PatternStream
from pyflink.common import Time

pattern = Pattern.begin("first_failure").where(lambda e: e.event_type == "login_failed") \
    .next("second_failure").where(lambda e: e.event_type == "login_failed") \
    .next("third_failure").where(lambda e: e.event_type == "login_failed") \
    .within(Time.minutes(1))

pattern_stream = PatternStream(login_events.key_by(lambda e: e.user_id), pattern)

alerts = pattern_stream.select(lambda match: f"ALERT: {match['first_failure'][0].user_id} had 3 failed logins in under 1 minute")
```
Feed a synthetic stream with one user having exactly 3 failed logins within 45
seconds (should alert), another user with 3 failed logins spread across 90 seconds
(should NOT alert, since it exceeds the 1-minute window), and a third user with only
2 failures (should not alert). Verify all three behave as expected.

## 6. Real-World Product Comparison

- **Fraud detection and security monitoring** systems (common at fintech and
  large-scale consumer platforms) are the canonical CEP use case — exactly the
  "sequence of specific events within a time constraint" shape this lesson's lab
  demonstrates.
- Contrast with **ksqlDB/Kafka Streams**, which have more limited native
  pattern-matching support compared to Flink CEP's dedicated NFA-based engine — for
  genuinely sequence-sensitive detection logic, Flink CEP is generally the more capable
  tool of the streaming engines covered this month.

## 7. Common Production Pitfalls

- Using CEP for what's really just a windowed count (order doesn't actually matter) —
  unnecessary complexity when a simpler windowed aggregation (Week 1, Day 4) would
  suffice and be easier to reason about and maintain.
- Writing overly loose patterns that match many partial sequences simultaneously,
  causing state size to grow larger than expected for the actual detection logic
  intended.
- Not setting a `within()` time constraint (or setting one far looser than needed) —
  unbounded or very long pattern-matching windows retain partial-match state far
  longer than necessary.

## 8. Review Questions
1. Why can a plain windowed count produce a false negative that CEP correctly avoids?
2. What does a CEP pattern compile into internally, and what does that explain about
   its state usage?
3. When is CEP the wrong tool, even though it could technically express a windowed
   count?
4. Why do loose patterns risk larger state than tight ones?

## 9. Proficiency Checkpoint
If you can correctly decide "CEP vs. windowed aggregation" for a stated detection
requirement and implement the CEP version correctly, you're at Level 3.

## Next
Day 13 covers Flink's scaling model — parallelism, slots, and reactive/autoscaling
mode — how a job like today's CEP pipeline actually scales under load.
