# Day 15: Architecture — Scalability Patterns: Load Balancing & Stateless Design

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Identify which of your platform's components are stateless vs. stateful, and explain
what that distinction implies for how each can be scaled.

## 2. Core Concept (basics → advanced)

**Stateless services** hold no data between requests that isn't either passed in by
the caller or fetched fresh from a separate data store — any instance can handle any
request, making horizontal scaling trivial: add more identical instances behind a
load balancer, and capacity increases linearly with no coordination needed between
instances. **Stateful services** (a database, a Flink job's keyed state, Week 1 Day
5) hold data that's tied to a *specific* instance — scaling requires either
partitioning that state across instances (sharding, Week 1 Days 3-4) or replicating
it (Week 1 Day 4-5), both of which are meaningfully more complex than "just add more
identical copies."

Common **load-balancing algorithms** for distributing requests across stateless
instances:
- **Round-robin**: cycle through instances in order — simple, works well when
  requests are roughly uniform in cost.
- **Least-connections**: route to the instance with the fewest active connections —
  better when request cost varies significantly.
- **Consistent-hash-based**: route based on a hash of some request attribute (e.g., a
  session ID) — used when you *want* a specific client's requests to consistently hit
  the same instance (e.g., for in-memory session caching), directly reusing the
  consistent-hashing pattern from Week 1, Day 3.

## 3. How It Really Works (Internals)

The entire "just add more instances" scaling story for stateless services depends on
truly holding no meaningful state locally — a service that's *supposed* to be
stateless but accidentally caches something in local memory that affects request
handling (a classic, subtle bug) breaks the "any instance can handle any request"
assumption silently, often surfacing only under load-balanced traffic patterns that
happen to route a client's related requests to different instances inconsistently.

Recognizing which of your own platform's components are genuinely stateless (an API
gateway, a stateless request-handling service) versus genuinely stateful (Kafka
brokers holding partition data, a Flink job's keyed state, ClickHouse nodes holding
MergeTree parts) is the practical first step in reasoning about how each would
actually need to scale — a stateless component's scaling story is "add instances
behind a load balancer"; a stateful component's scaling story requires revisiting
this month's specific sharding/replication mechanisms for that particular system.

## 4. Architecture & Design Pattern Spotlight

**Pattern: horizontal scaling prerequisites — statelessness as the property that
makes "just add more instances" actually work.** This reframes nearly every
scaling mechanism studied this month (Kafka partitions, ClickHouse shards, Flink's
keyed state and rescaling, Week 2 Day 13) as different systems' answers to "how do
you scale something that, unlike a stateless service, can't simply be duplicated
without coordination."

## 5. Hands-On Lab

List every major component in your own data platform (PySpark jobs, Kafka brokers,
Flink jobs, Redis, Elasticsearch, ClickHouse, any application/API services around
them) and classify each as stateless or stateful. For each **stateful** component,
name the specific mechanism (from earlier this month) that actually enables it to
scale (e.g., "Kafka scales via partitioning across brokers, Week 1 Day 3"; "ClickHouse
scales via sharding key selection, Week 1 Day 4"). For each **stateless** component,
confirm there's no accidental hidden local state that would break the "any instance
can handle any request" assumption.

## 6. Real-World Product Comparison

- **API gateways and stateless web services** at any scale (a canonical example
  across the industry) rely entirely on this pattern — the ability to autoscale them
  trivially is precisely why architects work hard to keep as much of a system
  stateless as the actual requirements allow.
- Contrast directly with **Kafka, ClickHouse, and Flink** — three genuinely stateful
  systems studied deeply this month, each requiring its own specific scaling mechanism
  rather than benefiting from simple load-balanced duplication.

## 7. Common Production Pitfalls

- Assuming a service is stateless without verifying it — subtle local caching or
  in-memory session state can silently break the stateless-scaling assumption under
  real load-balanced traffic.
- Choosing a load-balancing algorithm mismatched to actual request-cost variance —
  round-robin under highly variable request costs can leave some instances
  overloaded while others sit idle.
- Treating a genuinely stateful component's scaling as "just add more instances,"
  without applying the specific sharding/replication reasoning that component
  actually requires.

## 8. Review Questions
1. Why does statelessness make horizontal scaling structurally simple?
2. What's the risk of a service being "accidentally" stateful?
3. When would consistent-hash-based load balancing be preferred over round-robin?
4. Why do Kafka, ClickHouse, and Flink each need a genuinely different scaling
   mechanism rather than one generic answer?

## 9. Proficiency Checkpoint
If you can classify your own platform's components correctly and name the specific
scaling mechanism each stateful one relies on, you're at Level 3.5.

## Next
Day 16 covers SLIs/SLOs/error budgets and cell-based architecture — the reliability-
engineering framework for reasoning about acceptable failure rates across whatever
you've just classified.
