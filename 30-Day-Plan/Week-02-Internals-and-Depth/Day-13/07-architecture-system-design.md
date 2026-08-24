# Day 13: Architecture — Resilience Patterns: Circuit Breaker, Bulkhead, Retry

## Time: ~25 min | Track proficiency target for this day: Level 3

## 1. Learning Objective
Sketch a circuit breaker for a call from your pipeline to an external/flaky
dependency, and explain how it composes with bulkhead isolation and retry-with-backoff.

## 2. Core Concept (basics → advanced)

Three complementary patterns for surviving a flaky or overloaded dependency without
that dependency's problems cascading into your own system's failure:

- **Retry with backoff + jitter**: on a failed call, retry after a delay that grows
  with each attempt (backoff — avoiding hammering an already-struggling dependency
  immediately again) and includes **randomization** (jitter — preventing many clients
  from retrying in lockstep at the exact same moment, which would itself create a
  synchronized load spike against the recovering dependency).
- **Circuit breaker**: tracks recent failure rate for a given dependency; once
  failures exceed a threshold, the breaker "opens" and *stops attempting calls
  entirely* for a cooldown period (failing fast instead), then periodically allows a
  small number of test calls through ("half-open" state) to check if the dependency
  has recovered before fully resuming normal traffic.
- **Bulkhead**: isolates resources (thread pools, connection pools) per dependency, so
  that one slow/failing dependency exhausting its own allocated resources doesn't
  starve resources needed for calls to *other*, healthy dependencies — named after
  a ship's bulkheads, which contain flooding to one compartment rather than sinking
  the whole vessel.

```
Retry+backoff+jitter:  fail → wait ~1s±jitter → fail → wait ~2s±jitter → fail → wait ~4s±jitter
                       (spread out, not synchronized, growing delay)

Circuit breaker:       CLOSED (normal) → failures exceed threshold → OPEN (fail fast,
                       no calls attempted) → cooldown → HALF-OPEN (test a few calls)
                       → CLOSED again (if healthy) or back to OPEN (if still failing)

Bulkhead:              [Dependency A's own thread pool] [Dependency B's own thread pool]
                       (A exhausting its pool doesn't affect B's calls at all)
```

## 3. How It Really Works (Internals)

These three patterns solve genuinely different failure dynamics and compose together
rather than substituting for each other: retry-with-backoff handles **transient**
failures (a brief network blip) gracefully; the circuit breaker handles **sustained**
failures by stopping wasted effort (retrying against a dependency that's clearly down
for an extended period just adds load to an already-struggling system and delays your
own system noticing and reacting); bulkhead prevents a **single dependency's**
resource exhaustion from becoming a **whole-system** resource exhaustion. A
well-designed resilient call typically layers all three: bulkhead-isolated resources,
retry with backoff+jitter for transient issues within that isolated pool, and a
circuit breaker wrapping the whole thing to stop attempting calls entirely once it's
clear the dependency is sustainedly unhealthy.

## 4. Architecture & Design Pattern Spotlight

**Pattern: fault isolation and graceful degradation — treating dependency failure as
an expected, designed-for condition rather than an exceptional edge case.** This
mindset — assume dependencies *will* fail, design explicitly for it — is the same
underlying philosophy behind Kafka's ISR/replication (surviving broker failure,
Week 1 Day 4), Sentinel/Cluster failover (Week 2, Day 9-10), and Raft consensus
generally (Week 1, Day 4): resilient distributed systems are built by explicitly
designing for the failure of their own components and dependencies, not by hoping
failures don't happen.

## 5. Hands-On Lab

Sketch (pseudocode or a diagram) a resilient call from one of your own pipeline
components to a flaky or occasionally-slow external dependency (a third-party API, an
external database, or even a downstream internal service known to have occasional
issues). Specify explicitly:
- What retry policy (max attempts, backoff base, jitter range) fits this dependency's
  known failure characteristics?
- What circuit-breaker thresholds (failure rate, cooldown duration) make sense given
  how quickly this dependency typically recovers when it does fail?
- Does this call share a thread/connection pool with calls to other dependencies
  today, and would bulkhead isolation meaningfully reduce blast radius if it started
  failing?

## 6. Real-World Product Comparison

- **Netflix's Hystrix** (now largely superseded by Resilience4j and similar
  libraries, but historically influential) popularized circuit breaker and bulkhead
  patterns specifically for large-scale microservice architectures where any single
  service call failing shouldn't be allowed to cascade into a broader outage.
- Cloud SDKs (AWS SDK, GCP client libraries) build retry-with-backoff-and-jitter in by
  default for exactly the reasons described above — a well-known, standard practice
  for any client calling a remote, potentially-rate-limited or occasionally-degraded
  service.

## 7. Common Production Pitfalls

- Implementing retry without jitter — synchronized retries across many clients can
  create a "thundering herd" load spike against a dependency that's just starting to
  recover, potentially knocking it back down.
- Setting circuit-breaker thresholds without real data on the dependency's actual
  failure/recovery patterns — an arbitrary threshold can either trip far too
  eagerly (unnecessarily blocking calls that would have succeeded) or far too
  reluctantly (continuing to hammer a genuinely failing dependency for too long).
- Sharing resource pools across dependencies with very different reliability
  profiles — without bulkhead isolation, one consistently flaky dependency can starve
  resources needed by otherwise-healthy calls to unrelated dependencies.

## 8. Review Questions
1. Why do retry, circuit breaker, and bulkhead solve genuinely different problems
   rather than being interchangeable?
2. Why is jitter essential alongside backoff, not just a nice-to-have?
3. What does the circuit breaker's "half-open" state exist to check?
4. How does this "design for dependency failure" philosophy connect to consensus/
   replication patterns studied earlier this month?

## 9. Proficiency Checkpoint
If you can design a layered resilience strategy (bulkhead + retry + circuit breaker)
for a real flaky dependency with justified parameter choices, you're at Level 3.

## Next
Day 14 is this week's integrated lab and review — reproducing your real production
incidents end to end and documenting your BigQuery→ClickHouse target-state
architecture.
