# Day 16: Architecture — Reliability Engineering: SLIs, SLOs & Error Budgets

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Define one concrete SLI/SLO pair for a real component of your own platform, and
explain how an error budget turns that target into an actionable operating policy.

## 2. Core Concept (basics → advanced)

Three related concepts, precisely defined (often used loosely, but worth being exact
about):
- **SLI (Service Level Indicator)**: a *measured* quantity describing some aspect of
  service behavior — e.g., "the proportion of ClickHouse queries completing in under
  2 seconds," or "Kafka consumer-group lag in seconds."
- **SLO (Service Level Objective)**: a *target* value for an SLI — e.g., "99% of
  queries complete in under 2 seconds, measured over a rolling 30-day window."
- **Error budget**: the *allowed* amount of SLO violation — if your SLO is 99%, your
  error budget is the remaining 1%, a concrete, spendable allowance for the
  acceptable rate of "bad" events (slow queries, failed requests) before you're
  considered out of compliance with your own target.

```
SLI: "% of ClickHouse dashboard queries under 2s" — measured continuously

SLO: 99% of queries under 2s, over a rolling 30-day window

Error budget: 1% of queries in that window are ALLOWED to be slow —
              this is a real, trackable, SPENDABLE quantity, not just
              an aspiration — once it's exhausted, that's a signal to
              STOP shipping risky changes and focus on reliability instead
```

## 3. How It Really Works (Internals)

The genuinely useful part of this framework isn't the measurement — it's the
**operating policy** an error budget enables: while budget remains, teams can
reasonably take on some risk (ship new features, make infrastructure changes) because
some SLO violation is explicitly, deliberately tolerated. Once the budget is
exhausted, that's a concrete, pre-agreed signal to pause risky changes and prioritize
reliability work instead — turning "should we be more careful right now" from a
subjective judgment call into an objective, budget-driven decision everyone agreed to
in advance.

**Cell-based architecture** is a related reliability pattern worth knowing alongside
SLOs: partition your system into independent "cells" (each serving a subset of
traffic/tenants, with its own full stack of dependencies) so that a failure in one
cell has a **bounded blast radius** — it can't take down cells serving other
traffic/tenants, the same fault-isolation philosophy as bulkheads (Week 2, Day 13)
and per-user resource quotas (today's ClickHouse lesson), applied at the level of an
entire deployment topology rather than a single resource dimension.

## 4. Architecture & Design Pattern Spotlight

**Pattern: blast-radius reduction — a theme recurring at every scale studied this
month, from a single ClickHouse query's resource quota (today's ClickHouse lesson)
to bulkhead-isolated dependency calls (Week 2, Day 13) to whole-system cell-based
partitioning.** Recognizing "how do I limit how much damage one failure can cause"
as a single, recurring design question — asked at wildly different scales — is
exactly the kind of cross-scale pattern fluency this curriculum has been building.

## 5. Hands-On Lab

Pick one real component of your own platform (a specific dashboard query class, a
Kafka topic's consumer lag, a Flink job's checkpoint success rate) and define:
- A precise, measurable SLI for it.
- A specific SLO target with a stated measurement window.
- What the resulting error budget actually is, in concrete terms (e.g., "X minutes
  of acceptable lag per month," "Y failed dashboard loads per week").
- What operating policy you'd actually apply once that budget is exhausted — what,
  specifically, would your team stop or start doing?

## 6. Real-World Product Comparison

- **Google's SRE practice** (the origin of the SLI/SLO/error-budget framework, from
  the widely-referenced SRE book) formalized exactly this operating-policy approach —
  worth reading the original framing if this resonates as a useful tool for your own
  team's reliability conversations.
- **Cell-based architecture** is used at large scale by companies like **AWS**
  (many services are internally partitioned into cells/shards precisely for blast-
  radius containment) — a direct, large-scale validation of the pattern.

## 7. Common Production Pitfalls

- Defining an SLO without a clear measurement window or without actually
  instrumenting the underlying SLI — an SLO that can't be measured isn't actionable.
- Treating error-budget exhaustion as merely informational rather than as a real,
  pre-agreed trigger for changing team behavior — the framework only works if the
  policy attached to it is actually honored.
- Setting an SLO target without considering actual user/business impact — a target
  that's either needlessly strict (wasting engineering effort chasing unnecessary
  reliability) or too loose (allowing a genuinely user-impacting failure rate) both
  undermine the framework's value.

## 8. Review Questions
1. What's the precise distinction between an SLI, an SLO, and an error budget?
2. Why is the operating policy attached to error-budget exhaustion the genuinely
   useful part of this framework?
3. How does cell-based architecture relate to the bulkhead pattern from earlier this
   month?
4. What's one real SLI/SLO pair you could define and start measuring for your own
   platform today?

## 9. Proficiency Checkpoint
If you can define a real, measurable SLI/SLO/error-budget triple and articulate the
operating policy it implies, you're at Level 3.5.

## Next
Day 17 covers observability architecture broadly — metrics, logs, and traces, and how
a single correlation ID would flow through your own multi-system pipeline.
