# Day 25: Flink — Redesign Your Sunbird Flink Jobs

## Time: ~30 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Redesign your Sunbird Flink jobs with proper bounded/unbounded source handling
and checkpointing discipline, applying Week 1-2's depth directly.

## 2. Core Concept (basics → advanced)

Your real JobManager-instability investigation this month (Week 2, Day 10)
traced back to bounded-vs-unbounded source misconfiguration — worth an
explicit, systematic audit: for **every** Flink job in your Sunbird pipeline
(not just the one you already fixed), confirm source configuration matches
intended execution mode (Week 2, Day 10), checkpointing is enabled with
appropriate interval and alignment/unaligned configuration (Week 1, Day 6;
Week 3, Day 16), and state backend/serialization choices (Week 1, Day 5; Week
3, Day 15) are deliberate rather than default.

## 3. How It Really Works (Internals)

This audit is worth treating as a checklist applied uniformly across every
Sunbird Flink job, precisely because the bounded-source bug you found once is
a configuration-copying risk — if one job's source configuration was copied
from another (a common practice), the same misconfiguration could exist
elsewhere in the pipeline without having yet caused a visible incident. This
is exactly the "fix it once, then check everywhere else" discipline any real
incident response should include (Week 3, Day 21's postmortem template
explicitly includes a "prevention" section for this reason).

## 4. Architecture & Design Pattern Spotlight

**Pattern: systematic configuration audit after a real incident — checking
every instance of a pattern that caused one confirmed failure, not just the
specific instance that already broke.**

## 5. Hands-On Lab

List every Flink job in your Sunbird pipeline. For each, verify explicitly:
source boundedness configuration (Week 2, Day 10), checkpointing interval and
alignment mode (Week 1, Day 6; Week 3, Day 16), and state backend choice
(Week 1, Day 5). Flag any job whose configuration you can't confidently
verify without checking the actual code/config — that's your prioritized
follow-up list.

## 6. Real-World Product Comparison

This is your own real pipeline audit.

## 7. Common Production Pitfalls

- Fixing the one job that caused a visible incident without auditing sibling
  jobs that may share the same root-cause configuration pattern.
- Treating this audit as a one-time exercise rather than adding it to a
  standard pre-deployment checklist (Week 3, Day 21's runbook-building
  discipline) going forward.

## 8. Review Questions
1. Why is auditing every Flink job important, not just the one that already
   failed?
2. What three specific configuration dimensions does this audit check?
3. What would you add to a standard deployment checklist based on this
   audit?
4. Which job (if any) did this audit flag as needing further verification?

## 9. Proficiency Checkpoint
If you've completed a real, systematic audit across your actual Flink jobs,
you're at Level 4 — this is directly preventive, high-value production work.

## Next
This feeds into today's ClickHouse and Architecture lessons — the MDO portal
migration design itself.
