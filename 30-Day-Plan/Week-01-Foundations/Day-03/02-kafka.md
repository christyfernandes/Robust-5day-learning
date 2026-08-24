# Day 3: Kafka — Consumer Groups & Rebalancing

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain how Kafka distributes partitions across a consumer group, describe what
triggers a rebalance, and predict what a specific assignment strategy will do with a
given partition/consumer count.

## 2. Core Concept (basics → advanced)

A **consumer group** is Kafka's mechanism for horizontal scale-out of consumption: every
partition in a subscribed topic is assigned to exactly one consumer *within* the group,
but the same message is still delivered independently to every *other* group subscribed
to that topic. This is fundamentally different from a traditional message queue's
competing-consumers model, where a message goes to *one* consumer, period — Kafka gives
you both fan-out (across groups) and load-balancing (within a group) simultaneously,
because delivery is really just "the group tracks its own read offset into the log,"
not "the broker removes a delivered message."

```
Topic: orders (3 partitions)

Consumer Group "billing":                 Consumer Group "analytics":
  Consumer A ── P0                          Consumer X ── P0, P1, P2
  Consumer B ── P1                          (single consumer, all partitions)
  Consumer C ── P2

Same messages, delivered independently to both groups.
```

**Partition assignment strategies** decide which consumer in a group gets which
partitions:
- **Range**: partitions of each topic assigned in contiguous ranges per consumer — can
  cause imbalance if a consumer subscribes to many topics with the same range logic.
- **Round-robin**: partitions spread evenly across all consumers regardless of topic —
  more even, but every rebalance reassigns almost everything.
- **Sticky**: minimizes partition movement across rebalances while still balancing load
  — the practical default for most modern use.
- **Cooperative-sticky**: like sticky, but rebalances incrementally (only reassigning the
  specific partitions that need to move) instead of the old "stop-the-world" model where
  every consumer gives up all partitions before reassignment.

## 3. How It Really Works (Internals)

One broker per consumer group acts as the **group coordinator**. Every consumer sends
periodic heartbeats to it. A **rebalance** is triggered when: a consumer joins, a
consumer leaves (including a heartbeat timeout — perceived as a crash even if it's just a
long GC pause), or the topic's partition count changes.

With the old **eager** rebalancing protocol, every consumer in the group revokes *all* of
its partitions before the new assignment is computed and handed out — meaning a brief
total-stop for the whole group on every rebalance, however small the actual membership
change. **Cooperative rebalancing** (the modern default via `CooperativeStickyAssignor`)
instead computes the new assignment, and only the specific partitions that actually need
to move are revoked and reassigned — the rest of the group keeps consuming uninterrupted.
This is a meaningful production difference: a large consumer group on the eager protocol
can see multi-second full-group pauses on every single scaling event.

## 4. Architecture & Design Pattern Spotlight

**Pattern: partitioned work distribution via a coordinator.** One coordinator (per group)
owns membership and assignment; the actual data plane (partition reads) is fully
decentralized. You'll see this same shape in Flink's JobManager/TaskManager relationship
and in Kubernetes' scheduler — a small stateful coordinator, a large stateless data plane.

## 5. Hands-On Lab

```bash
# terminal 1: start consumer A in group "test-group"
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --group test-group

# terminal 2: start consumer B in the SAME group
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --group test-group

# terminal 3: produce a few messages, watch A and B split the partitions between them

# now start a THIRD consumer in the same group and watch both terminals' logs —
# you should see "Revoking previously assigned partitions" / rebalance messages
```
Check `--describe` on the group (`kafka-consumer-groups.sh --describe --group
test-group`) before and after adding the third consumer, and note exactly which
partitions moved.

## 6. Real-World Product Comparison

- **RabbitMQ**'s classic competing-consumers pattern delivers each message to exactly one
  consumer across the *entire* queue — there's no group-vs-group fan-out without
  explicitly fanning out via exchanges/multiple queues, which Kafka gives "for free" via
  consumer groups.
- **LinkedIn** (Kafka's birthplace) runs enormous consumer groups across independent
  teams' analytics, monitoring, and processing pipelines — the same log, read
  independently and non-destructively by dozens of groups, was the entire founding
  motivation for Kafka's design.

## 7. Common Production Pitfalls

- Setting a consumer's processing loop to do slow, blocking work (e.g., a synchronous
  network call per message) without tuning `max.poll.interval.ms` — the group coordinator
  perceives the consumer as dead and rebalances away its partitions mid-processing,
  which can cause duplicate processing on top of the outage.
- Assuming more consumers always means more throughput — a consumer group can never have
  more *active* consumers than partitions; the extras sit idle.
- Not distinguishing "consumer crashed" rebalances (needs investigation) from "we scaled
  the group" rebalances (expected) in monitoring/alerting.

## 8. Review Questions
1. Why can two different consumer groups both read every message from the same topic?
2. What's the practical cost difference between eager and cooperative rebalancing?
3. If you have 6 partitions and 8 consumers in one group, what happens to the extra 2?
4. What's one production cause of an *unwanted* rebalance that has nothing to do with
   scaling?

## 9. Proficiency Checkpoint
If you can correctly predict a rebalance's partition reassignment for a given
assignor and consumer count, you're at Level 2 and ready for broker-internals depth.

## Next
Day 4 goes inside the broker itself — log segments, ISR, and leader election — the
mechanics behind what makes a partition durable in the first place.
