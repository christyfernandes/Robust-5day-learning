# Topic-Day File Template

Every full lesson file (one track, one day — e.g. `Day-01/03-flink.md`) follows this
exact structure. Use it to write Days 3–30 yourself, or hand this file to Claude and
say "write Day N for [track] following DAY_TEMPLATE.md" to generate it in the same
style as Day 1–2.

```markdown
# Day N: <Track> — <Topic Title>

## Time: ~25 min | Track proficiency target for this day: Level X

## 1. Learning Objective
One or two sentences: what you should be able to *do* after this, not just "understand."

## 2. Core Concept (basics → advanced)
The idea, explained plainly first, then pushed one level deeper than a typical
tutorial would go. Use a diagram (ASCII is fine) if it's spatial/structural.

## 3. How It Really Works (Internals)
The mechanism underneath the API — this is the part most tutorials skip and the part
that separates Level 2 from Level 3+. E.g., not just "Kafka has replication" but ISR,
leader election, and what min.insync.replicas actually enforces.

## 4. Architecture & Design Pattern Spotlight
Name the reusable pattern this concept is an instance of (e.g., "leader-follower
replication," "sparse index," "log-structured storage," "CQRS"). Cross-reference where
else in the curriculum the same pattern shows up.

## 5. Hands-On Lab
A concrete, runnable exercise. Prefer scenarios shaped like real production problems
over toy examples where possible.

## 6. Real-World Product Comparison
Name 2–3 real products/companies. What they chose, roughly why, and one concrete
trade-off — not just "X is faster." Pull from `PRODUCT_COMPARISON_MATRIX.md` and add
the specific angle for this topic.

## 7. Common Production Pitfalls
2–4 mistakes people actually hit, ideally including the kind you've hit in your own
production systems.

## 8. Review Questions
3–5 questions you should be able to answer out loud without notes.

## 9. Proficiency Checkpoint
A one-line "if you can do X, you're at Level Y on this specific topic" gut check.

## Next
One line connecting to tomorrow's topic in this track.
```

## Notes on tone
- Assume senior engineering background (11+ years) — skip "what is a variable"-level
  explanation, don't skip "what is the actual algorithm/mechanism."
- Prefer specificity over breadth: one well-explained internal mechanism beats five
  shallow bullet points.
- Where a topic maps to a real, current production issue (see `CURRICULUM.md` §6),
  say so explicitly and lean into it — the lab should produce something reusable at
  work, not just a learning artifact.
