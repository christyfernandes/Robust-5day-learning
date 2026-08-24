# Day 9: Elasticsearch — Relevance Tuning: BM25 Parameters & function_score

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Adjust BM25's `k1` and `b` parameters on a test index and observe how result ordering
shifts, and use `function_score` to blend relevance with a business signal.

## 2. Core Concept (basics → advanced)

Day 3 introduced BM25's three inputs (term frequency with saturation, IDF, field-length
normalization) conceptually. Today: the two parameters that actually control that
behavior, tunable per index:

- **`k1`** controls how quickly term-frequency saturation kicks in — higher `k1` means
  additional occurrences of a term keep contributing more score for longer before
  saturating (default `1.2`; range typically 0–3 in practice).
- **`b`** controls how strongly field-length normalization is applied — `b=1` fully
  normalizes for field length (a match in a long field is penalized more); `b=0`
  disables length normalization entirely (a match counts the same regardless of field
  length).

**`function_score`** lets you combine the BM25 relevance score with an arbitrary
business signal (popularity, recency, price) via a configurable blending function
(`sum`, `multiply`, `max`, etc.) — this is how "relevant AND popular" or "relevant AND
recent" ranking is actually implemented, since BM25 alone only knows about term
statistics, never about business context.

## 3. How It Really Works (Internals)

Tuning `k1` down (say, to `0.5`) makes a document that mentions a term 10 times only
modestly more relevant than one mentioning it twice — useful for domains where
keyword-stuffing shouldn't be rewarded much. Tuning `b` down (toward `0`) is useful when
document length genuinely doesn't correlate with topical focus for your domain (e.g., a
product catalog where titles and descriptions naturally vary in length for reasons
unrelated to relevance) — without this adjustment, longer descriptions can be unfairly
penalized purely for their length, even when equally relevant.

`function_score`'s `boost_mode` parameter decides how the function's output combines
with the base BM25 query score (`multiply` is common — final score = BM25 score ×
function value, so a popularity function acts as a genuine multiplier on relevance
rather than replacing it) — getting `boost_mode` wrong is a common cause of
"popular but irrelevant" results dominating, when the intent was "relevant, tie-broken
by popularity."

## 4. Architecture & Design Pattern Spotlight

**Pattern: tunable probabilistic ranking, exposed as explicit, documented knobs.** This
is a deliberate design choice — Elasticsearch could have hidden BM25's parameters as an
implementation detail, but instead exposes `k1`/`b` per-index specifically because
different domains (news search vs. e-commerce vs. legal document search) genuinely
benefit from different tuning, and no single default serves all of them equally well.

## 5. Hands-On Lab

```json
PUT /products
{ "settings": { "similarity": { "custom_bm25": {
    "type": "BM25", "k1": 0.3, "b": 0.0
}}}}
```
Reindex your Day 3 `products` test data into this new index, run the same query as
Day 3, and compare `_score` values and result ordering against the default-similarity
index. Then add a `function_score` wrapper blending in a synthetic `popularity` field
(add one to your test docs) with `boost_mode: multiply`, and observe how a less
textually relevant but more popular product can now outrank a more textually relevant
but unpopular one.

## 6. Real-World Product Comparison

- **News and legal search** applications often tune `k1` down and disable/reduce `b`,
  since keyword repetition and document length vary for reasons unrelated to topical
  relevance in those domains.
- **Algolia**, by contrast, doesn't expose BM25 tuning at this level of granularity at
  all — it uses its own proprietary, more rule-based ranking formula, explicitly
  trading tunability for a simpler, more opinionated out-of-the-box ranking experience
  aimed at e-commerce use cases.

## 7. Common Production Pitfalls

- Tuning `k1`/`b` based on a handful of manually-inspected queries rather than a
  proper relevance evaluation set — small tuning changes can improve some queries while
  quietly regressing others; without systematic evaluation, you're guessing.
- Using `function_score`'s default `boost_mode` (`multiply`) without checking whether
  your business-signal function can return `0` — a `0` popularity score multiplied
  against BM25 zeroes out an otherwise perfectly relevant result entirely.
- Re-tuning relevance parameters without re-testing existing saved queries/dashboards
  that depend on a particular ordering — a tuning change is, in effect, a behavior
  change for every consumer of that index's search results.

## 8. Review Questions
1. What does raising `k1` do to the marginal value of additional term occurrences?
2. Why might disabling `b` (`b=0`) be appropriate for a product catalog?
3. What does `boost_mode: multiply` risk if your business-signal function can return 0?
4. Why does Elasticsearch expose these as tunable parameters rather than fixing them?

## 9. Proficiency Checkpoint
If you can tune `k1`/`b` deliberately for a stated domain and correctly predict the
ranking effect, and safely combine relevance with a business signal via
`function_score`, you're at Level 3.

## Next
Day 10 covers data modeling — nested vs. object vs. parent-child — the schema-design
decisions that determine what your relevance-tuned queries can even express.
