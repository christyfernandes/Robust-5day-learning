# Day 6: Kafka — Schema Registry & Compatibility

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Evolve an Avro schema by adding an optional field, and correctly predict which
compatibility mode would accept or reject that change.

## 2. Core Concept (basics → advanced)

Kafka itself has no opinion about message format — it stores bytes. **Schema
Registry** (Confluent's, or an open-source equivalent) adds a governance layer on top:
producers register a schema (commonly Avro, sometimes Protobuf or JSON Schema) for each
topic, and the registry enforces **compatibility rules** whenever a new schema version
is registered, preventing a producer's schema change from silently breaking existing
consumers.

Compatibility modes (the actual governance policy you configure per subject):
- **Backward**: new schema can read data written with the *previous* schema (consumers
  upgrade first, safely). Adding an optional field with a default is the classic
  backward-compatible change.
- **Forward**: data written with the *new* schema can be read by consumers still using
  the *previous* schema (producers upgrade first, safely).
- **Full**: both backward and forward — the strictest, safest, and most restrictive mode.

```
Backward-compatible change:           Breaking change:
  v1: {name, email}                    v1: {name, email}
  v2: {name, email, phone=null}        v2: {name}          ← removed a required field
  (old consumers ignore new field,     (old consumers expecting "email" will fail
   new consumers get a default          when reading v2 data — REJECTED under
   for old data — ACCEPTED)             backward compatibility)
```

## 3. How It Really Works (Internals)

The registry stores schemas per **subject** (typically `<topic>-value` or
`<topic>-key`), versioned, and checks every new registration against the compatibility
rule configured for that subject — this check happens at **registration time**, not at
produce/consume time, so an incompatible schema is rejected before it ever reaches
Kafka, rather than causing a runtime deserialization failure discovered later by some
downstream consumer.

Avro's actual compatibility mechanics rely on **schema resolution**: a consumer reads
data using its own (possibly different) schema than the one it was written with, and
Avro's resolution rules define exactly what's allowed (adding a field requires a
default value so old data resolves cleanly; removing a required field breaks resolution
for anyone still expecting it; changing a field's type is only allowed between
compatible type pairs, like `int` → `long`).

## 4. Architecture & Design Pattern Spotlight

**Pattern: contract-first schema evolution — the same governance problem as API
versioning, solved with an explicit, enforced contract instead of ad hoc coordination
between teams.** This is directly analogous to Protobuf/gRPC's own field-numbering and
`reserved` keyword discipline for safe API evolution, or a REST API's versioning
strategy — different transport, same underlying discipline: never let a producer's
change silently break a consumer that hasn't (or can't) upgrade in lockstep.

## 5. Hands-On Lab

```json
// v1 schema
{"type": "record", "name": "Order", "fields": [
  {"name": "order_id", "type": "string"},
  {"name": "amount", "type": "double"}
]}

// v2 schema — attempt to add a field
{"type": "record", "name": "Order", "fields": [
  {"name": "order_id", "type": "string"},
  {"name": "amount", "type": "double"},
  {"name": "currency", "type": "string", "default": "USD"}
]}
```
Register v1, set the subject's compatibility mode to `BACKWARD`, then attempt to
register v2 — it should succeed (default value makes it safe). Now try a v3 that
*removes* `amount` entirely — registration should be **rejected**. Check the registry's
error message and confirm it explains the specific incompatibility.

## 6. Real-World Product Comparison

- **Confluent Schema Registry** is the reference implementation most production Kafka
  deployments use; **Protobuf** (often paired with gRPC for service-to-service APIs)
  handles the same evolution problem via field numbers and `reserved` fields rather than
  a centralized registry service — a decentralized version of the same discipline.
- This governance problem recurs directly in your work: any team consuming Kafka
  topics you own faces the same "can I change this schema safely" question that
  Schema Registry formalizes — worth having this framework in mind even for topics
  without a registry currently enforcing it.

## 7. Common Production Pitfalls

- Registering a schema change without setting (or checking) the subject's compatibility
  mode — by default, some registries are permissive, silently allowing changes that
  would break existing consumers.
- Removing a field without a transition period (deprecate first, remove later) — even
  under `FULL` compatibility mode enforcement, downstream consumers still need real time
  to migrate off a field they depend on.
- Not distinguishing "the registry accepted my schema" from "every consumer has actually
  deployed code that handles it" — compatibility-mode enforcement is a safety net, not a
  substitute for coordinating actual consumer deployments.

## 8. Review Questions
1. What's the practical difference between backward and forward compatibility?
2. Why does adding a field require a default value to be backward-compatible?
3. At what point in the produce/consume flow does compatibility checking actually happen?
4. How is Schema Registry's role analogous to Protobuf's field-numbering discipline?

## 9. Proficiency Checkpoint
If you can predict whether a given schema change would pass under backward, forward, or
full compatibility mode without testing it, you're at Level 2 moving into Level 3.

## Next
Day 7 combines everything from this week into one lab session — including standing up
a real multi-service pipeline and writing your first ADR.
