# Day 4: Redis — Pub/Sub vs. Streams

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain the durability difference between Pub/Sub and Streams, and decide when Streams
is genuinely "enough" instead of standing up Kafka.

## 2. Core Concept (basics → advanced)

**Pub/Sub**: fire-and-forget broadcast. A publisher sends a message to a channel; every
*currently connected* subscriber receives it. If no one's listening, the message is
gone — there's no log, no replay, no persistence of any kind.

**Redis Streams**: an append-only log data structure (conceptually a lightweight Kafka
topic living inside Redis) — messages persist in the stream, consumers track their own
read position, and Streams adds **consumer groups** with per-message acknowledgment,
meaning a crashed consumer's unacknowledged messages can be claimed and reprocessed by
another consumer in the group.

```
Pub/Sub:    Publisher ──▶ [Channel] ──▶ currently-connected subscribers only
                                          (no listener when published = message lost)

Streams:    Producer ──▶ [Stream: persisted log] ──▶ Consumer Group
                                                        ├─ Consumer A (XREADGROUP, XACK)
                                                        └─ Consumer B (XREADGROUP, XACK)
                          (unacked messages sit in the Pending Entries List
                           until XACK'd or XCLAIM'd by another consumer)
```

## 3. How It Really Works (Internals)

A Stream entry has an ID that's itself a timestamp+sequence pair (`<ms>-<seq>`),
naturally ordering entries by arrival. `XREADGROUP` reads new entries for a consumer
group and moves them into that consumer's **Pending Entries List (PEL)** — entries stay
in the PEL until explicitly `XACK`'d. If a consumer crashes mid-processing, its
unacknowledged entries remain visible in the PEL, and another consumer can `XCLAIM` them
after an idle-time threshold — this is a genuine (if simpler) analog of Kafka's
consumer-group rebalancing and offset-commit model, implemented as a single Redis data
structure rather than a whole distributed system.

The honest limitation: Streams doesn't have Kafka's partition-based horizontal
scale-out — a single stream's throughput is bounded by Redis's (single-threaded, for
commands) processing capacity, and there's no built-in cross-datacenter replication
story equivalent to Kafka's MirrorMaker. Streams is genuinely "Kafka for a single node's
worth of throughput," not a drop-in Kafka replacement at scale.

## 4. Architecture & Design Pattern Spotlight

**Pattern: fire-and-forget broadcast (Pub/Sub) vs. durable consumer-group log
(Streams) — the exact same durability spectrum as Kafka itself vs. a simple
in-process event bus.** Recognizing "do I need replay/durability, or just live
notification" is the actual decision, not "Redis vs. Kafka" as a brand choice.

## 5. Hands-On Lab

```bash
# create a stream + consumer group
redis-cli XADD jobs '*' task "process_order" order_id 1001
redis-cli XGROUP CREATE jobs workers '$' MKSTREAM

# consumer 1 reads (but doesn't ack yet — simulating a crash mid-processing)
redis-cli XREADGROUP GROUP workers consumer-1 COUNT 1 STREAMS jobs '>'

# simulate consumer-1 crashing before XACK — check pending entries
redis-cli XPENDING jobs workers

# consumer 2 claims the abandoned entry after an idle threshold
redis-cli XCLAIM jobs workers consumer-2 0 <entry-id-from-XPENDING>
redis-cli XACK jobs workers <entry-id>
```
Verify the message is never lost despite consumer-1's "crash" — this is the core
durability property Pub/Sub cannot offer at all.

## 6. Real-World Product Comparison

- Many teams use Redis Streams as a **lightweight job queue** or **event bus** for
  moderate-throughput internal workflows, deliberately choosing not to operate a full
  Kafka cluster for that use case — the operational simplicity of "it's already in our
  Redis instance" is a real, legitimate trade-off, not a compromise.
- **Twitter** (historically) and many others use Redis Pub/Sub purely for ephemeral
  real-time notifications (e.g., "someone started typing") where losing a message on
  disconnect is completely acceptable — the opposite end of the durability spectrum from
  what Streams (or Kafka) is for.

## 7. Common Production Pitfalls

- Using Pub/Sub for anything that must not be lost (e.g., order events) — there is no
  fallback if the subscriber briefly disconnects; the message is simply gone.
- Never `XACK`-ing successfully processed Stream entries — the PEL grows unbounded,
  eventually causing memory and operational issues.
- Scaling a Streams-based system past what a single Redis instance can handle, instead
  of recognizing that's the actual signal to migrate to Kafka.

## 8. Review Questions
1. What specifically happens to a Pub/Sub message if no subscriber is connected?
2. How does the Pending Entries List enable crash recovery in Streams?
3. What's the genuine scaling limitation of Streams compared to Kafka?
4. When is Pub/Sub's lack of durability actually the *correct* choice, not just a
   limitation?

## 9. Proficiency Checkpoint
If you can correctly decide "Pub/Sub, Streams, or Kafka" for a given durability and
scale requirement, you're at Level 2 on Redis messaging.

## Next
Day 5 covers Redis transactions (MULTI/EXEC/WATCH) and Lua scripting — the two ways
Redis gives you atomic multi-step operations.
