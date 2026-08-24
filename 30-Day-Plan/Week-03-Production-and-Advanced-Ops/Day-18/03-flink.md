# Day 18: Flink — High Availability: JobManager HA & Failover

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Configure JobManager HA and force a failover, confirming a standby JobManager takes
over without losing job progress.

## 2. Core Concept (basics → advanced)

The **JobManager** is the coordination brain of a Flink cluster (scheduling tasks,
triggering checkpoints, Week 1 Day 6) — if it fails with no HA configured, every
running job fails along with it, even if every TaskManager is perfectly healthy.
**JobManager HA** runs multiple JobManager instances — one **active leader**, one or
more **standbys** — so a leader failure triggers automatic failover to a standby,
which resumes coordinating already-running jobs from their last completed
checkpoint, rather than requiring a full manual restart.

```
Normal operation:            JobManager failure, NO HA:           JobManager failure, WITH HA:

JobManager (active) ──┐      JobManager DIES                      JobManager (active) DIES
  coordinates jobs     │      │                                    │
                        │      ▼                                    ▼
TaskManagers ───────────┘   ALL JOBS FAIL                    Standby JobManager becomes
  (execute tasks)          (even though TaskManagers          leader, RESUMES coordinating
                            are still healthy!)                jobs from last checkpoint
```

## 3. How It Really Works (Internals)

Leader election among JobManager instances requires a coordination service — either
**ZooKeeper** (the traditional choice) or, in Kubernetes deployments, the **Kubernetes
HA services** (using Kubernetes' own leader-election primitives via ConfigMaps,
avoiding a separate ZooKeeper dependency) — this is architecturally the same
consensus problem studied throughout this month (Week 1, Day 4's Raft lesson): a
quorum of coordination-service participants must agree on which JobManager instance
is currently the leader, and detect its failure to trigger the standby promotion.

Critically, HA doesn't mean jobs never notice a leader failure at all — there's a
real, if typically brief, gap while failover completes, during which job coordination
(new checkpoint triggers, task rescheduling decisions) pauses; TaskManagers continue
executing already-scheduled work during this gap, but the newly-active JobManager
must reconstruct its view of running jobs' state (from persisted checkpoint metadata)
before resuming full coordination.

## 4. Architecture & Design Pattern Spotlight

**Pattern: standby-based failover, coordinated via the same consensus mechanisms
(ZooKeeper/Kubernetes leader election) studied throughout this month.** This is
directly analogous to Redis Sentinel's primary/replica failover (Week 2, Day 9) and
Kafka's KRaft controller failover (Week 1, Day 5) — a small set of coordination
participants, a leader, standbys ready to take over, and a quorum-based mechanism
to detect failure and promote a replacement without split-brain (two JobManagers
both believing they're the leader simultaneously).

## 5. Hands-On Lab

```yaml
# flink-conf.yaml (ZooKeeper-based HA example)
high-availability: zookeeper
high-availability.storageDir: hdfs:///flink/ha/
high-availability.zookeeper.quorum: localhost:2181
high-availability.cluster-id: /cluster1
```
Start a cluster with 2 JobManager instances (one becomes leader), submit a
long-running stateful job, then kill the active JobManager process. Confirm the
standby JobManager takes over (check its logs for leader-election messages) and that
the running job continues correctly — verify state is intact by checking the job's
output for continuity, not a reset.

## 6. Real-World Product Comparison

- **Kubernetes HA services** are increasingly preferred over ZooKeeper-based HA for
  new Flink-on-Kubernetes deployments specifically to avoid an additional
  ZooKeeper dependency — the same "absorb an external coordination dependency into
  the platform you're already running on" motivation behind Kafka's KRaft
  (Week 1, Day 5) and ClickHouse's Keeper (Week 1, Day 5).
- **Ververica Platform** and other managed Flink offerings configure JobManager HA
  as a standard, expected production setting — not an advanced or optional feature
  for any deployment expected to run continuously.

## 7. Common Production Pitfalls

- Running Flink in production without JobManager HA configured at all — a single
  JobManager failure becomes a full outage for every running job, an unnecessary
  single point of failure.
- Not testing failover before relying on it — confirming HA configuration is
  syntactically valid is different from confirming a real failover actually
  preserves job state correctly.
- Under-provisioning the ZooKeeper (or Kubernetes coordination) quorum backing HA —
  the same odd-node-count, quorum-sizing reasoning from Week 1 Day 4 applies directly
  to whatever coordination service backs your JobManager HA setup.

## 8. Review Questions
1. What specifically fails without JobManager HA, even if TaskManagers are healthy?
2. Why does failover require a coordination service, rather than JobManagers
   independently deciding who's the leader?
3. What happens to already-running jobs during the failover gap?
4. Why are Kubernetes HA services increasingly preferred over ZooKeeper for new
   deployments?

## 9. Proficiency Checkpoint
If you can configure and successfully test JobManager HA failover, you're at Level
3.5 — a genuine production-hardening step for any Flink deployment.

## Next
Day 19 covers Flink deployment modes — session vs. application vs. per-job — and
Kubernetes Operator patterns for managing Flink at scale.
