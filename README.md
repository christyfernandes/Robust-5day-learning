# The 30-Day Data Engineering Curriculum
## 7 Parallel Tracks · Basics → Advanced → Architect-Level

**PySpark · Kafka · Flink · Redis · Elasticsearch · ClickHouse · Architecture & System Design**

### What this is

This started as a 5-day crash course (still here, archived in
[`legacy-5-day-plan/`](legacy-5-day-plan/)) built when I first moved from an Angular/UI
background into data engineering. It got me moving fast on 5 technologies, but by
design it stayed shallow — 5 topics in ~2 hours a day was never going to reach
internals, real failure modes, or "why did Company X actually pick this."

A year into leading a data engineering team, this is the rebuild: **30 days, 7
parallel tracks** (the original 5, plus **ClickHouse** and **Architecture & System
Design** — the two things I actually use every day now), sequenced from basics to a
genuine **Level 4/5 target** (see the proficiency rubric below), with every topic
carrying an explicit **design-pattern spotlight** and a **real-world product
comparison**, not just tutorial-shaped how-tos.

### 👉 Start here: [`30-Day-Plan/`](30-Day-Plan/)

---

## Quick Navigation

| Document | What it's for |
|---|---|
| **[30-Day-Plan/CURRICULUM.md](30-Day-Plan/CURRICULUM.md)** | The master blueprint — full 30-day × 7-track matrix |
| **[30-Day-Plan/PROFICIENCY_RUBRIC.md](30-Day-Plan/PROFICIENCY_RUBRIC.md)** | What "Level 1–5" actually means, per track |
| **[30-Day-Plan/PRODUCT_COMPARISON_MATRIX.md](30-Day-Plan/PRODUCT_COMPARISON_MATRIX.md)** | Cross-cutting reference: who uses what, and the direct alternatives comparisons |
| **[30-Day-Plan/DAY_TEMPLATE.md](30-Day-Plan/DAY_TEMPLATE.md)** | The structure every topic-day lesson follows |
| **[30-Day-Plan/PROGRESS_TRACKER.md](30-Day-Plan/PROGRESS_TRACKER.md)** | Daily checklist + weekly self-scoring |
| **[30-Day-Plan/HOW_TO_CONTINUE.md](30-Day-Plan/HOW_TO_CONTINUE.md)** | How to expand the remaining days into full lessons |

## The 7 Tracks

| # | Track | Role in the stack |
|---|-------|---------------------|
| 1 | PySpark | Distributed batch compute & lakehouse ETL |
| 2 | Kafka | Durable, ordered event backbone |
| 3 | Flink | True (record-at-a-time) stream processing |
| 4 | Redis | In-memory cache / low-latency state |
| 5 | Elasticsearch | Full-text search & log/metric analytics |
| 6 | ClickHouse | Columnar OLAP / real-time analytics serving layer |
| 7 | Architecture & System Design | The glue — patterns and trade-offs tying the other 6 together |

## The Week Arc

| Week | Days | Theme | Exit level |
|---|---|---|---|
| [Week 1](30-Day-Plan/Week-01-Foundations/) | 1–7 | **Foundations** | Level 2 |
| [Week 2](30-Day-Plan/Week-02-Internals-and-Depth/) | 8–14 | **Internals & Depth** | Level 3 |
| [Week 3](30-Day-Plan/Week-03-Production-and-Advanced-Ops/) | 15–21 | **Production & Advanced Ops** | Level 3.5–4 |
| [Week 4](30-Day-Plan/Week-04-Architecture-Mastery/) | 22–27 | **Architecture Mastery** | Level 4 |
| [Capstone](30-Day-Plan/Capstone-Days-28-30/) | 28–30 | **Integrated build** | Level 4–4.5, portfolio-ready |

## What's Fully Written vs. What's a Brief

**Days 1–2** (all 7 tracks) are complete, full-depth lesson files — the template for
everything else. **Days 3–30** currently exist as complete, detailed **briefs**
(objective + pattern spotlight + product comparison + hands-on lab, for every single
track on every single day) inside each week's `README.md` — the entire 30-day plan is
fully designed, just not all narrated into full lesson prose yet. See
[`HOW_TO_CONTINUE.md`](30-Day-Plan/HOW_TO_CONTINUE.md) for how to expand any day (ask
Claude, or self-author from the brief) as you reach it — that's also just a more
honest way to pace 30 days of study than front-loading everything on day zero.

## Personalized to Real Work

A number of labs are deliberately built around actual production issues, not toy
examples — see `CURRICULUM.md` §6 for the full mapping, but in short: the PySpark
memory/GC incident, the Flink JobManager/bounded-source issue, and the ClickHouse
JOIN fan-out problem are all real, and several Week 3–4 labs produce documents (ADRs,
runbooks, cost models) meant to go straight to the team, not just a notebook.

---

## Also in This Repo

- **[`legacy-5-day-plan/`](legacy-5-day-plan/)** — the original 5-day plan, archived
  (including its runnable `FinalProject/` demo, which the Capstone extends).
- **[`Sunbird-data-pipeline/`](Sunbird-data-pipeline/)** — real architecture
  documentation for the Sunbird telemetry pipeline (Flink/Kafka/Redis/Druid), separate
  from this learning curriculum but referenced by it (Week 4, Day 25).

---

*Started as a 5-day sprint. This is the version built to actually get to Level 4/5.*
