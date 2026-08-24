# Day 17: Flink — Monitoring: Web UI Checkpoint & Backpressure Metrics

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Identify checkpoint duration and backpressure ratio for a running job via Flink's
metrics reporter — directly building your ongoing JobManager-debugging practice into
a proactive monitoring habit.

## 2. Core Concept (basics → advanced)

The Flink Web UI (and its underlying metrics, exportable to Prometheus/Grafana via a
metrics reporter) exposes exactly the signals this month's Flink lessons have used
for diagnosis, now as continuously-monitored production metrics rather than one-off
investigation tools:

- **Checkpoint duration and success rate** (Week 1, Day 6; Week 3, Day 16): a rising
  trend or a drop in success rate is an early warning of exactly the barrier-
  alignment/backpressure problems studied earlier, catchable *before* it becomes a
  full incident.
- **Backpressure ratio** (Week 2, Day 11): the percentage of time an operator spends
  blocked waiting for downstream capacity — a direct, quantified version of the
  Web UI's "High/Low" backpressure indicator from that lesson's lab.
- **Job state and uptime**: directly relevant to Week 2 Day 10's bounded-source
  incident — a job unexpectedly transitioning to `FINISHED` (or restarting
  frequently) is visible here as a state-transition metric, not just something you'd
  notice by chance when checking the UI manually.

## 3. How It Really Works (Internals)

The genuine operational value here is converting *manual, reactive* investigation
(what you did in Week 1-2's labs, checking the Web UI after noticing a problem) into
*automated, proactive* monitoring — the same underlying metrics, wired into
Prometheus/Grafana with alert thresholds, catch a developing checkpoint-duration
trend or a job's unexpected state transition **before** consumer lag has already
grown large enough for someone to notice downstream. This is precisely the gap
between "I know how to diagnose this class of incident" (established earlier this
month) and "I'd catch this before it became an incident" (today's actual production
maturity goal).

## 4. Architecture & Design Pattern Spotlight

**Pattern: directly relevant to your JobManager-instability debugging — turning a
reactive diagnostic skill into a proactive monitoring practice.** This mirrors the
same shift from Day 17's Kafka lesson (lag as a monitored, alerted signal, not just
something you check when a problem is already suspected) — across every system this
week, the theme is converting earlier weeks' diagnostic knowledge into standing,
automated observability.

## 5. Hands-On Lab

```yaml
# flink-conf.yaml
metrics.reporters: prom
metrics.reporter.prom.factory.class: org.apache.flink.metrics.prometheus.PrometheusReporterFactory
metrics.reporter.prom.port: 9250
```
With this configured, run a job (ideally reproducing Week 2 Day 11's backpressure
scenario, or Week 2 Day 10's bounded-source scenario) and query the exposed
Prometheus metrics endpoint directly (`curl localhost:9250/metrics` or via a
Grafana dashboard if available) for `flink_jobmanager_job_lastCheckpointDuration`
and the relevant backpressure/task metrics. Define one concrete alert threshold for
each (e.g., "alert if checkpoint duration exceeds 2x its typical value" or "alert if
a job's state changes to FINISHED unexpectedly for a job tagged as long-running") —
directly informed by your real incident history.

## 6. Real-World Product Comparison

- **Ververica** (the company behind much of Flink's commercial support) and other
  managed Flink platforms build dashboards specifically around these exact metrics —
  validating that checkpoint duration and backpressure ratio are considered the
  standard, essential health signals across the Flink operator community, not a
  niche concern.
- This is directly the monitoring setup that would have caught your real
  JobManager-instability incident earlier — worth prioritizing as an actual
  follow-up action from this curriculum, not just a learning exercise.

## 7. Common Production Pitfalls

- Only checking the Flink Web UI reactively (when something already seems wrong)
  rather than wiring these metrics into standing dashboards/alerts.
- Alerting on absolute checkpoint-duration thresholds without accounting for a
  given job's normal baseline — a job with naturally larger state may have a higher
  "normal" checkpoint duration than another; relative/trend-based alerting is often
  more robust than a single absolute threshold across different jobs.
- Not correlating job-state metrics with consumer-lag metrics (Day 17's Kafka
  lesson) in the same investigation — they're two views of the same underlying
  problem class and are more diagnostic together than either alone.

## 8. Review Questions
1. What's the practical difference between reactive Web-UI checking and proactive
   metrics-based monitoring?
2. Why would monitoring job-state transitions specifically have helped your real
   incident?
3. Why might a relative/trend-based checkpoint-duration alert be more robust than an
   absolute threshold?
4. How do Flink job-state metrics and Kafka consumer-lag metrics complement each
   other in an investigation?

## 9. Proficiency Checkpoint
If you've set up real, working metrics export and defined concrete, incident-
informed alert thresholds, you're at Level 3.5+ — a genuine operational maturity
step beyond this month's earlier reactive diagnosis.

## Next
Day 18 covers Flink High Availability — JobManager HA and failover — the next layer
of production robustness beyond monitoring alone.
