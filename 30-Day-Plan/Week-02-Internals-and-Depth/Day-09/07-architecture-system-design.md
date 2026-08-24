# Day 9: Architecture — Event-Driven Patterns: Choreography vs. Orchestration

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Classify your own Sunbird telemetry pipeline's event style against three event-driven
patterns, and explain the choreography-vs-orchestration trade-off.

## 2. Core Concept (basics → advanced)

Three distinct ways services can use events to communicate, often conflated but worth
distinguishing precisely:

- **Event notification**: "something happened" — a minimal event (e.g., `OrderPlaced
  {order_id: 123}`), and any interested service must call back to fetch full details if
  it needs them. Small events, but couples consumers to the producer's API for detail
  lookups.
- **Event-carried state transfer**: the event itself carries the full relevant state
  (e.g., `OrderPlaced {order_id: 123, items: [...], customer: {...}, total: 99.50}`) —
  consumers don't need to call back at all, at the cost of larger events and needing to
  keep the event schema in sync with whatever data consumers actually need.
- **Event sourcing**: the events themselves **are** the system of record — current
  state is derived by replaying the full event history, not stored as a separate
  mutable table at all. This is a much bigger architectural commitment than the first
  two (which are just messaging styles layered on top of however state is normally
  stored).

Separately, **choreography vs. orchestration** describes *how a multi-step process is
coordinated*:
- **Choreography**: each service reacts to events independently; there's no central
  coordinator — the overall process emerges from each service's local reactions
  (this is how a Saga, Week 1 Day 5, is often implemented).
- **Orchestration**: a central coordinator explicitly calls each step in sequence and
  tracks overall process state — easier to observe/debug the full process as a single
  place, at the cost of that coordinator becoming a more central, more coupled
  component.

## 3. How It Really Works (Internals)

Choreography's core trade-off: no single service needs to know about the whole
process, which maximizes decoupling — but that same property means **the overall
process itself becomes hard to see anywhere** — understanding "what happens when an
order is placed" requires tracing through every service's independent event handlers,
often across a codebase (or several codebases) no one person owns end to end.
Orchestration inverts this: a coordinator service explicitly encodes the whole
process, trivially observable and debuggable in one place — at the cost of that
coordinator needing to know about (and often directly call) every participant, a real
coupling point.

Neither is universally "better" — the actual decision hinges on process complexity
and change frequency: simple, rarely-changing flows often favor choreography's
decoupling; complex, frequently-evolving, or heavily-audited processes (where "what
exactly happened, in what order" needs to be centrally traceable) usually favor
orchestration.

## 4. Architecture & Design Pattern Spotlight

**Pattern: choreography vs. orchestration as a process-coordination spectrum, layered
on top of whichever event style (notification, state-transfer, or sourcing) a system
uses for the underlying messages.** These are genuinely two separate design axes
(what the events contain, vs. how the overall process is coordinated) — worth
analyzing independently rather than treating "event-driven architecture" as one
undifferentiated choice.

## 5. Hands-On Lab

Classify the Sunbird telemetry pipeline you've documented (Flink jobs, Kafka routing,
Redis dedup, Druid storage) against both axes:
- **Event style**: do the Kafka messages in this pipeline function more like
  notifications (minimal, requiring lookups), full state-transfer events (self-
  contained), or is there any genuine event-sourcing (state reconstructed by replaying
  history) happening anywhere in it?
- **Coordination style**: is the overall telemetry flow choreographed (each stage
  reacts independently to the stage before it) or orchestrated (something explicitly
  sequences the stages)? Would the opposite style have made this pipeline easier or
  harder to build and debug?

## 6. Real-World Product Comparison

- **Netflix's** microservice ecosystem uses both styles deliberately depending on
  process complexity — simpler event reactions favor choreography; complex,
  multi-step, heavily-monitored business processes (like a full account signup flow)
  more often use explicit orchestration for traceability.
- **Event sourcing** as a full architectural commitment is less common than the other
  two styles specifically because of its cost (replaying full history to derive
  current state, snapshotting strategies needed at scale) — but it's the natural fit
  when a complete, provable audit trail is itself a requirement, not just a nice-to-have.

## 7. Common Production Pitfalls

- Choosing choreography for a genuinely complex, frequently-changing business process,
  then struggling to answer "what actually happens, end to end" without a coordinator
  anywhere to look at.
- Choosing orchestration for a simple, rarely-changing reaction chain, adding
  unnecessary central coupling and a single point of failure/bottleneck for something
  that didn't need central coordination at all.
- Conflating "event-driven" with "event sourcing" — most event-driven systems use
  event notification or state-transfer, with state stored conventionally elsewhere;
  true event sourcing is a much rarer, heavier commitment.

## 8. Review Questions
1. What's the practical difference between event notification and event-carried state
   transfer?
2. Why does event sourcing represent a fundamentally bigger commitment than the other
   two event styles?
3. What does choreography optimize for, and what does it make harder to see?
4. When would orchestration's central coupling be worth its debuggability benefit?

## 9. Proficiency Checkpoint
If you can classify a real pipeline against both the event-style and coordination-style
axes, and justify whether the chosen style fits the process's actual complexity, you're
at Level 3.

## Next
Day 10 covers log compaction and Redis Cluster's hash slots — two more concrete
mechanisms behind the event backbones you've now analyzed architecturally.
