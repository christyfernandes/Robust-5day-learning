# Day 24: Architecture — Trade-off Frameworks: Build vs. Buy & Boring Technology

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Apply the build-vs-buy and "boring technology" frameworks to one real, upcoming
decision at your own work.

## 2. Core Concept (basics → advanced)

Two complementary decision frameworks for evaluating any architectural choice:

- **Build vs. buy**: the recurring question underneath most of this month's
  managed-vs-self-hosted comparisons (Spark/Databricks, Kafka/Confluent Cloud,
  ClickHouse/BigQuery, Week 3 Days 19-20) — build (self-host/self-develop) when
  you need control, customization, or cost efficiency at your specific scale;
  buy (managed/vendor) when operational simplicity and reduced team burden
  outweigh the premium and reduced control.
- **"Boring technology"** (a term popularized in the industry, notably by Dan
  McKinley's widely-cited essay): deliberately prefer well-understood, mature,
  "boring" technology for most of a system, reserving genuine
  innovation-tokens for the few places where a novel technology choice
  actually provides a decisive advantage — because every new, unfamiliar
  technology choice carries a real, ongoing operational learning and risk cost
  (exactly Week 3's tuning/monitoring/security/DR burden, multiplied across
  however many "exciting" technologies a team adopts simultaneously).

## 3. How It Really Works (Internals)

These two frameworks compose: a build-vs-buy decision should account not just
for cost (Week 3, Day 20's TCO modeling) but for how many "innovation tokens" a
given choice consumes — self-hosting ClickHouse (your own real decision) is
itself an innovation-token spend (new operational skills: Week 3's tuning,
security, DR, all genuinely new team capability compared to BigQuery's fully-
managed model) — worth spending deliberately, with the token explicitly
"budgeted" against the concrete benefit (Day 20's cost model, the fan-out
fixes from Week 2), rather than accumulated unconsciously alongside every
other new technology a team happens to adopt.

## 4. Architecture & Design Pattern Spotlight

**Pattern: total-cost framing (Week 3) + innovation-token budgeting — together,
the master framework for evaluating any build-vs-buy or new-technology
decision, including your own live ClickHouse migration.** This is the natural
capstone to Week 3's cost-focused lessons and today's "when NOT to use it"
exercises across every track — a repeatable method for any future decision,
not just this one.

## 5. Hands-On Lab

Apply this combined framework to one real, upcoming decision at your own work
(it doesn't need to be the ClickHouse migration specifically — pick any real
decision currently on your team's table). Explicitly answer: is this a build
or buy decision, and why, using Day 20's TCO-modeling discipline? How many
"innovation tokens" does the build option actually cost (new operational
skills your team would need to develop, per Week 3's specific lessons)? Is
that cost budgeted deliberately, or is it accumulating alongside other new
technology choices without anyone tracking the total?

## 6. Real-World Product Comparison

- **Dan McKinley's "boring technology" essay** (widely referenced in the
  industry) is worth reading directly — it's a short, concrete articulation of
  exactly this innovation-token budgeting discipline, from someone who
  developed it while scaling a real production system.
- Your own **ClickHouse migration** is, explicitly, an innovation-token spend
  — worth stating this plainly in your Day 21 ADR and Day 25 capstone design:
  you're consciously choosing to spend a token here because the concrete,
  quantified benefit (Day 20's cost model) justifies the new operational
  burden, not because ClickHouse is simply more interesting than the status
  quo.

## 7. Common Production Pitfalls

- Adopting new, "exciting" technology across many parts of a system
  simultaneously without any conscious accounting of the cumulative
  operational-learning cost this represents.
- Making a build-vs-buy decision purely on infrastructure cost (Day 20)
  without also weighing the innovation-token cost of new operational skills
  required.
- Treating "boring" as inherently inferior, missing that boring, well-
  understood technology is often the *correct* choice for the majority of a
  system, freeing genuine innovation-token budget for the few places it
  matters most.

## 8. Review Questions
1. What's the relationship between build-vs-buy and innovation-token
   budgeting?
2. Why is your own ClickHouse migration an innovation-token spend, and is it
   justified?
3. What's one real decision at your work you applied this framework to today?
4. Why might "boring" be the right choice for most of a system, even for a
   team capable of more sophisticated alternatives?

## 9. Proficiency Checkpoint
If you've applied this combined framework to a real decision with honest,
specific reasoning, you're at Level 4 — a genuinely senior architectural
discipline.

## Next
Day 25 is the day this entire month has been building toward: designing your
actual MDO portal migration, end to end.
