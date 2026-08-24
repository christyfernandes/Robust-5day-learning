# Day 17: Kafka — Monitoring: JMX Metrics & Consumer-Lag Alerting

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Set up a consumer-lag alert threshold and simulate a lag spike to validate it fires
correctly.

## 2. Core Concept (basics → advanced)

**Consumer lag** (the gap between the latest offset in a partition and a consumer
group's committed offset) is the single most important Kafka health signal — it
directly measures "how far behind real-time is this consumer," which is usually the
metric that actually matters to downstream stakeholders, more so than broker-level
CPU or disk metrics in isolation. Kafka exposes a rich set of **JMX metrics**
(broker-level: request rates, ISR shrink/expand events; consumer-level: lag,
fetch rate) that feed into monitoring systems (Prometheus/Grafana being the most
common open-source combination).

```
Consumer group lag = latest_offset_in_partition - consumer_group_committed_offset

Lag = 0:        consumer is fully caught up (real-time)
Lag = 10,000:   consumer is 10,000 messages behind — translate this to TIME
                 (messages/sec throughput) to know if that's 1 second or 1 hour
                 of actual delay — the raw message count alone isn't meaningful
                 without that context
```

## 3. How It Really Works (Internals)

Raw lag (message count) needs to be interpreted **relative to throughput** to be
actionable — a lag of 10,000 messages means something very different for a topic
processing 100 messages/sec (100 seconds behind) versus one processing 100,000
messages/sec (0.1 seconds behind, essentially noise). This is exactly why mature
lag-alerting setups convert lag into **estimated time-behind-realtime**, not raw
message count, before setting alert thresholds — an alert threshold in raw message
count either fires too often for high-throughput topics or misses real problems on
low-throughput ones.

**Cruise Control** (an open-source Kafka operations tool) goes further, using
collected metrics to make automated rebalancing decisions (moving partitions between
brokers to even out load) — an example of monitoring data feeding directly into
automated operational action, rather than only human-facing dashboards/alerts.

## 4. Architecture & Design Pattern Spotlight

**Pattern: lag as the primary health signal — the same "measure the thing users
actually care about, not just infrastructure-level proxies" principle as Day 16's
SLI/SLO framing.** Lag is, in effect, an SLI for a Kafka-based pipeline's real-time-
ness — the same measurement discipline (define the metric that matters, set a
threshold, alert on it meaningfully) applies directly.

## 5. Hands-On Lab

```bash
# baseline: check current lag for a consumer group
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group your-group

# simulate a lag spike: pause the consumer, keep producing
# (stop your consumer process, let a producer keep running for a minute or two)

kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group your-group   # re-check — LAG column should have grown
```
Convert the observed lag (message count) into estimated seconds-behind-realtime
using your known producer throughput, and set a concrete alert threshold in those
terms (e.g., "alert if any partition is more than 60 seconds behind") rather than an
arbitrary raw message count — write down why this threshold, specifically, makes
sense for this topic's actual throughput.

## 6. Real-World Product Comparison

- **Confluent Control Center** and open-source **Burrow** (a dedicated Kafka
  consumer-lag-monitoring tool) both exist specifically because naive raw-lag
  alerting is insufficient — both convert lag into more meaningful,
  throughput-normalized health signals automatically.
- This is directly the monitoring layer that would have surfaced your real Flink
  JobManager-instability incident (Week 2, Day 10) earlier — a `FINISHED` job
  produces exactly the lag-growing-with-no-consumption signature this lesson's lab
  simulates.

## 7. Common Production Pitfalls

- Alerting on raw lag count without normalizing by throughput, producing either
  alert fatigue (false alarms on high-throughput topics) or missed incidents
  (undetected problems on low-throughput topics).
- Monitoring only broker-level metrics (CPU, disk) without consumer-lag monitoring
  — broker health and actual pipeline real-time-ness are related but distinct signals.
- Not testing alert thresholds against a simulated scenario before relying on them —
  an untested alert threshold is an assumption, not a validated safety mechanism.

## 8. Review Questions
1. Why is raw lag count alone insufficient for a meaningful alert threshold?
2. What does Cruise Control do with collected metrics that goes beyond
   human-facing dashboards?
3. How is consumer lag conceptually similar to an SLI from Day 16's framework?
4. How would this monitoring layer have surfaced your real Flink incident earlier?

## 9. Proficiency Checkpoint
If you can define and validate a throughput-normalized lag alert threshold, you're at
Level 3.5.

## Next
Day 18 covers Kafka security — SASL/SSL and ACLs — the access-control layer for a
cluster you're now monitoring effectively.
