# Day 20: PySpark — Managed vs. Self-Hosted Cost: $/TB-Processed

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Build a $/TB-processed cost model for your own batch workload, comparing managed
(Databricks/EMR/Dataproc) against self-managed cluster costs.

## 2. Core Concept (basics → advanced)

Comparing managed and self-hosted Spark costs requires normalizing to a common unit
— **$/TB-processed** is a useful one, since it captures the actual work done rather
than just infrastructure spend, letting you compare fundamentally different pricing
models on equal footing:

- **Managed (Databricks/EMR/Dataproc)**: typically charges a premium on top of raw
  compute (a per-DBU or per-instance-hour markup) in exchange for managed cluster
  lifecycle, auto-tuning (Databricks' Photon, Week 1 Day 3), and reduced
  operational burden.
- **Self-managed**: raw infrastructure cost (compute + storage) plus the real,
  often under-counted cost of the **operational labor** to manage cluster
  provisioning, tuning (Week 3 Day 15's playbook), monitoring (Day 17), and
  incident response (your own real memory/JobManager incidents this month) —
  labor cost is real cost, even when it doesn't appear on a cloud invoice.

## 3. How It Really Works (Internals)

The genuinely easy mistake in this comparison is **only counting the visible
infrastructure line-item** and ignoring operational labor entirely — a self-managed
cluster that appears cheaper on raw compute cost can be more expensive in total
once you account for the engineering time spent on exactly the tuning, monitoring,
and incident-response work this curriculum has covered all month (which, notably, is
real work you and your team are already doing). The correct comparison estimates
**both** sides honestly: managed platform premium vs. self-managed infrastructure
savings *minus* the fully-loaded cost of the operational labor self-managing
actually requires.

## 4. Architecture & Design Pattern Spotlight

**Pattern: TCO modeling — normalizing genuinely different pricing structures to a
common unit, and counting operational labor as a real cost, not a free good.** This
is the same discipline Day 20's ClickHouse lesson applies to your actual, live
BigQuery-vs-self-hosted decision — worth internalizing the general method here
first, since it transfers directly.

## 5. Hands-On Lab

For your own actual PySpark batch workload, build a $/TB-processed comparison:
- Estimate your current (or a representative) job's data volume processed per run
  and total infrastructure cost (self-managed instance costs for that run's
  duration).
- Estimate the equivalent managed-platform cost (Databricks/EMR/Dataproc list
  pricing for comparable compute).
- Add a realistic estimate of operational labor hours per month spent on tuning/
  monitoring/incident response for this specific workload, at a reasonable loaded
  hourly cost, and add it to the self-managed side.

Compare the two totals — is self-managed still cheaper once labor is honestly
counted? By how much?

## 6. Real-World Product Comparison

- **Databricks, EMR, and Dataproc** each price their management premium
  differently, and the "right" choice varies by workload predictability, team
  size, and existing operational maturity — there's no universal answer, only a
  answer specific to your actual numbers.
- Many teams underestimate self-managed operational cost specifically because
  labor doesn't show up as a discrete line item the way cloud infrastructure
  billing does — a genuine, common blind spot worth correcting for explicitly.

## 7. Common Production Pitfalls

- Comparing only raw infrastructure cost, ignoring operational labor entirely —
  systematically biasing the comparison toward self-managed.
- Using list pricing for managed platforms without accounting for realistic
  discounts/committed-use pricing that often apply at real usage volumes.
- Building the cost model once and never revisiting it as workload volume or team
  operational maturity changes over time.

## 8. Review Questions
1. Why is $/TB-processed a more useful comparison unit than raw monthly spend?
2. What cost do naive self-managed-vs-managed comparisons commonly omit?
3. Why might team operational maturity change which option is actually cheaper?
4. What would make your own honest answer favor managed vs. self-managed?

## 9. Proficiency Checkpoint
If you've built a real, honestly-labor-inclusive cost model for your own workload,
you're at Level 3.5 — directly transferable to today's ClickHouse-vs-BigQuery
exercise.

## Next
Day 21 is this week's integrated lab and review — producing your final incident
postmortems and cost/architecture decision documents.
