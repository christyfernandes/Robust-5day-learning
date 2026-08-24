# Day 19: PySpark — Cost Optimization: Spot Instances & Autoscaling

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Model the cost difference between a fixed-size cluster and an autoscaled cluster for
your actual batch job profile.

## 2. Core Concept (basics → advanced)

**Spot/preemptible instances** offer substantial cost savings (commonly 60-90% off
on-demand pricing) in exchange for the provider being able to reclaim them with
short notice — a genuine trade worth making for **fault-tolerant, restartable**
batch workloads (Spark's lineage-based recomputation, Week 1 Day 1, means losing an
executor mid-job is recoverable, not catastrophic), but a poor fit for
latency-sensitive or stateful workloads that can't tolerate sudden node loss.

**Autoscaling** (dynamic allocation, Week 2 Day 9, at the infrastructure level rather
than just the executor-count level) matches cluster size to actual demand over
time — a batch workload with bursty, uneven load (e.g., a nightly ETL run using
substantial resources for 2 hours, then idle for 22) benefits enormously from
autoscaling versus a fixed-size cluster provisioned for peak load and sitting mostly
idle otherwise.

```
Fixed cluster:     [=========== always-on capacity ===========]
                    (paid for 24/7, but only USED heavily for ~2 hrs/day)

Autoscaled:         [==peak==]                    [==peak==]
                    (scales UP for the 2-hour job, DOWN to near-zero after —
                     pay roughly proportional to actual usage)
```

## 3. How It Really Works (Internals)

The real cost-modeling exercise combines both levers: spot pricing reduces
**per-instance-hour cost**; autoscaling reduces **total instance-hours consumed** by
matching capacity to actual demand rather than provisioning for peak permanently.
Together, they can compound into very large total savings for the right workload
shape — but the "right workload shape" qualifier matters: a job with unpredictable,
constant load doesn't benefit from autoscaling the way a bursty, predictable batch
job does, and a job sensitive to executor loss (long-running stateful work without
good checkpointing) doesn't tolerate spot preemption gracefully.

## 4. Architecture & Design Pattern Spotlight

**Pattern: elastic capacity for bursty batch load — the same underlying "pay for
what you actually use, not peak capacity held permanently" idea as Flink's Reactive
Mode (Week 2, Day 13) and Kubernetes autoscaling generally.** This is a specific
instance of a much broader cloud-cost-optimization principle: workloads with
genuine burstiness are the ones where elastic infrastructure delivers real, not just
theoretical, savings.

## 5. Hands-On Lab

For your actual batch workload profile (e.g., your nightly PySpark job's typical
resource usage and runtime), build a simple cost model comparing:
- **Fixed cluster**: sized for peak load, running 24/7, at on-demand pricing.
- **Autoscaled cluster**: scaling to peak only during the job's actual runtime,
  scaling down otherwise, using spot pricing for a plausible fraction of capacity.

Calculate the total monthly cost for each scenario using realistic instance pricing
figures, and quantify the savings percentage — this is a concrete number worth
bringing into any infrastructure-cost conversation.

## 6. Real-World Product Comparison

- **Databricks' Job Clusters** (ephemeral, auto-terminating clusters spun up per
  job and torn down afterward) are built specifically around this exact
  cost-optimization principle — you only pay for the cluster's actual runtime, not
  a permanently-provisioned environment.
- **AWS EMR** and **GCP Dataproc** both support spot/preemptible instance pools
  specifically for Spark workloads, explicitly marketed around this fault-tolerant-
  recomputation property Spark's architecture provides.

## 7. Common Production Pitfalls

- Using spot instances for stateful or latency-sensitive workloads without
  accounting for preemption's real operational impact — not every Spark job
  tolerates node loss equally gracefully.
- Provisioning a fixed cluster sized for peak load "to be safe," without
  quantifying the actual idle-capacity cost being paid for the other 22 hours a day.
- Not accounting for autoscaling's own overhead (scale-up latency, the time a job
  waits for new capacity to become available) when estimating actual end-to-end job
  duration under an autoscaled configuration.

## 8. Review Questions
1. Why are spot instances a good fit for Spark batch workloads specifically?
2. What two separate levers (pricing model, capacity matching) does this cost model
   combine?
3. Why doesn't every workload benefit equally from autoscaling?
4. What real cost, beyond instance-hour pricing, does autoscaling introduce?

## 9. Proficiency Checkpoint
If you can build a real cost model for your own workload and correctly identify
whether it's a good candidate for spot/autoscaling, you're at Level 3.5.

## Next
Day 20 covers managed vs. self-hosted TCO comparison — the next layer of this same
cost-optimization thinking, applied to the build-vs-buy decision broadly.
