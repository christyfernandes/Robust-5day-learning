# Day 19: Flink — Deployment Modes: Session vs. Application vs. Per-Job

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Compare resource isolation between session mode and per-job mode for a realistic
mixed job workload.

## 2. Core Concept (basics → advanced)

Three ways to deploy Flink jobs onto a cluster, each with different isolation
trade-offs:
- **Session mode**: one long-running Flink cluster (JobManager + TaskManagers)
  accepts and runs *multiple* jobs, submitted independently over time — jobs share
  the same cluster's resources and, critically, the same JobManager process.
- **Per-job mode** (being phased out in favor of Application mode in newer
  versions, but conceptually foundational): a dedicated cluster is spun up *for one
  specific job*, and torn down when it completes — full resource isolation between
  jobs, at the cost of cluster startup overhead per job.
- **Application mode**: similar isolation goal to per-job mode, but runs the job's
  `main()` method on the JobManager itself (rather than the client), reducing
  client-side resource requirements for job submission — the modern recommended
  default for isolated, single-application deployments, especially on Kubernetes.

```
Session mode:              Per-job / Application mode:

[Shared JobManager]        [Job A: dedicated JobManager + TaskManagers]
  Job A, Job B, Job C        (fully isolated, own cluster lifecycle)
  ALL share resources       [Job B: separate dedicated JobManager + TaskManagers]
  ONE misbehaving job         (fully isolated, own cluster lifecycle)
  can affect the others
  (and a JobManager crash
   takes down ALL jobs)
```

## 3. How It Really Works (Internals)

Session mode's core risk is precisely the shared-JobManager exposure studied in
today's Flink HA lesson — if the shared JobManager becomes unstable (perhaps due to
one misbehaving job's resource demands, or hits the exact class of issue you've
investigated with your own JobManager instability this month), **every** job running
in that session is affected, not just the problematic one. Per-job/Application
mode's isolation directly prevents this cross-job blast radius, at the cost of
losing the resource-sharing efficiency a session cluster provides for many small,
short-lived jobs (spinning up a full dedicated cluster per job has real startup
latency and resource overhead that doesn't make sense for very lightweight or
frequent jobs).

## 4. Architecture & Design Pattern Spotlight

**Pattern: deployment isolation trade-offs — the exact same blast-radius reasoning
studied all week (bulkheads, Week 2 Day 13; cell-based architecture, Day 16;
per-user resource quotas, Day 16's ClickHouse lesson), now applied to Flink's own
deployment topology.** Session mode optimizes for resource efficiency across many
jobs; per-job/Application mode optimizes for fault isolation between them — a
direct, concrete instance of the efficiency-vs-isolation trade-off recurring
throughout this curriculum.

## 5. Hands-On Lab

Compare, for your own actual mix of Flink jobs (if you run multiple), which
deployment mode better fits each: a frequently-changing, lightweight job might favor
session mode's lower per-job overhead; your production job with real
JobManager-instability history is a strong candidate for per-job/Application mode's
isolation, specifically so that instability in *that* job's JobManager doesn't risk
affecting other unrelated jobs sharing the same session cluster. Write down which
mode you'd recommend for your own most critical production job, and why, using
today's isolation-vs-efficiency framing explicitly.

## 6. Real-World Product Comparison

- The **Flink Kubernetes Operator** defaults to Application mode for new
  deployments specifically because Kubernetes-native, per-job resource isolation
  aligns naturally with Kubernetes' own pod-based resource model — a deliberate
  ecosystem convergence, not a coincidence.
- Companies running many small, frequently-submitted Flink jobs (e.g., ad hoc
  analytics jobs) often still use session clusters for exactly the resource-
  efficiency reason described above — isolation isn't free, and the right choice
  genuinely depends on the actual job mix.

## 7. Common Production Pitfalls

- Running a critical, historically-unstable production job in a shared session
  cluster alongside other jobs, unnecessarily exposing unrelated jobs to that job's
  instability.
- Using per-job/Application mode for very lightweight, frequently-submitted jobs
  without accounting for the cumulative cluster-startup overhead this incurs at
  scale.
- Not revisiting deployment-mode choice as a job's criticality or resource profile
  changes over time — an appropriate choice at initial deployment can become wrong
  as usage patterns evolve.

## 8. Review Questions
1. What's the core isolation risk of session mode that per-job/Application mode
   eliminates?
2. Why does per-job/Application mode have real overhead that session mode avoids?
3. What's the Kubernetes-specific reason Application mode is now the recommended
   default for new deployments?
4. How would you decide which mode fits your own most critical production job?

## 9. Proficiency Checkpoint
If you can correctly justify a deployment-mode choice for a real job mix using the
isolation-vs-efficiency trade-off, you're at Level 3.5.

## Next
Day 20 covers Flink's managed alternatives — AWS Kinesis Data Analytics and Google
Cloud Dataflow — and Beam's shared lineage with Flink's own dataflow model.
