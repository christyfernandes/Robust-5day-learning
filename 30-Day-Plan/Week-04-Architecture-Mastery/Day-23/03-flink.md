# Day 23: Flink — Case Studies: Alibaba (Blink), Uber, Stripe

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Extract one concrete takeaway from Alibaba's, Uber's, and Stripe's public Flink
usage.

## 2. Core Concept (basics → advanced)

- **Alibaba (Blink)**: Alibaba built and open-sourced significant enhancements
  to Flink (known as Blink) specifically for their own massive-scale real-time
  computation needs (notably around events like Singles' Day), later
  contributing much of this work back to mainline Flink — a strong case study
  in pushing a stream-processing engine to genuinely extreme scale, including
  state-backend (Week 1, Day 5) and checkpointing (Week 1, Day 6) optimizations.
- **Uber**: extensively documented Flink usage for real-time pricing, fraud
  detection, and ETA computation — concrete, production discussions of exactly-
  once sinks (Week 2, Day 9), CEP-adjacent pattern detection (Week 2, Day 12),
  and deployment-mode choices (Week 3, Day 19).
- **Stripe**: uses Flink for real-time financial data processing, where
  correctness guarantees (exactly-once semantics, checkpointing reliability) are
  not just performance nice-to-haves but genuine financial-correctness
  requirements — a strong case study in what "correctness actually matters"
  looks like in production.

## 3. How It Really Works (Internals)

Stripe's case is worth specific attention: in a financial-processing context, a
duplicate or lost event isn't a minor inconvenience — it can mean an incorrect
charge or a missed one. This makes their public discussions of Flink's exactly-
once mechanisms (Week 2, Day 9) unusually concrete about *why* these guarantees
matter, beyond an abstract "correctness is good" framing — a useful lens for
evaluating whether your own use cases have genuinely Stripe-like correctness
stakes, or more Netflix-recommendation-like tolerance for occasional
imperfection.

## 4. Architecture & Design Pattern Spotlight

**Pattern: case-study literacy, applied to Flink** — with Stripe specifically
illustrating how correctness-guarantee stakes (not just scale) should drive
architectural rigor.

## 5. Hands-On Lab

Read a primary source from each of Alibaba/Blink, Uber, and Stripe covering
Flink usage. For Stripe specifically, identify: what specific correctness
guarantee (from Week 2, Day 9's exactly-once lesson) is load-bearing for their
use case, and what would the concrete business consequence be if that guarantee
failed?

## 6. Real-World Product Comparison

This lesson *is* the comparison exercise.

## 7. Common Production Pitfalls

- Assuming every use case has Stripe-like correctness stakes, over-engineering
  exactly-once guarantees where at-least-once with idempotent downstream
  handling would suffice at much lower complexity cost.
- Assuming Alibaba-scale optimizations (Blink's contributions) are necessary
  for your own, likely much smaller, scale.
- Not distinguishing "this company operates at extreme scale" from "this
  company's specific correctness requirements are extreme" — these are
  independent dimensions worth assessing separately for your own use case.

## 8. Review Questions
1. What motivated Alibaba's Blink enhancements to Flink?
2. Why does Stripe's use case make exactly-once semantics a genuine business
   requirement, not just a nice-to-have?
3. What's the difference between scale-driven and correctness-driven
   architectural rigor?
4. Where does your own use case sit on this spectrum?

## 9. Proficiency Checkpoint
If you can correctly place your own use case on the scale-vs-correctness-stakes
spectrum using these real examples, you're at Level 4.

## Next
Day 24 covers when NOT to use Flink.
