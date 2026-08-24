# Day 20: Elasticsearch — Alternatives: OpenSearch, Typesense, Meilisearch, Algolia

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Compare OpenSearch's and Elasticsearch's current licenses, and understand the fork
dynamics that parallel today's Redis/Valkey lesson.

## 2. Core Concept (basics → advanced)

Elasticsearch itself underwent a strikingly similar licensing story to Redis's,
slightly earlier: Elastic changed licensing away from fully permissive open source,
prompting **AWS to fork the last open-source version into OpenSearch**, now
governed under the OpenSearch Software Foundation — structurally the same dynamic
as the Redis-to-Valkey story (today's Redis lesson), just a few years earlier and
with a different corporate actor leading the fork.

Separately, **Typesense and Meilisearch** are newer, purpose-built search engines
designed around simpler operational models and faster default relevance tuning for
common use cases (particularly instant/typo-tolerant search), trading some of
Elasticsearch's generality and aggregation power (Week 1, Day 4) for simpler setup
and often better out-of-the-box relevance for straightforward use cases.
**Algolia** (referenced back in Week 1, Day 3) is a fully-managed, proprietary
search-as-a-service — the "buy, don't build or self-host at all" end of this
spectrum.

## 3. How It Really Works (Internals)

The OpenSearch/Elasticsearch divergence is worth watching specifically because,
unlike a simple rebrand, **the two codebases have been diverging since the fork** —
new Elasticsearch features (including things like vector search enhancements,
Week 2 Day 13) and new OpenSearch features aren't guaranteed to stay in parity
over time, meaning "OpenSearch vs. Elasticsearch" is increasingly a genuine
feature-comparison question, not just a licensing-preference question, the longer
the fork has existed.

## 4. Architecture & Design Pattern Spotlight

**Pattern: fork dynamics after a license change — directly parallel to today's
Redis/Valkey lesson, and worth recognizing as a recurring pattern in the broader
open-source ecosystem** (also seen historically in other projects beyond this
month's two examples) — a license change by a commercial steward reliably produces
a community/competitor fork when the change is restrictive enough, and evaluating
either side of such a fork requires checking both current licensing terms *and*
current feature parity, since both drift over time.

## 5. Hands-On Lab

Compare OpenSearch's and Elasticsearch's current official licenses directly from
each project's own documentation (don't rely on this lesson's snapshot, since
terms can change). Then pick one feature studied this month (vector search/kNN,
Week 2 Day 13, is a good candidate) and check whether it's currently available,
and with what maturity, in both OpenSearch and Elasticsearch — this is a concrete
way to assess actual feature-parity drift rather than assuming the fork remains a
pure drop-in equivalent.

## 6. Real-World Product Comparison

- **AWS OpenSearch Service** is the natural choice for AWS-centric organizations
  wanting a managed, Elasticsearch-API-compatible search service without Elastic's
  own licensing terms.
- **Typesense/Meilisearch** are increasingly popular for developer-facing,
  simpler search use cases (e-commerce site search, documentation search) where
  Elasticsearch's full aggregation/analytics power (this month's Week 1-2 material)
  is unnecessary overhead — worth considering when the actual requirement is
  "good search," not "a general-purpose analytics engine that also does search."

## 7. Common Production Pitfalls

- Assuming OpenSearch and Elasticsearch remain feature-identical indefinitely
  after the fork — verify current parity for any specific feature you depend on,
  rather than assuming.
- Choosing Elasticsearch's full feature set for a use case that's really just
  "good search," when a simpler, purpose-built tool (Typesense/Meilisearch) would
  meet the actual requirement with less operational overhead.
- Not re-evaluating licensing/fork risk periodically for dependencies already in
  production, the same pitfall from today's Redis lesson.

## 8. Review Questions
1. What's the structural parallel between the OpenSearch fork and the Valkey fork?
2. Why does feature parity between a fork and its origin project require ongoing
   verification, not a one-time check?
3. When would Typesense/Meilisearch be a better fit than full Elasticsearch?
4. What does Algolia represent on the build-vs-buy spectrum?

## 9. Proficiency Checkpoint
If you can accurately compare current OpenSearch/Elasticsearch licensing and
feature parity for a specific feature, you're at Level 3.5.

## Next
Day 21 is this week's integrated lab and review.
