# Day 22: Architecture — Reference Architecture: Your Real Target Stack

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Draw the full Kafka→Flink→ClickHouse→Redis/Elasticsearch reference architecture
as one diagram — synthesizing every pattern studied this month into a single,
coherent picture.

## 2. Core Concept (basics → advanced)

A **reference architecture** names each stage's role explicitly, using the
patterns and vocabulary built across this entire curriculum:

```
[Sources] ──▶ Kafka (durable log, Week 1 Day 1;
                     event backbone for Outbox/Saga/CQRS, today's Kafka lesson)
                  │
                  ▼
              Flink (stream processing — bounded/unbounded handled correctly,
                     Week 2 Day 10; exactly-once sinks, Week 2 Day 9;
                     checkpointed state, Week 1 Day 5-6)
                  │
                  ├──▶ ClickHouse (OLAP serving layer — OBT/star/dictionary
                  │                schema design, today's ClickHouse lesson;
                  │                hot/cold tiering, Week 2 Day 10;
                  │                Refreshable MVs, Week 1 Day 6)
                  │
                  ├──▶ Redis (hot-tier cache — cache-aside/write-through,
                  │           Week 2 Day 11; cache-key discipline, Week 1 Day 6)
                  │
                  └──▶ Elasticsearch (CQRS read model for search/facets,
                                       today's Elasticsearch lesson)
                  │
                  ▼
              BI Layer (Looker/dashboards — querying ClickHouse directly,
                        or via Redis-cached results)
```

## 3. How It Really Works (Internals)

The genuine value of drawing this as one diagram — rather than seven separate
per-track mental models — is seeing the **interaction points** explicitly: where
does Kafka's exactly-once guarantee (Week 2, Day 9) need to be preserved all the
way through Flink's sink (Week 2, Day 9's 2PC lesson) to ClickHouse (which,
notably, isn't transactional the same way relational systems are — a real caveat
Day 26's integration lesson addresses directly)? Where does cache invalidation
(Week 1, Day 6; Week 2, Day 11) need to be triggered by the same event stream
feeding ClickHouse, to keep Redis and ClickHouse from silently diverging? These
cross-component questions are exactly what a single, unified reference diagram
surfaces that per-system documentation, studied separately, does not.

## 4. Architecture & Design Pattern Spotlight

**Pattern: ingest → stream process → OLAP store → BI layer — the master
reference shape this entire curriculum has been building toward, one stage at a
time.** Every individual lesson this month has been, in effect, deepening your
understanding of one node or edge in this exact diagram — today is where that
accumulated depth becomes one coherent, presentable architecture.

## 5. Hands-On Lab

Draw your own actual target-state reference architecture (the real
BigQuery→ClickHouse migration architecture, not a generic template), labeling
every stage with the *specific* pattern/decision this month's lessons equipped
you to make for it: your chosen sharding key (Week 1, Day 4), your OBT/star/
dictionary schema decision (today's ClickHouse lesson), your caching pattern
(Week 2, Day 11), your exactly-once guarantee boundary (Week 2, Day 9), your
tiering policy (Week 2, Day 10), and your monitoring/security posture (Week 3).
This single diagram is your month's most comprehensive synthesis artifact.

## 6. Real-World Product Comparison

- This is precisely the kind of reference architecture diagram **Netflix,
  Uber, and Cloudflare** (Day 23's case studies) publish in their own engineering
  blogs — a single picture capturing an entire data platform's major
  components and their interactions, exactly the artifact worth producing for
  your own team.

## 7. Common Production Pitfalls

- Documenting each system's configuration separately without ever producing the
  unified diagram, missing the cross-component interaction questions it would
  surface.
- Treating this diagram as a one-time artifact rather than keeping it updated as
  the actual architecture evolves — a stale reference diagram misleads more than
  it helps.
- Not explicitly labeling *why* each stage's specific decision was made (the
  pattern/lesson behind it) — a diagram without rationale is much less useful for
  onboarding new team members or defending decisions in a review (Day 27).

## 8. Review Questions
1. What cross-component question does a single unified diagram surface that
   separate per-system documentation misses?
2. Why does ClickHouse's lack of full relational transactionality matter for the
   Flink-sink boundary specifically?
3. What's the value of labeling each stage with its specific underlying decision
   and rationale?
4. How would you keep this diagram from going stale as your architecture evolves?

## 9. Proficiency Checkpoint
If you've produced a complete, correctly-labeled reference architecture diagram
for your own real target stack, you're at Level 4 — this is the single most
valuable synthesis artifact from the entire curriculum so far.

## Next
Day 23 grounds this reference architecture in real companies' actual, public
engineering decisions — case studies across all 7 tracks.
