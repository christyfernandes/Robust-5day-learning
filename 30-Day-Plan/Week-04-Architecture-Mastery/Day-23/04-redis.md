# Day 23: Redis — Case Studies: Twitter, GitHub, Stack Overflow

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Extract one concrete takeaway from Twitter's, GitHub's, and Stack Overflow's
public Redis usage — with particular attention to Stack Overflow's famously
small server footprint.

## 2. Core Concept (basics → advanced)

- **Twitter**: historically used Redis extensively for timeline-related
  infrastructure, including near-primary-store use cases (Week 2, Day 12's
  lesson referenced this directly) — a strong real-world example of the
  durability-configuration discipline that lesson described.
- **GitHub**: uses Redis for caching and background job queuing at very large
  scale — a good case study in the caching-pattern decisions (Week 2, Day 11)
  and monitoring discipline (Week 3, Day 17) this curriculum covered.
- **Stack Overflow**: famously documented running their entire (very
  high-traffic) site on a remarkably small number of physical servers for many
  years — Redis was a meaningful part of making that possible, alongside
  aggressive caching and a deliberately simple, well-understood architecture.

## 3. How It Really Works (Internals)

Stack Overflow's case is worth digging into specifically because it runs
counter to a common industry assumption that massive scale requires massive,
complex distributed infrastructure — their publicly documented architecture
achieved very high performance with a comparatively small, well-tuned set of
servers, in part because of disciplined caching (exactly this month's Week 2 Day
11 material) and a conscious choice to avoid unnecessary architectural
complexity. This is a genuinely useful counter-example to keep in mind against
any assumption that "more distributed, more complex" is automatically the
right answer at scale — sometimes deep understanding of a smaller number of
well-chosen tools (exactly this curriculum's approach) outperforms broad,
under-optimized complexity.

## 4. Architecture & Design Pattern Spotlight

**Pattern: case-study literacy, applied to Redis — with Stack Overflow
specifically illustrating that architectural restraint, backed by deep
understanding, can outperform default complexity.** This is a valuable
counterbalance to Week 4's broader emphasis on sophisticated patterns — knowing
when *not* to reach for them (Day 24's explicit topic) is itself a mark of
architectural maturity.

## 5. Hands-On Lab

Read a primary source on Stack Overflow's server architecture specifically
(their engineering blog has documented this in detail historically), and one
each from Twitter and GitHub's Redis usage. For Stack Overflow, identify
specifically: which of this month's caching/tuning lessons (Week 2, Day 11;
Week 3, Day 15) most directly explain how they achieved such high performance
with comparatively simple infrastructure.

## 6. Real-World Product Comparison

This lesson *is* the comparison exercise.

## 7. Common Production Pitfalls

- Assuming architectural complexity is inherently necessary for high traffic,
  missing the Stack Overflow counter-example.
- Applying Twitter-scale distributed-systems complexity to a use case that
  doesn't require it.
- Not recognizing that "simple and deeply understood" can be a legitimate,
  competitive architectural choice, not just a starting point to grow out of.

## 8. Review Questions
1. What did Stack Overflow's architecture demonstrate about the relationship
   between scale and complexity?
2. Which specific Week 2/3 lessons best explain their approach?
3. Why is restraint itself a mark of architectural maturity?
4. Where might your own platform be over-engineered relative to its actual
   requirements?

## 9. Proficiency Checkpoint
If you can articulate why Stack Overflow's restraint was a deliberate,
defensible architectural choice (not a limitation), you're at Level 4.

## Next
Day 24 covers when NOT to use Redis — directly building on today's restraint
theme.
