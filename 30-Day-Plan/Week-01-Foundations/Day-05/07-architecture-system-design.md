# Day 5: Architecture — Distributed Transactions: 2PC, Saga, Outbox

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain why two-phase commit doesn't scale well for microservices, and design a Saga
with compensating actions for a realistic multi-step business operation.

## 2. Core Concept (basics → advanced)

Once "one operation" spans multiple independent services/databases (e.g., "place an
order" touches inventory, payment, and shipping), you need a way to keep them
consistent without a single database transaction to rely on.

- **Two-Phase Commit (2PC)**: a coordinator asks every participant to **prepare**
  (lock resources, confirm it *can* commit), waits for all to agree, then tells everyone
  to **commit**. Strongly consistent — but every participant holds locks for the entire
  duration of the coordinator round-trip, and if the coordinator or any participant
  fails mid-protocol, the whole thing can block indefinitely (a real, well-known
  availability problem, not a hypothetical one).
- **Saga**: break the operation into a sequence of local transactions, each with a
  predefined **compensating action** to undo it if a later step fails. No distributed
  locks — each local transaction commits independently and immediately; failure is
  handled by explicitly running compensations backward through completed steps.
- **Outbox pattern**: solves a narrower but critical problem — atomically committing a
  local database change *and* reliably publishing an event about it (e.g., to Kafka),
  without a distributed transaction. Write the event to an "outbox" table in the *same*
  local transaction as the business change, then a separate process reads the outbox
  and publishes to Kafka, guaranteeing the event is never lost even if the publish step
  crashes right after the local commit.

```
2PC:      Coordinator ──prepare──▶ Inventory, Payment, Shipping (all lock & wait)
                       ◄──ready───
                       ──commit──▶ (all commit together, locks held the whole time)

Saga:     Reserve Inventory (commits immediately)
              │ success
              ▼
          Charge Payment (commits immediately)
              │ FAILS
              ▼
          Compensate: Release Inventory Reservation (undo step 1)
```

## 3. How It Really Works (Internals)

2PC's core problem is the **blocking window**: between "prepare" and "commit," every
participant holds locks on the relevant resources, and if the coordinator crashes in
that window, participants don't know whether to commit or abort — they're stuck holding
locks until the coordinator recovers (this is a formally known limitation, not a
implementation bug — 2PC is provably blocking under coordinator failure).

Sagas trade that away entirely: no distributed locks, ever — but at the cost of giving
up atomicity in the traditional sense. Between "reserve inventory" committing and
"charge payment" being attempted, the system is in a genuinely **intermediate state**
(inventory reserved, payment not yet charged) that other parts of the system might
observe. This is why Saga-based systems need to be designed with intermediate states in
mind from the start (e.g., "reserved" as a distinct, visible inventory state, not just
"available" or "sold") — it's a real design responsibility Saga shifts onto you that 2PC
would have hidden (at the cost of availability).

## 4. Architecture & Design Pattern Spotlight

**Pattern: coordinating distributed state without global locks, via compensating
actions instead of rollback.** This is the dominant pattern in modern event-driven
microservice architectures precisely because it avoids 2PC's blocking-under-failure
problem — and it composes naturally with Kafka as the event backbone connecting each
local-transaction step, with the Outbox pattern ensuring each step's "I did my part,
here's the event" is never lost even across a crash.

## 5. Hands-On Lab

Sketch a Saga for a realistic order-processing flow with 3 steps: reserve inventory →
charge payment → schedule shipment. For each step, write down:
- What's the compensating action if a *later* step fails?
- What intermediate state does the system need to expose while the Saga is in progress
  (e.g., what does the customer see if inventory is reserved but payment hasn't been
  attempted yet)?
- Where would you use the Outbox pattern to make sure "inventory reserved" reliably
  produces a Kafka event even if the service crashes immediately after committing that
  local change?

## 6. Real-World Product Comparison

- **Kafka-backed microservice architectures** (a common pattern at companies like
  Uber and Netflix) lean heavily on Saga + Outbox specifically because 2PC across
  independently-owned, independently-scaled services is both an availability risk and
  an organizational one (every participant needs to agree to hold locks for another
  team's coordinator).
- 2PC still shows up **within** a single database's internals (e.g., distributed SQL
  systems like Spanner use variants of it under the hood, with additional mechanisms to
  bound the blocking problem) — it's not "wrong," just a poor fit for loosely-coupled,
  independently-deployed services.

## 7. Common Production Pitfalls

- Choosing 2PC for a cross-microservice operation "for simplicity," without accounting
  for the availability cost of participant lock-holding under partial failure.
- Designing a Saga without actually implementing (or testing) the compensating actions —
  the failure path is exactly the part that doesn't get exercised by normal happy-path
  testing, and is exactly where Saga-based systems most often break in production.
- Forgetting the Outbox pattern and instead publishing an event directly after a local
  commit in application code — a crash between the commit and the publish silently
  loses the event, with no way to know it happened.

## 8. Review Questions
1. Why is 2PC's blocking window a fundamental limitation, not an implementation detail?
2. What does a Saga give up, compared to 2PC, and what does it gain?
3. What specific problem does the Outbox pattern solve that a Saga alone doesn't?
4. Why must intermediate states be a deliberate design decision in a Saga-based system?

## 9. Proficiency Checkpoint
If you can design a Saga with real compensating actions and correctly place an Outbox
where it's needed, you're at Level 2 moving solidly into Level 3 architectural thinking.

## Next
Day 6 shifts from cross-service transactions to caching architecture — CDN layers,
invalidation, and mapping your own MDO portal's cache hierarchy end to end.
