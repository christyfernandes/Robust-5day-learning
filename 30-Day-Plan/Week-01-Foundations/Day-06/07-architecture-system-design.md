# Day 6: Architecture — Caching Strategy & Invalidation

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Map your own MDO portal's full cache hierarchy end to end, and mark the specific layer
where you suspect the cache-bypass problem is actually occurring.

## 2. Core Concept (basics → advanced)

A real production system rarely has "a cache" — it has a **hierarchy** of caches, each
with its own invalidation rules and failure modes:

```
Browser cache (client-side, respects Cache-Control/ETag headers)
     │
     ▼
CDN (edge cache — caches full responses close to the user)
     │
     ▼
Application-layer cache (e.g., Redis — caches query results or rendered fragments)
     │
     ▼
Database / query engine (the actual source of truth — e.g., BigQuery/ClickHouse)
```

Every layer is a chance for staleness (data changed at the source, but an intermediate
layer still serves the old version) or, just as commonly in practice, a chance for a
request to **bypass** a layer entirely when it shouldn't (a misconfigured cache key, a
query parameter that varies unexpectedly, or an embedded dashboard iframe with
different caching semantics than the parent page) — turning what should be a cheap
cache hit into a full, expensive query against the source engine every time.

## 3. How It Really Works (Internals)

**Cache invalidation** strategies, in increasing complexity:
- **TTL-based expiry**: simplest — cache entries expire after a fixed time, guaranteeing
  a bound on staleness but not immediate consistency.
- **Explicit invalidation on write**: the write path actively evicts/updates the
  relevant cache entries — more immediately consistent, but requires the write path to
  correctly know every cache key that could be affected (a real source of subtle bugs
  when a single write affects many derived cache entries).
- **Cache-key design**: this is where most real bypass bugs actually live — if a cache
  key doesn't fully capture everything that affects the response (e.g., missing a
  per-organization dimension, or a filter parameter), you either get incorrect cache
  hits (serving org A's cached data to org B) or, more commonly for a dashboard, a cache
  key that's *too specific* (includes something that varies per request, like a
  timestamp or session token) so it never actually hits the cache at all — every request
  looks "unique" to the cache layer and falls through to the source engine.

This second failure mode — an overly-specific cache key causing near-100% cache
*misses* despite a caching layer technically being in place — is a very common root
cause of "why is our dashboard so expensive" investigations, and worth checking first.

## 4. Architecture & Design Pattern Spotlight

**Pattern: "there are only two hard things in computer science: cache invalidation,
naming things, and off-by-one errors."** The joke endures because cache-key design and
invalidation genuinely are this hard in practice — every layer above adds real
complexity, and a bug at any single layer (not just "no cache") can look identical
from the outside: expensive, repeated queries against the source of truth.

## 5. Hands-On Lab

Sketch your own MDO portal's actual cache hierarchy, layer by layer, with your best
current understanding of each layer's cache-key strategy and invalidation rule. For
each layer, ask explicitly: **could a request "look unique" to this layer when it
shouldn't?** (Check for things like: per-request timestamps embedded in a query, session
tokens included in what should be a shared cache key, or an embedded iframe's requests
carrying different headers than a direct page load.) Mark your best-guess bypass point
— this is a real diagnostic artifact for this week's actual POC work, not just an
exercise.

## 6. Real-World Product Comparison

- **CDN-layer caching** (Cloudflare, Fastly, Akamai) is explicitly designed around
  cache-key normalization (deciding which query parameters/headers matter for
  cacheability) — precisely the same discipline your dashboard's embedded queries need.
- Many BI/dashboard tools (Looker among them) have their own query-result caching layer
  *in addition to* whatever the underlying warehouse does — meaning a cache-bypass bug
  can exist at the BI-tool layer, the CDN layer, or the application layer independently,
  which is exactly why a careful, full-hierarchy sketch (not just "check Looker's
  cache settings") matters for this week's investigation.

## 7. Common Production Pitfalls

- Assuming "we have a cache" means every layer is actually being hit — verify hit rates
  per layer explicitly, don't infer it from the presence of caching infrastructure.
- Including something that varies per-request (a timestamp, a session ID) in a cache
  key meant to be shared across users/requests — silently defeats caching entirely
  while looking, superficially, like caching is configured correctly.
- Debugging cost/latency problems by only looking at the source engine (BigQuery/
  ClickHouse) rather than first confirming which cache layer, if any, is actually being
  bypassed.

## 8. Review Questions
1. Why can an overly-specific cache key cause near-100% cache misses despite caching
   being "in place"?
2. What's the practical trade-off between TTL-based expiry and explicit
   invalidation-on-write?
3. Why is per-layer hit-rate verification necessary, rather than assuming a cache
   hierarchy is working end to end?
4. Name one concrete way an embedded dashboard iframe could bypass caching that a
   direct page load wouldn't.

## 9. Proficiency Checkpoint
If you can sketch a real, multi-layer cache hierarchy and identify a plausible bypass
point with a specific, falsifiable hypothesis, you're at Level 2 moving into Level 3 —
and you've produced a genuinely useful artifact for this week's investigation.

## Next
Day 7 combines this week's concepts into one lab session — including your first ADR,
built on this exact caching investigation.
