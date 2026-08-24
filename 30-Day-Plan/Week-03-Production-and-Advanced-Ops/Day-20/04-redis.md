# Day 20: Redis — Licensing Landscape: SSPL, Valkey & Managed Alternatives

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Note which license each of Redis, Valkey, and DragonflyDB ship under today, and
explain why licensing is a legitimate architectural input, not just a legal
footnote.

## 2. Core Concept (basics → advanced)

In 2024, Redis Ltd. changed Redis's license away from the fully permissive BSD
license to a **dual-license model** (RSALv2/SSPL) that restricts certain
commercial/competitive uses (notably, offering Redis as a managed service
competing with Redis Ltd.'s own commercial offering) — a significant change from
Redis's original fully-open-source status, prompting the community to fork the
last BSD-licensed version into **Valkey**, now governed under the Linux
Foundation.

```
Redis (pre-2024):        BSD (fully permissive open source)
Redis (2024+):            RSALv2/SSPL (restricts certain commercial uses)
Valkey:                   BSD-derived fork, Linux Foundation governed
DragonflyDB:               (check current license — has its own independent
                            licensing terms, separate from this Redis/Valkey story)
```

## 3. How It Really Works (Internals)

This kind of license change is a genuine **architectural risk input**, not merely a
legal department's concern — an organization building critical infrastructure on
a specific license's terms needs to account for the possibility of future license
changes affecting their ability to use, modify, or redistribute the software as
originally planned. This is precisely why "which license does this ship under, and
what's the governance model behind it (a single vendor's commercial entity vs. a
neutral foundation)" belongs in the same architectural evaluation as performance
and feature comparisons — a technically superior option with unfavorable or
uncertain licensing terms carries real organizational risk that a purely
technical comparison would miss entirely.

## 4. Architecture & Design Pattern Spotlight

**Pattern: open-source license risk as an architectural input.** This parallels the
Redpanda/Pulsar category-distinction lesson from today's Kafka track — just as
migration effort category matters for evaluating alternatives, licensing and
governance model matter as a first-class evaluation criterion alongside technical
capability, cost, and operational fit.

## 5. Hands-On Lab

Research and document the current license for Redis, Valkey, and DragonflyDB (and
note that licenses can and do change — verify against each project's own current,
official documentation rather than relying on this lesson's snapshot, since
licensing terms are exactly the kind of thing that shifts over time). For each,
note: is it governed by a single commercial vendor, a foundation, or another
structure — and what does that imply for your organization's risk tolerance if you
were to depend on it for critical infrastructure?

## 6. Real-World Product Comparison

- **AWS ElastiCache** and **GCP Memorystore** (managed Redis-compatible services)
  navigated this exact licensing change themselves — worth checking which
  underlying implementation (original Redis under its new license, or Valkey) each
  currently uses, since this affects your own downstream exposure if you use
  either managed service.
- The **Valkey fork** itself is a direct, real-world instance of exactly the kind
  of community response a restrictive license change can provoke — worth
  understanding as a case study in open-source governance risk generally, not just
  for Redis specifically.

## 7. Common Production Pitfalls

- Treating licensing as purely a legal concern disconnected from technical
  architecture decisions, missing a real organizational risk dimension.
- Not periodically re-checking licensing terms for dependencies already in
  production — license changes can happen to software you're already relying on,
  not just new adoptions.
- Choosing a technically inferior option purely on licensing grounds without
  weighing the actual, realistic risk (a license change affecting your specific use
  case) against the technical trade-off — this should be a weighed decision, not an
  automatic veto.

## 8. Review Questions
1. What changed about Redis's licensing in 2024, and what prompted the Valkey
   fork?
2. Why is licensing a legitimate architectural input rather than purely a legal
   concern?
3. What's the practical difference between vendor-governed and foundation-governed
   open-source projects for risk purposes?
4. How would you weigh a licensing risk against a technical advantage when
   choosing between alternatives?

## 9. Proficiency Checkpoint
If you can accurately state current licensing for these three projects and explain
why it matters architecturally, you're at Level 3.5.

## Next
Day 21 is this week's integrated lab and review.
