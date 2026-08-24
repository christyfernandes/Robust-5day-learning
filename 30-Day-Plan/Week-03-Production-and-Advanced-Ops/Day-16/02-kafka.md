# Day 16: Kafka — Reliability: Unclean Leader Election & min.insync.replicas

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Simulate a scenario where all ISR members are down, and identify the specific
configuration that would have prevented data loss.

## 2. Core Concept (basics → advanced)

Week 1, Day 4 established that only ISR members can normally become the new leader
after a failure. But what happens if **every** ISR member becomes unavailable
simultaneously (e.g., a correlated multi-broker failure)? Kafka faces an explicit
choice, governed by `unclean.leader.election.enable`:

- **Disabled (default, safe)**: the partition becomes **unavailable** for writes/reads
  until at least one ISR member returns — no data loss, but a real availability gap.
- **Enabled**: Kafka may elect a leader from **outside** the ISR (a replica that had
  fallen behind) — the partition becomes available again immediately, but any
  messages the out-of-sync replica never received are **silently and permanently
  lost**, with no error surfaced to indicate this happened.

```
All ISR members down, unclean election DISABLED (default):
  Partition UNAVAILABLE → writes/reads fail with clear errors →
  no data loss, but a real outage until an ISR member recovers

All ISR members down, unclean election ENABLED:
  An out-of-ISR replica becomes leader → partition AVAILABLE again →
  but any data only the down ISR members had is GONE, silently
```

## 3. How It Really Works (Internals)

This is the single clearest, most concrete instance of the availability-vs-
consistency (durability) trade-off in the entire Kafka curriculum — and it's a
**direct configuration knob**, not an abstract trade-off you passively accept. The
correct choice depends entirely on the actual cost of data loss for a given topic:
for a topic carrying, say, financial transaction events, disabled (the default) is
almost certainly correct — an availability gap is recoverable, silent data loss is
not. For a topic carrying, say, low-stakes UI telemetry where availability matters
more than never losing a message, enabling unclean election for that *specific* topic
might be a reasonable, deliberate trade — the decision should be made per-topic based
on actual business cost, not applied blanket across an entire cluster.

## 4. Architecture & Design Pattern Spotlight

**Pattern: consistency-vs-availability, made concrete as a single boolean
configuration knob.** This directly instantiates the PACELC framing from Week 1, Day
1 and Day 7's ADR exercise — today's lesson is the same trade-off, no longer abstract,
attached to a specific, nameable Kafka setting with a specific, quantifiable
consequence.

## 5. Hands-On Lab

```bash
kafka-topics.sh --create --topic unclean-test --partitions 1 --replication-factor 3 \
  --config min.insync.replicas=2 --bootstrap-server localhost:9092

# kill ALL 3 broker replicas for this partition (simulating a correlated failure)
# attempt to produce/consume — confirm the partition is UNAVAILABLE (default config)

# now restart brokers with unclean.leader.election.enable=true, repeat the failure,
# and observe a leader gets elected from a lagging replica instead —
# then check for missing messages that were only on the still-down brokers
```
Confirm the concrete difference: unavailability with a clear error (safe default) vs.
availability with silent data loss (opt-in, risky) — write down which specific topics
in your own production environment you'd consider enabling this for, and why.

## 6. Real-World Product Comparison

- **LinkedIn** and most serious Kafka operators leave unclean leader election
  disabled globally, and instead invest in **preventing** correlated multi-broker
  failures in the first place (proper rack/availability-zone awareness for replica
  placement) rather than accepting silent data loss as a fallback.
- This is the same trade-off decision framework as **`min.insync.replicas`** itself
  (Week 1, Day 4) — both are explicit, quantifiable durability-vs-availability knobs,
  not abstract concerns.

## 7. Common Production Pitfalls

- Enabling unclean leader election cluster-wide "for availability" without
  considering it per-topic based on actual data-loss cost.
- Not testing the "all ISR members down" scenario before it happens for real —
  understanding the *configured* behavior in the abstract is different from having
  actually observed it under a controlled simulation.
- Conflating "the partition is unavailable" (a visible, recoverable problem) with
  "we lost data" (an invisible, permanent problem) when reasoning about incident
  severity — they are very differently serious outcomes.

## 8. Review Questions
1. What specifically happens differently under each `unclean.leader.election.enable`
   setting when all ISR members are down?
2. Why is silent data loss worse than a visible availability gap, in most cases?
3. How does this setting directly instantiate the PACELC framing from Week 1?
4. Why might this setting reasonably differ per-topic rather than being a single
   cluster-wide choice?

## 9. Proficiency Checkpoint
If you can correctly reason about which specific topics should or shouldn't enable
unclean leader election, with a clear justification, you're at Level 3.5.

## Next
Day 17 covers Kafka monitoring — JMX metrics and consumer-lag alerting — the tooling
that would surface an ISR-shrinking situation before it becomes a full outage.
