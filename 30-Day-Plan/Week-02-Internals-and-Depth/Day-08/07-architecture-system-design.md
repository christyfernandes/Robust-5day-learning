# Day 8: Architecture — Architectural Styles: Monolith, Microservices, Modular Monolith

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Sketch your own data platform's actual service boundaries today, and justify them (or
identify where they're wrong) using bounded-context reasoning.

## 2. Core Concept (basics → advanced)

Three architectural styles for organizing a system's codebase and deployment units:

- **Monolith**: one deployable unit, one codebase, typically one database. Simple to
  develop and deploy early on; coordination between "modules" is just function calls,
  no network involved.
- **Microservices**: many independently deployable services, each typically owning
  its own data store, communicating over the network (often via the event-driven
  patterns from Day 9's Architecture lesson). Enables independent scaling and
  independent team ownership, at the cost of genuine distributed-systems complexity
  (network calls can fail, consistency across services becomes an active design
  problem — Week 1 Day 5's Saga/2PC lesson).
- **Modular monolith**: one deployable unit, but internally organized into strictly
  separated modules with enforced boundaries (no reaching across module boundaries to
  touch another module's internal data) — a deliberate middle path, often recommended
  as the *starting* architecture even for systems that may eventually split into
  microservices.

```
Monolith:              [ Everything, one deployment, shared DB ]

Microservices:         [Service A]──▶[Service B]──▶[Service C]
                        own DB        own DB         own DB
                        (network calls between them)

Modular monolith:       [ Module A | Module B | Module C ]  ← one deployment
                          (enforced boundaries between modules,
                           but still function calls, not network calls)
```

## 3. How It Really Works (Internals)

The real decision driver isn't "microservices are more modern" — it's **bounded
contexts**, a concept from Domain-Driven Design: a bounded context is a boundary within
which a particular domain model (its terms, its rules) applies consistently. Two teams
using the word "order" to mean subtly different things (one meaning a pending cart, one
meaning a fulfilled shipment) are, whether they've noticed it or not, working in
different bounded contexts — and forcing them into one shared data model creates
constant translation friction. **Microservice boundaries should follow bounded-context
boundaries**, not organizational charts or arbitrary technical convenience — splitting
services along the wrong lines (e.g., by technical layer instead of by domain
concept) is a well-documented anti-pattern that reproduces monolith-style coupling,
just now over a slower, less reliable network.

## 4. Architecture & Design Pattern Spotlight

**Pattern: bounded contexts (from Domain-Driven Design) as the actual unit of
architectural decomposition — not "microservices" or "monolith" as ends in
themselves.** Get the bounded contexts right, and either a modular monolith or
microservices can work well; get them wrong, and microservices just distribute the same
tangled coupling a poorly-organized monolith would have had, but now with network
failure modes added on top.

## 5. Hands-On Lab

Sketch your own data platform's actual current service/component boundaries — PySpark
jobs, Kafka topics and their producers/consumers, Flink jobs, the ClickHouse cluster,
any application services around them. For each boundary, ask explicitly: is this a
genuine bounded-context boundary (different teams, different domain vocabulary, could
evolve independently), or is it a boundary that exists for purely technical/historical
reasons? Mark any boundary you're not confident about, and write one sentence on what
evidence would resolve the uncertainty.

## 6. Real-World Product Comparison

- **Shopify** famously runs a large, deliberately-maintained modular monolith (not
  microservices) specifically because their bounded contexts benefit from shared
  transactional guarantees more than from independent deployability — a well-known,
  intentional counter-example to "microservices by default."
- **Netflix** is the canonical large-scale microservices example, but their split was
  driven by genuinely independent team ownership and scaling needs across very
  distinct bounded contexts (recommendations, billing, streaming delivery) — not
  microservices as a goal unto itself.

## 7. Common Production Pitfalls

- Adopting microservices primarily because it's perceived as the modern default,
  without first identifying genuine bounded-context boundaries to split along.
- Splitting services along technical layers (e.g., a separate "database service," a
  separate "business logic service") rather than domain boundaries — this pattern
  (sometimes called a "distributed monolith") gets all of microservices' network
  complexity with none of the independent-deployability benefit.
- Underestimating the operational cost increase (deployment, monitoring, debugging
  across service boundaries) when splitting a monolith, relative to the actual
  organizational/scaling benefit gained.

## 8. Review Questions
1. What's a bounded context, and why should it drive service boundaries rather than
   org charts or technical convenience?
2. Why is a "distributed monolith" considered worse than either a true monolith or true
   microservices?
3. Why might a modular monolith be the *right* long-term choice for some systems, not
   just a stepping stone?
4. What's one piece of evidence that would tell you a given service boundary is
   correctly drawn?

## 9. Proficiency Checkpoint
If you can sketch your own platform's boundaries and justify each one using
bounded-context reasoning (not just "that's how it's always been"), you're at Level 3.

## Next
Day 9 covers event-driven patterns — choreography vs. orchestration — the
communication style that connects whatever boundaries you just sketched.
