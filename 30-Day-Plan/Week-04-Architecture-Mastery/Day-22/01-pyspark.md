# Day 22: PySpark — Design Patterns: Medallion Architecture

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Sketch a Medallion pipeline for one of your real datasets, and explain what each
layer's specific job is — not just its name.

## 2. Core Concept (basics → advanced)

**Medallion architecture** organizes a lakehouse (Week 2, Day 13) into three
progressively refined layers:

- **Bronze**: raw data, as-ingested, minimal transformation — a durable, replayable
  record of exactly what arrived, in its original form (schema-on-read, Week 2 Day
  12's data-lake framing).
- **Silver**: cleaned, validated, conformed data — deduplicated, schema-enforced,
  joined with reference data where needed — the layer where most data-quality
  logic actually lives.
- **Gold**: business-level aggregates and marts, shaped specifically for
  consumption (dashboards, ML features) — often the layer that maps most directly
  onto what a BI tool or downstream consumer actually queries.

```
Raw source ──▶ BRONZE (as-is, replayable)
                    │
                    ▼ clean, dedupe, validate, conform schema
              SILVER (trustworthy, but still fairly granular)
                    │
                    ▼ aggregate, join, shape for specific consumption
               GOLD (business-ready, consumption-optimized)
```

## 3. How It Really Works (Internals)

The key operational insight: each layer's **`MERGE`-based upsert** (Week 2, Day 13's
lakehouse transaction log) is what makes this pipeline **idempotent and
re-runnable** — reprocessing a bronze batch through to silver again (e.g., after
fixing a bug in the cleaning logic) should produce the same silver result, not
duplicate or corrupt it, precisely because `MERGE` (rather than blind `INSERT`)
handles the "this record may already exist, update it correctly" case. This
directly connects to Week 1 Day 1's lineage-based fault tolerance — Medallion's
bronze layer plays a role analogous to Kafka's durable log (today's Kafka lesson):
a replayable source of truth that downstream layers can always be rebuilt from.

## 4. Architecture & Design Pattern Spotlight

**Pattern: layered data refinement — separating "as received" from "cleaned" from
"business-ready" as three distinct, independently-reprocessable stages.** This
maps directly onto the Lambda architecture's batch-layer concept (Week 2, Day 11)
and is a specific, concrete instantiation of it — Medallion is, in effect, a
detailed blueprint for what "the batch layer" actually does internally.

## 5. Hands-On Lab

Sketch a Medallion pipeline for one of your own real datasets (Sunbird telemetry
is a strong candidate): what does bronze look like for this data (the raw event
shape)? What specific cleaning/validation/dedup logic belongs in silver? What
gold-layer aggregate(s) would actually feed your real dashboards? For each layer
transition, specify whether it's implemented as a `MERGE` (idempotent upsert) or a
simple append, and why.

## 6. Real-World Product Comparison

- **Databricks** popularized the "Medallion" terminology specifically, though the
  underlying layered-refinement pattern predates the name and appears under
  different terminology across many lakehouse implementations.
- This maps directly onto your own **BigQuery→ClickHouse migration** — your raw
  ingested events (bronze-equivalent), any intermediate cleaned tables (silver-
  equivalent), and your dashboard-serving aggregates/Refreshable MVs (Week 1, Day
  6 — gold-equivalent) are the same architectural shape, whichever specific engine
  implements it.

## 7. Common Production Pitfalls

- Skipping the silver layer and jumping from raw bronze data straight to
  gold-layer aggregates — data-quality issues then surface directly in
  business-facing dashboards rather than being caught and fixed at a dedicated
  cleaning stage.
- Using blind `INSERT` instead of `MERGE` for silver/gold layer updates, breaking
  idempotent reprocessing — a re-run after a bug fix duplicates rather than
  corrects data.
- Not clearly documenting which layer a given downstream consumer should actually
  query — accidentally letting a BI tool query bronze or silver directly, bypassing
  the intended gold-layer contract.

## 8. Review Questions
1. What's the specific job of each Medallion layer, beyond just "increasingly
   clean"?
2. Why does `MERGE`-based upsert matter for safe reprocessing?
3. How does Medallion relate to Lambda architecture's batch layer?
4. How would you map your own real pipeline onto bronze/silver/gold?

## 9. Proficiency Checkpoint
If you can design a real Medallion pipeline with correct `MERGE`-vs-append
decisions per layer, you're at Level 4.

## Next
Day 23 covers real case studies — Databricks, Netflix, Airbnb — grounding this
pattern in actual production usage.
