# Day 23: PySpark — Case Studies: Databricks, Netflix, Airbnb

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Read one public engineering account from each of Databricks, Netflix, and Airbnb,
and extract one specific architectural choice you didn't already expect.

## 2. Core Concept (basics → advanced)

Reading real companies' own accounts of their architecture serves a different
purpose than this month's conceptual lessons — it tests whether your mental
models (Catalyst, Tungsten, shuffle, Weeks 1-2) actually match how experienced
practitioners reason about trade-offs *in a specific, messy, real context*, not
just in the clean, isolated form a lesson presents them.

- **Databricks**: as Spark's commercial steward, their engineering blog is the
  primary source for Photon (Week 1, Day 8's codegen-vs-vectorization
  comparison) and Delta Lake (Week 2, Day 13) design rationale — read for *why*
  specific engineering trade-offs were made, not just *what* was built.
- **Netflix**: publishes extensively on large-scale Spark usage for
  recommendation-system feature pipelines and batch ETL, often discussing
  concrete operational lessons (cluster sizing, cost optimization, Week 3 Day 15
  and Day 19-20) at a scale most organizations never reach.
- **Airbnb**: has published on their internal data platform's evolution,
  including lakehouse adoption (Week 2, Day 13) and the organizational
  challenges of a company-wide data platform, not just the pure technology
  choices.

## 3. How It Really Works (Internals)

The specific skill this lab builds: reading a real engineering account and
**mapping its concrete details back onto this month's vocabulary** — when Netflix
discusses a shuffle-related performance problem, can you identify precisely
which Week 1 Day 3 mechanism they're describing, even if they use different
terminology? When Databricks discusses Photon's design, can you connect it
explicitly to Tungsten codegen's trade-offs (Week 1, Day 8)? This translation
exercise — real-world account to precise technical vocabulary — is exactly what
separates "I've studied Spark" from "I can read and critically evaluate someone
else's Spark architecture," a genuinely different and more advanced skill.

## 4. Architecture & Design Pattern Spotlight

**Pattern: case-study literacy — the ability to read a real engineering account
critically, mapping its specifics onto precise underlying mechanisms rather than
taking claims at face value.** This is a deliberately different skill from the
conceptual/hands-on skills built in Weeks 1-3, and it's what Day 27's mock review
will specifically test.

## 5. Hands-On Lab

Read one recent public engineering blog post or talk from each of Databricks,
Netflix, and Airbnb (search their respective engineering blogs) covering Spark
usage. For each, write down: one architectural choice you didn't already expect,
and which specific concept from this month's curriculum (name the exact lesson)
best explains *why* that choice makes sense given their stated constraints.

## 6. Real-World Product Comparison

This lesson *is* the product comparison exercise — the goal today is direct
engagement with primary sources, not a secondary summary.

## 7. Common Production Pitfalls

- Reading a company's architecture blog and assuming their choices transfer
  directly to your own context without considering their very different scale
  and constraints.
- Taking marketing-adjacent claims (common in vendor blogs like Databricks')
  at face value without applying the critical, mechanism-level scrutiny this
  month's curriculum has built.
- Skimming for the "answer" rather than genuinely reading for the reasoning —
  the reasoning, not the specific choice, is what's actually transferable to your
  own decisions.

## 8. Review Questions
1. What's the difference between reading for "what they built" versus "why they
   built it that way"?
2. Why doesn't a choice that works at Netflix's scale necessarily transfer to a
   smaller organization?
3. What's one architectural choice you found that surprised you, and why?
4. How does this case-study skill differ from this month's earlier hands-on labs?

## 9. Proficiency Checkpoint
If you can read a real engineering account and precisely map its details onto
this month's technical vocabulary, you're at Level 4.

## Next
Day 24 covers "when NOT to use it" decision frameworks — the natural next step
after grounding your knowledge in real-world usage.
