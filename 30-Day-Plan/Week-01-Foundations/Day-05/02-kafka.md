# Day 5: Kafka — KRaft Mode

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain why Kafka replaced ZooKeeper with KRaft, and what the controller quorum actually
does differently now.

## 2. Core Concept (basics → advanced)

For most of its history, Kafka relied on **ZooKeeper** as an external coordination
service — storing cluster metadata (broker list, topic configs, partition-leader
assignments, ACLs) and handling controller election via ZooKeeper's own consensus
mechanism. This worked, but meant operating *two* distributed systems (Kafka brokers +
a ZooKeeper ensemble) with their own separate failure modes, scaling limits, and
operational playbooks.

**KRaft** (Kafka Raft) removes that dependency entirely: cluster metadata is now stored
as a Kafka-native **event log** (conceptually, metadata changes are just another
partition, replicated via an actual Raft implementation running among a small set of
dedicated **controller** brokers), and controller election happens via that same Raft
protocol rather than ZooKeeper's Zab protocol.

```
ZooKeeper era:                          KRaft era:

Kafka Brokers ──▶ ZooKeeper Ensemble    Kafka Brokers ──▶ Controller Quorum
                  (separate system,                        (a subset of Kafka
                   own Zab consensus,                        brokers, running
                   own ops burden)                           Raft, storing
                                                              metadata as a
                                                              Kafka-native log)
```

## 3. How It Really Works (Internals)

A small set of brokers are configured with the `controller` role (often 3 or 5, for the
same odd-quorum reasoning from Day 4's Raft lesson). These controllers maintain the
**metadata log** — every cluster change (new topic, partition reassignment, broker
join/leave) is appended as an event to this log, replicated via Raft to the controller
quorum, and then propagated to all brokers, which apply it to their local in-memory
metadata cache. This means broker startup no longer requires a separate ZooKeeper
handshake — a broker simply catches up on the metadata log like a consumer catching up
on any other topic, which meaningfully simplifies both operations and, notably, cluster
startup/recovery time at scale (this was one of KRaft's original motivating benefits —
faster controller failover and metadata propagation than ZooKeeper's model allowed at
very large partition counts).

## 4. Architecture & Design Pattern Spotlight

**Pattern: consensus-based metadata management, self-hosted rather than externalized.**
KRaft is a direct, concrete instance of Day 4's Raft lesson — Kafka literally uses the
same algorithm you traced on paper, applied to its own cluster metadata. It's also a
recognizable architectural trend: absorbing a previously-external coordination
dependency into the system itself (the same motivation behind ClickHouse building its
own Keeper instead of depending on ZooKeeper, Day 5's ClickHouse lesson).

## 5. Hands-On Lab

```bash
# generate a cluster UUID and format storage for a single-node KRaft broker+controller
KAFKA_CLUSTER_ID="$(kafka-storage.sh random-uuid)"
kafka-storage.sh format -t "$KAFKA_CLUSTER_ID" -c config/kraft/server.properties

kafka-server-start.sh config/kraft/server.properties
```
Inspect the metadata log directly:
```bash
kafka-metadata-shell.sh --snapshot /tmp/kraft-combined-logs/__cluster_metadata-0/00000000000000000000.log
```
Browse the tree it prints — you're looking directly at the Raft-replicated metadata
that used to live in ZooKeeper. Create a topic, then re-run the shell and find the new
topic's entry in the metadata log.

## 6. Real-World Product Comparison

- **Confluent** (the company built around Kafka) drove much of KRaft's development
  specifically because very large ZooKeeper-backed clusters (hundreds of thousands of
  partitions) hit real operational and scaling limits in controller failover time —
  KRaft was built to remove that ceiling.
- This is Kafka's own architecture evolution, ZK-era vs. KRaft-era — a useful case study
  in what it actually costs (in engineering effort and migration risk) to replace a
  foundational dependency in a system already running in production everywhere.

## 7. Common Production Pitfalls

- Assuming KRaft is a drop-in operational replacement with identical tooling — several
  ZooKeeper-era admin tools and metrics have KRaft-specific equivalents that aren't
  always 1:1.
- Under-provisioning the controller quorum (too few dedicated controller nodes, or
  co-locating controller role with very high broker load) — the controller quorum being
  slow directly slows down every metadata operation cluster-wide.
- Migrating an existing large ZooKeeper-based cluster without thoroughly testing the
  migration path in a non-production environment first — this is a foundational
  dependency change, not a routine upgrade.

## 8. Review Questions
1. What specific problem did KRaft solve that ZooKeeper-based Kafka had?
2. What role does the controller quorum play, concretely, in KRaft mode?
3. Why does KRaft's approach to metadata replication mirror Day 4's Raft lesson so
   directly?
4. Why does ClickHouse Keeper exist for a conceptually similar reason?

## 9. Proficiency Checkpoint
If you can explain KRaft's controller quorum as "Raft, applied to Kafka's own cluster
metadata" without hand-waving, you're at Level 2 moving into Level 3.

## Next
Day 6 covers Kafka's Schema Registry — contract-first schema evolution, the governance
layer sitting on top of the cluster you've now studied end to end.
