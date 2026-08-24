# Day 20: Kafka — Alternatives: Confluent Cloud vs. MSK vs. Redpanda vs. Pulsar

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Fill in the Kafka row of your product comparison matrix, weighted by your own
workload's actual priorities.

## 2. Core Concept (basics → advanced)

Four genuinely different points on the managed-vs-self-hosted-vs-rewrite spectrum:
- **Confluent Cloud**: fully managed Kafka (from Kafka's primary commercial
  steward), including Schema Registry (Week 1, Day 6) and ksqlDB (Week 2, Day 8) as
  integrated managed services — highest convenience, highest cost premium.
- **Amazon MSK**: AWS's managed Kafka offering — less integrated tooling than
  Confluent Cloud, but tighter AWS-ecosystem integration and typically lower
  premium over raw infrastructure cost.
- **Redpanda**: a from-scratch, Kafka-API-compatible reimplementation in C++
  (not JVM-based) — architecturally closer to the DragonflyDB-vs-Redis relationship
  (Week 2, Day 13): API-compatible, but a genuinely different, often more
  resource-efficient implementation underneath.
- **Apache Pulsar**: not API-compatible with Kafka at all — a fundamentally
  different architecture (separates the message broker layer from the storage
  layer, using Apache BookKeeper for storage) that solves similar problems with
  different trade-offs.

## 3. How It Really Works (Internals)

The Confluent Cloud/MSK comparison is a managed-vs-managed decision (both fully
operated by the vendor, differing mainly in tooling depth and ecosystem
integration) — the Redpanda comparison is architecturally analogous to Week 2 Day
13's DragonflyDB-vs-Redis question (same wire protocol, different, often more
efficient implementation underneath, a genuine "drop-in replacement" evaluation).
Pulsar is a categorically different comparison — not a drop-in replacement at all,
but a from-scratch architectural alternative, meaning adopting it isn't a simple
swap but a genuine rewrite of anything depending on Kafka-specific behavior or
tooling.

## 4. Architecture & Design Pattern Spotlight

**Pattern: managed vs. self-hosted vs. architecturally-different rewrites — three
genuinely different categories of alternative, not one undifferentiated
"competitor" list.** Recognizing which category a given alternative falls into
(pure hosting change, API-compatible reimplementation, or architectural rewrite)
determines how much migration effort and risk it actually represents — a critical
distinction when actually evaluating options, not just listing them.

## 5. Hands-On Lab

Fill in your `PRODUCT_COMPARISON_MATRIX.md`'s Kafka row, weighting each alternative
against your own workload's actual priorities (cost sensitivity, operational
maturity, tooling needs, migration risk tolerance) rather than a generic,
context-free comparison. For each alternative, note explicitly which category it
falls into (managed hosting change / API-compatible rewrite / architectural
rewrite) and what that implies for actual migration effort.

## 6. Real-World Product Comparison

- **Redpanda's** C++ implementation claims meaningfully lower per-node resource
  requirements than JVM-based Kafka for comparable throughput — a claim worth
  validating against your own workload via benchmarking, the same empirical
  discipline from Week 2 Day 13's DragonflyDB lab, rather than accepting vendor
  marketing at face value.
- **Apache Pulsar** is used by companies (like some at very large scale) that
  specifically value its storage/broker separation for particular operational
  flexibility reasons — a genuinely different architecture serving genuinely
  different priorities than Kafka's design.

## 7. Common Production Pitfalls

- Treating all four alternatives as equivalent "Kafka competitors" without
  distinguishing hosting changes from API-compatible rewrites from architectural
  rewrites — very different migration efforts and risks.
- Choosing based on vendor marketing claims (e.g., Redpanda's efficiency claims)
  without empirical validation against your own actual workload.
- Underweighting ecosystem/tooling maturity (Schema Registry integration, Kafka
  Connect connector availability) when evaluating an architecturally-different
  alternative like Pulsar.

## 8. Review Questions
1. What are the three genuinely different categories these four alternatives fall
   into?
2. Why is Redpanda's comparison structurally similar to DragonflyDB's vs. Redis?
3. Why is Pulsar not a "drop-in" alternative the way Redpanda is?
4. What would make Confluent Cloud the right choice over MSK for a specific team?

## 9. Proficiency Checkpoint
If you've filled in a real, workload-weighted comparison matrix distinguishing the
three alternative categories, you're at Level 3.5.

## Next
Day 21 is this week's integrated lab and review, producing your final decision
documents.
