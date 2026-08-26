# Topic-Day File Template

Every full lesson file (one track, one day — e.g. `Day-01/03-flink.md`) follows this
exact structure. Use it to write new days yourself, or hand this file to Claude and
say "write Day N for [track] following DAY_TEMPLATE.md" to generate it in the same
style as the rest of the curriculum.

**Revision note (v2):** this template was updated after finishing a full first pass
of Day 1, based on direct feedback from actually studying it: the original version
under-served true beginners, labs were unverifiable without a working local
environment, review questions had no answers, and proficiency checkpoints didn't
summarize what they were actually testing. The structure below fixes all four. Every
lesson file in this repo is being revised to match it.

```markdown
# Day N: <Track> — <Topic Title>

## Time: ~25-30 min | Track proficiency target for this day: Level X

## 1. Learning Objective
One or two sentences: what you should be able to *do* after this, not just "understand."

## 2. Core Concept (basics → advanced)
Start genuinely at the beginner level — define every piece of jargon the FIRST time
it's used, in plain language, before using it technically. Don't assume the reader
already knows what a "partition," "broker," or "shard" is just because they're a
senior engineer in a different domain. Then build up to the deeper explanation. A
reader new to this specific tool should be able to follow the whole section start to
finish without getting stuck on an undefined term. Use a diagram (ASCII is fine) if
it's spatial/structural.

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
over toy examples where possible. Immediately follow the code with:

### Sample Output
A realistic, accurate rendering of what running this actually produces — a console
log, a UI table, an API response, a CLI output — formatted exactly as the real tool
would format it. **Write this from documented, known tool behavior; do not guess.**
Then explain it piece by piece (line-by-line, row-by-row, or block-by-block,
whichever fits the output shape), tying each part back to the concept taught above —
e.g., for a Spark stages table: which row is the shuffle boundary, and how do you
know from the columns shown. The goal is that someone who can't get the tool running
locally still learns exactly what they'd see if they could, and someone who *can* get
it running has a known-correct reference to check their own output against.

## 6. Real-World Product Comparison
Name 2–3 real products/companies. What they chose, roughly why, and one concrete
trade-off — not just "X is faster." Pull from `PRODUCT_COMPARISON_MATRIX.md` and add
the specific angle for this topic.

## 7. Common Production Pitfalls
2–4 mistakes people actually hit, ideally including the kind you've hit in your own
production systems.

## 8. Review Questions
3–5 questions you should be able to answer out loud without notes. Each question is
immediately followed by its answer inside a collapsible block:

1. Question text?
<details><summary>Show answer</summary>

Concise, correct, complete-enough-to-be-useful answer. Not just a one-liner if the
question genuinely needs more — but no padding either.

</details>

## 9. Proficiency Checkpoint
Open with a **Quick Recap** — a dense, bullet-point summary of the specific facts the
checkpoint statement is testing, written so it works as standalone flash-card-style
review material (someone should be able to read only this bullet list, days later,
and have the day's core content refreshed). Then the checkpoint statement itself:
"If you can do X, you're at Level Y on this specific topic."

## Next
One line connecting to tomorrow's topic in this track.
```

## Notes on tone
- Assume senior engineering background (11+ years) for judgment and system-design
  maturity, but NOT prior exposure to this specific tool — define this tool's own
  vocabulary from scratch every time, even for a reader who's an expert elsewhere.
  Skip "what is a variable"-level explanation; don't skip "what does this tool call
  a partition, and why."
- Prefer specificity over breadth: one well-explained internal mechanism beats five
  shallow bullet points.
- Where a topic maps to a real, current production issue (see `CURRICULUM.md` §6),
  say so explicitly and lean into it — the lab should produce something reusable at
  work, not just a learning artifact.
- Sample outputs and review-question answers must be technically accurate to the
  real tool's actual behavior — when genuinely uncertain what a specific version's
  output looks like, phrase it as "this is what you should expect to see" rather than
  asserting an exact byte-for-byte format you're not sure of.
