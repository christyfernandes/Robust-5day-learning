# Day 12: ClickHouse — Codecs & Compression

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Apply the `Delta` codec to a monotonic timestamp column and compare compressed size
against the default — directly relevant to your cost-reduction mission.

## 2. Core Concept (basics → advanced)

ClickHouse compresses data **per column** (a direct benefit of columnar storage —
values within one column tend to be far more similar to each other than values across
different columns, which compresses much better than row-oriented data). Beyond the
general-purpose codecs (`LZ4` — fast, moderate compression, the default; `ZSTD` —
slower, meaningfully better compression ratio), ClickHouse offers **specialized
codecs** that exploit specific data patterns:

- **`Delta`**: stores the *difference* between consecutive values instead of the
  values themselves — extremely effective for monotonically increasing data (a
  timestamp column, an auto-incrementing ID), since the deltas are typically small,
  uniform numbers that compress far better than the original large, varied values.
- **`DoubleDelta`**: stores the difference *of the differences* — even more effective
  for data with a highly regular, near-constant delta (e.g., timestamps recorded at a
  fixed interval), since the second-order delta approaches zero/constant.
- **`Gorilla`**: designed specifically for floating-point time-series data (metrics)
  where consecutive values tend to be very close to each other — exploits this via
  XOR-based encoding of consecutive float values, a technique originated in
  Facebook's Gorilla time-series database paper.

## 3. How It Really Works (Internals)

Codecs can be **stacked**: a common pattern is applying `Delta` (or `DoubleDelta`)
*first* to transform the data into a more compressible representation, then a
general-purpose codec like `ZSTD` *second* to compress the resulting (now much more
uniform) delta values further — `CODEC(Delta, ZSTD)`. This two-stage approach
routinely achieves compression ratios well beyond what `ZSTD` alone could achieve on
the raw values, precisely because the delta transform exposes redundancy that a
general-purpose compressor couldn't otherwise detect.

Since compression directly determines how much data must be read from disk (and,
critically for your cost-reduction mission, how much storage capacity you actually
need to provision), codec selection is a direct, quantifiable lever on infrastructure
cost — choosing `Delta+ZSTD` over the default for a genuinely monotonic column isn't a
micro-optimization; on large time-series-heavy tables, it can be a substantial
fraction of total storage footprint.

## 4. Architecture & Design Pattern Spotlight

**Pattern: column-aware, data-pattern-specific compression, chosen per column rather
than applied uniformly.** This is a deliberate design philosophy difference from most
row-oriented databases (where compression, if present at all, is usually a single
generic algorithm applied uniformly) — ClickHouse treats codec selection as a
first-class per-column schema decision, on par with choosing a data type, precisely
because the payoff (for the right data pattern) is large enough to be worth that
granularity of control.

## 5. Hands-On Lab

```sql
CREATE TABLE events_default (
    event_time DateTime,
    value Float64
) ENGINE = MergeTree ORDER BY event_time;

CREATE TABLE events_delta (
    event_time DateTime CODEC(Delta, ZSTD),
    value Float64 CODEC(Gorilla, ZSTD)
) ENGINE = MergeTree ORDER BY event_time;

-- insert the SAME ~10M synthetic rows (monotonic timestamps, smoothly-varying floats)
-- into both tables, then compare:
SELECT table, formatReadableSize(sum(data_compressed_bytes)) AS compressed
FROM system.parts
WHERE table IN ('events_default', 'events_delta') AND active
GROUP BY table;
```
Compare the compressed size difference directly — this is a concrete, quantifiable
number you can bring back to the cost-reduction conversation this week.

## 6. Real-World Product Comparison

- **Facebook's Gorilla** time-series database paper is the direct origin of the
  `Gorilla` codec — a well-documented, real-world case study in exactly this kind of
  domain-specific compression strategy for metrics data.
- **BigQuery**'s columnar storage also compresses per-column, but does not expose
  this level of codec-selection control to the user — another concrete instance of
  the trade-off between "the platform decides for you" (BigQuery) and "you have
  granular, cost-relevant control" (ClickHouse) that runs through much of this
  migration decision.

## 7. Common Production Pitfalls

- Leaving every column at the default codec without checking which columns are
  genuinely monotonic or near-constant-delta and would benefit meaningfully from
  `Delta`/`DoubleDelta`/`Gorilla`.
- Applying `Delta`/`Gorilla` to a column that *isn't* actually monotonic or smoothly
  varying — these codecs can perform *worse* than a general-purpose codec on data that
  doesn't match their assumed pattern.
- Not measuring actual compressed size before and after a codec change — the benefit
  is highly data-dependent, and assuming a codec choice from one table applies equally
  well to a superficially similar column elsewhere is a guess, not a measurement.

## 8. Review Questions
1. Why does `Delta` compress a monotonically increasing column so much better than
   the raw values would compress?
2. What's the benefit of stacking `Delta` and `ZSTD` together rather than using either
   alone?
3. When would `Gorilla` be the wrong codec choice?
4. Why does BigQuery not expose this same level of codec control, and what does that
   trade-off mean for your migration decision?

## 9. Proficiency Checkpoint
If you can identify which real columns in your production schema would benefit from
specific codecs and quantify the actual compression improvement, you're at Level 3.5 —
directly reusable in your cost-reduction analysis.

## Next
Day 13 covers ClickHouse's native Kafka table engine — direct streaming ingestion from
Kafka into a MergeTree table, without a separate consumer application.
