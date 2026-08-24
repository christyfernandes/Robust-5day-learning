# Day 18: PySpark — Security & Multi-Tenancy: Fair Scheduling

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Configure a fair-scheduler pool for two competing job classes, and explain how it
prevents one workload from starving another.

## 2. Core Concept (basics → advanced)

On shared infrastructure serving multiple teams/job classes (exactly your own shared
single-node production reality, Week 2 Day 9), the default **FIFO scheduler** runs
jobs strictly in submission order — a long-running job submitted first can starve a
short, urgent job submitted afterward, even if the short job needs only a small
fraction of total cluster resources. The **FAIR scheduler** instead allocates
resources across configured **pools**, giving each pool a fair share of available
resources concurrently, rather than strict submission-order precedence — closely
analogous to Kubernetes' namespace-based resource quotas (which achieve a similar
per-tenant isolation goal through a different mechanism).

```
FIFO:  [Long job A submitted first] ████████████████████ (runs to completion)
                                     [Short job B waits the ENTIRE time, even
                                      though it needs minimal resources]

FAIR (2 pools):  [Job A's pool] ████░░░░████░░░░████░░░░  (gets its fair share)
                 [Job B's pool] ░░░░████░░░░████░░░░████  (runs CONCURRENTLY,
                                                            doesn't wait for A)
```

## 3. How It Really Works (Internals)

Pool configuration lets you assign **minimum shares** (guaranteed resources a pool
can always claim) and **weights** (relative priority when there's contention beyond
minimums) per job class — this is precisely the resource-governance concept from
Week 3 Day 16's ClickHouse quota lesson, applied here to whole-job scheduling rather
than per-query memory limits: both are answers to "how do you prevent one tenant's
workload from starving another's, on genuinely shared infrastructure," the exact
same underlying multi-tenancy problem recurring at a different layer.

## 4. Architecture & Design Pattern Spotlight

**Pattern: fair-share scheduling — the scheduling-layer instance of the bulkhead/
quota pattern studied at other layers this month (ClickHouse per-user quotas, Day 16;
resilience-pattern bulkheads, Week 2 Day 13).** Recognizing that "isolate one
tenant's resource consumption from affecting another's" recurs at the query level
(ClickHouse), the connection-pool level (bulkhead), and now the job-scheduling level
(Spark fair scheduler) reinforces that this is one general principle applied
throughout distributed systems, not three unrelated features.

## 5. Hands-On Lab

```xml
<!-- fairscheduler.xml -->
<pool name="urgent_jobs">
  <minShare>4</minShare>
  <weight>2</weight>
</pool>
<pool name="background_jobs">
  <minShare>1</minShare>
  <weight>1</weight>
</pool>
```
```python
spark.conf.set("spark.scheduler.mode", "FAIR")
spark.sparkContext.setLocalProperty("spark.scheduler.pool", "background_jobs")
# submit a long-running job tagged to background_jobs

spark.sparkContext.setLocalProperty("spark.scheduler.pool", "urgent_jobs")
# submit a short job tagged to urgent_jobs WHILE the background job is still running
```
Confirm (via the Spark UI's Jobs/Stages view, which shows pool assignment) that the
urgent job starts making progress concurrently, rather than waiting for the
background job to finish first.

## 6. Real-World Product Comparison

- **YARN's** own fair scheduler and capacity scheduler solve this identical
  multi-tenancy problem at the cluster-manager level (rather than within a single
  Spark application) — relevant when multiple *separate* Spark applications (not
  just jobs within one application) share a YARN cluster.
- **Kubernetes namespace resource quotas** achieve an analogous isolation goal for
  Spark-on-K8s deployments (Week 1, Day 3) — a different specific mechanism, same
  underlying multi-tenancy fairness goal.

## 7. Common Production Pitfalls

- Leaving the default FIFO scheduler on infrastructure serving genuinely competing
  job classes, allowing accidental starvation without anyone intending it.
- Setting pool `minShare` values that sum to more than actual available cluster
  capacity, making the "guarantee" meaningless under real contention.
- Not distinguishing this Spark-application-internal scheduling from
  cluster-manager-level scheduling (YARN/K8s) — the two operate at different
  layers and often need to be configured together for full effect.

## 8. Review Questions
1. What specific problem does FIFO scheduling create for a short, urgent job
   submitted after a long-running one?
2. How is fair-share pool configuration analogous to Day 16's ClickHouse per-user
   quotas?
3. Why might pool `minShare` values summing beyond cluster capacity undermine the
   fairness guarantee?
4. How does this differ from YARN/Kubernetes-level scheduling, and when would you
   need both?

## 9. Proficiency Checkpoint
If you can configure fair-share pools that prevent real starvation between
competing job classes, you're at Level 3.5.

## Next
Day 19 covers cost optimization — spot/preemptible instances and autoscaling — for
exactly this kind of shared, multi-tenant infrastructure.
