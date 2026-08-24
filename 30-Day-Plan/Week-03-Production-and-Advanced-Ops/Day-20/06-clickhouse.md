# Day 20: ClickHouse — Cost Modeling: Self-Hosted vs. BigQuery TCO (Your Live POC)

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Build the actual cost-comparison framework — hardware/ops cost vs. projected
BigQuery scan cost — for your real workload. This is not a practice exercise; it's
the central deliverable of your live POC.

## 2. Core Concept (basics → advanced)

The two pricing models are structurally different, which is exactly why a naive
"just compare the invoices" comparison misleads:

- **BigQuery**: pay-per-byte-scanned (plus separate storage cost) — cost scales
  with *query volume and query pattern*, not with a fixed capacity you provision
  upfront. A workload with occasional, well-pruned queries can be very cheap; the
  same data volume with frequent, poorly-pruned dashboard queries (Week 1, Day 4's
  fan-out lesson, Week 2 Day 9) can be very expensive, invisibly, until the bill
  arrives.
- **Self-hosted ClickHouse**: pay for provisioned capacity (hardware/cloud
  instances, sized for peak load, Week 3 Day 15) regardless of how much you
  actually query it, *plus* the fully-loaded **operational labor** cost (Day 20's
  PySpark lesson made this same point for Spark) — cluster tuning, monitoring
  (Week 3, Day 17), security (Day 18), backup/DR (Day 19), and incident response,
  all real, ongoing costs even when not itemized on an infrastructure invoice.

```
BigQuery cost ≈ (bytes scanned per query × query frequency × price per TB scanned)
                 + storage cost
                 (scales with QUERY PATTERN — can spike invisibly from a
                  single change in dashboard query behavior, e.g. Week 2 Day 9's
                  fan-out bug multiplying effective bytes scanned)

Self-hosted cost ≈ (provisioned hardware cost, sized for PEAK load)
                    + operational labor (tuning + monitoring + incident response
                      + security + backup/DR — real cost, easy to under-count)
                    (scales with PROVISIONED CAPACITY, roughly flat regardless
                     of actual query volume within that capacity)
```

## 3. How It Really Works (Internals)

The single most consequential input to this model is your **actual query pattern**
— specifically, total bytes scanned per month under BigQuery's current pricing,
which you can pull directly from BigQuery's own query history/billing export
(not an estimate — real, measured data). This is where Week 1, Day 4's join-fan-out
investigation and Week 2, Day 9's ClickHouse fan-out lesson connect directly back
to cost: if any of your current BigQuery dashboard queries are scanning far more
bytes than their logical result actually requires (a fan-out-adjacent inefficiency,
an unpruned partition scan, a `SELECT *` where only a few columns are needed), your
*current* BigQuery bill is inflated by exactly that inefficiency — meaning part of
the "savings" a ClickHouse migration appears to offer might actually be achievable
by fixing the query pattern itself, independent of which engine runs it. A rigorous
cost model separates these two effects: (a) genuine engine/pricing-model
differences, and (b) query-pattern inefficiencies that could be fixed either way.

The self-hosted side's honesty check is the same one from today's PySpark lesson:
does your model include a realistic, fully-loaded estimate of the operational labor
this curriculum's Week 3 has made concrete (tuning, Day 15; monitoring, Day 17;
security, Day 18; backup/DR, Day 19) — not just hardware/cloud-instance cost?

## 4. Architecture & Design Pattern Spotlight

**Pattern: compute+storage-owned vs. pay-per-byte-scanned — the same TCO-modeling
discipline as today's PySpark lesson, applied to the actual decision your POC
exists to make.** The general method (normalize to a common unit, separate
genuine architectural cost differences from fixable inefficiencies, honestly
count operational labor) transfers directly — today's difference is that this
isn't a hypothetical exercise, it's the real number your stakeholders are waiting
for.

## 5. Hands-On Lab

Build the actual framework, using real numbers:
1. **BigQuery baseline**: pull actual monthly bytes-scanned and cost from your
   BigQuery billing history for the specific dashboards/queries in scope for
   migration. Separately flag any queries you already know (from Week 1-2's fan-out
   investigation) are scanning more than they logically need to — note what the
   *corrected* BigQuery cost would be if those were fixed, independent of any
   migration.
2. **ClickHouse projected cost**: your 3-node cluster's actual hardware/cloud cost
   (already known from your POC), plus a realistic monthly operational-labor
   estimate (hours/month × loaded hourly cost) for tuning, monitoring, security,
   and backup/DR specific to this cluster.
3. Compare total monthly cost under both models, **and** separately report the
   "corrected BigQuery" figure — this three-way comparison (current BigQuery,
   corrected BigQuery, self-hosted ClickHouse) is a materially more honest and
   more useful artifact for stakeholders than a simple two-way comparison.

## 6. Real-World Product Comparison

- This exact three-way framing (current cost, cost-if-optimized-in-place,
  cost-if-migrated) is standard practice in serious FinOps/cost-optimization
  engagements — separating "we're paying more than we need to for reasons
  unrelated to the platform" from "the platform itself is fundamentally more/less
  expensive for our pattern" is the single most valuable analytical move in this
  kind of comparison.
- **Snowflake** and other consumption-priced warehouses share BigQuery's
  pay-per-scan-adjacent cost dynamic (Snowflake's is compute-time-based rather
  than bytes-scanned, but shares the same "query pattern directly drives cost"
  property) — the same query-efficiency-first discipline applies to any
  consumption-priced comparison, not just BigQuery specifically.

## 7. Common Production Pitfalls

- Comparing current (possibly inefficient) BigQuery cost directly against
  projected ClickHouse cost, without separating out fixable query-pattern
  inefficiencies — this can make a migration look more beneficial than it
  genuinely is on architectural grounds alone.
- Omitting operational labor from the self-hosted side, the same PySpark-lesson
  pitfall, systematically underestimating self-hosted TCO.
- Presenting a single point-estimate cost comparison without sensitivity
  analysis — query volume and data volume both grow over time, and the "right"
  answer today may not hold in 18 months; a model that shows how the comparison
  changes with growth is more durable and more credible to stakeholders.

## 8. Review Questions
1. Why does BigQuery's cost scale with query pattern while ClickHouse's scales
   with provisioned capacity?
2. Why is separating "fixable query inefficiency" from "genuine architectural
   cost difference" the single most valuable analytical move here?
3. What specific costs does a self-hosted TCO estimate commonly, systematically
   under-count?
4. Why does a three-way comparison (current, corrected, migrated) serve
   stakeholders better than a simple two-way one?

## 9. Proficiency Checkpoint
If you've built this real, three-way cost model with actual numbers from your own
BigQuery billing history and ClickHouse cluster costs, you're at Level 4 — this is
the literal deliverable your POC exists to produce.

## Next
Day 21 is this week's integrated lab and review — you'll turn this cost model into
a formal, stakeholder-ready report and a one-page ADR.
