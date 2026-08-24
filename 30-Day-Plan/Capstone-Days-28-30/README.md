# Capstone — Days 28–30
### Target exit proficiency: Level 4–4.5 on all 7 tracks, portfolio-ready

Three days, one integrated deliverable. Where Week 4 built architecture *judgment*,
the Capstone forces you to actually **build and document** one coherent system —
because designing on paper and shipping a working, documented platform are different
skills, and the gap between them is exactly what separates Level 3.5 from Level 4+.

---

## Day 28 — Build

Integrate all 7 tracks into one **"Real-Time Analytics Platform"**:

```
Source events → Kafka (ingest, partitioned by key)
              → Flink (enrichment, dedup, windowed aggregation)
              → ClickHouse (OLAP serving layer: raw table + Refreshable MVs)
              → Redis (hot-path cache in front of ClickHouse for point lookups)
              → Elasticsearch (search/log layer for the same event stream)
              → PySpark (batch backfill / reprocessing job for historical corrections)
```

Deliverables:
- [ ] Working `docker-compose.yml` bringing up all 6 tool services (extend
      `../../legacy-5-day-plan/FinalProject/docker-compose.yml` — it already has
      Kafka/Redis/Elasticsearch wiring — with Flink and ClickHouse services added)
- [ ] A producer generating realistic events into Kafka
- [ ] A Flink job consuming, enriching, and writing to at least 2 of {ClickHouse,
      Redis, Elasticsearch}
- [ ] A ClickHouse Refreshable Materialized View computing a real-time rollup
- [ ] One architecture diagram of the whole thing

## Day 29 — Document

Write the full documentation package — every one of these should be genuinely reusable
as a template at Tarento, not just an academic exercise:
- [ ] **README** for the platform (what it does, how to run it, architecture diagram)
- [ ] **ADRs** for the major decisions (why Kafka not Pulsar, why ClickHouse not
      Druid, why this sharding key, etc.) — reuse the ADR format from Week 3 Day 21
- [ ] **Runbooks** for the failure modes you've now personally debugged this month
      (consumer lag, Flink bounded-source misconfiguration, Spark OOM, ClickHouse
      fan-out)
- [ ] **Cost model** — the self-hosted vs. managed comparison framework from Week 3,
      applied to this platform
- [ ] **Monitoring spec** — what metrics/dashboards you'd stand up in production, and why

## Day 30 — Assess

- [ ] Score yourself honestly against every checklist in `../PROFICIENCY_RUBRIC.md`
- [ ] Do a full mock architecture review of the Capstone platform (ideally with an
      actual colleague; failing that, role-play both sides)
- [ ] Fill in the final column of `../PROGRESS_TRACKER.md`

---

## Path to Level 5

Level 5 (deep specialist / contributor-level) is intentionally out of scope for 30
days — real Level 5 comes from production scars, not study time. Once you've hit Level
4 across all 7 tracks, here's the realistic next-quarter path:

1. **Pick 1–2 tracks to specialize in.** Given your role and the live POC, ClickHouse
   and Architecture/System Design are the natural picks — you already have production
   responsibility for both.
2. **Let production be the curriculum.** The next real incident, cost review, or
   design decision *is* the next lesson — you now have the vocabulary and mental
   models to extract the general principle from the specific mess, which is most of
   what separates Level 4 from Level 5.
3. **Contribute upstream, even in a small way**, once you hit a real edge case — a
   documentation PR, a bug report with a solid repro, or a config recommendation to a
   project's discussion forum. This is usually how Level 5 practitioners actually got
   there: not by studying more, but by being the person who found and reported (or
   fixed) something real.
4. **Write it up.** An internal blog post, a tech talk, or a detailed postmortem
   shared with your org turns your Level 4 experience into a durable artifact — and
   forces the kind of precise explanation that reveals whether you're really at Level 5
   on a topic or still at a strong Level 4.

Good luck — and if you're reading this after finishing Day 30: you built a genuinely
production-shaped analytics platform, end to end, with the documentation package to
back it up. That's a real portfolio piece, not just a study log.
