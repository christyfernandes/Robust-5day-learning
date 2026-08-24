# Day 7 — Lab + Week 1 Review

## Time: ~3-4 hours | Proficiency target: Level 2 confirmed across all 7 tracks

Day 7 has no new concepts — it's where Week 1's ideas become muscle memory. Three
parts: stand up a real multi-service pipeline, write your first ADR, and self-assess
honestly against the Week 1 target before moving into Week 2's internals-level depth.

## Part 1 — Stand Up the Pipeline (~90 min)

Extend `legacy-5-day-plan/FinalProject/docker-compose.yml` (which already wires up
Kafka + Zookeeper + Redis + Elasticsearch) with a ClickHouse service:

```yaml
  clickhouse:
    image: clickhouse/clickhouse-server:24.8
    ports:
      - "8123:8123"   # HTTP interface
      - "9000:9000"   # native protocol
    ulimits:
      nofile:
        soft: 262144
        hard: 262144
```

Bring everything up:
```bash
docker compose up -d
docker compose ps   # confirm all 5 services are healthy
```

**Produce events into Kafka.** Reuse/adapt `legacy-5-day-plan/FinalProject/producer.py`
to emit a realistic event stream (order events, clickstream, or whatever domain you
prefer — consistency with later weeks matters more than the specific choice):

```python
from kafka import KafkaProducer
import json, random, time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode(),
)

for i in range(1000):
    event = {
        "event_id": i,
        "org_id": random.randint(1, 20),
        "event_type": random.choice(["view", "click", "purchase"]),
        "amount": round(random.uniform(5, 500), 2) if random.random() > 0.7 else None,
        "timestamp": time.time(),
    }
    producer.send("events", value=event, key=str(event["org_id"]).encode())
    time.sleep(0.05)
producer.flush()
```

**Write events to Redis (cache) and Elasticsearch (search) as a warm-up integration** —
a plain consumer for now (Flink joins the pipeline properly in Week 2):

```python
from kafka import KafkaConsumer
import redis, json
from elasticsearch import Elasticsearch

r = redis.Redis()
es = Elasticsearch("http://localhost:9200")
consumer = KafkaConsumer("events", bootstrap_servers="localhost:9092",
                          value_deserializer=lambda v: json.loads(v))

for msg in consumer:
    event = msg.value
    r.incr(f"org:{event['org_id']}:event_count")          # cheap running counter
    es.index(index="events", document=event)               # searchable copy
```

Verify: `redis-cli GET org:5:event_count` returns a plausible count, and
`curl "localhost:9200/events/_search?q=event_type:purchase"` returns real hits.

## Part 2 — Your First ADR (~45 min)

Using the CAP/PACELC framing from Day 1, write an ADR (Architecture Decision Record)
for a hypothetical feature at work — pick a consistency model (strong vs. eventual) and
justify it. Use this template (also referenced from Week 4):

```markdown
# ADR-001: [Consistency model] for [feature name]

## Status
Proposed

## Context
What is the feature? What are its read/write patterns? What happens if two clients
see different data momentarily — is that acceptable, or does it break something?

## Decision
Strong consistency / Eventual consistency — and specifically which mechanism
(e.g., "synchronous replication with quorum acks" vs. "async replication, eventual
convergence").

## Consequences
- What do we gain? (availability, latency, simplicity)
- What do we give up? (the PACELC trade-off, named explicitly)
- What would make us revisit this decision later?
```

**Worked example** (yours should be about a real or realistic feature, not this one):
a "view count" feature on a content platform is a strong candidate for **eventual
consistency** — a view counter being off by a few seconds of lag is invisible to users,
and demanding strong consistency here would add latency/availability cost for a
guarantee nobody needs. Contrast with an inventory "decrement stock" operation
(Day 5's Redis lesson) — that one usually *does* need strong consistency, because
overselling has a real business cost.

## Part 3 — Self-Assessment (~15 min)

Fill in your Week 1 row in [`../../PROGRESS_TRACKER.md`](../../PROGRESS_TRACKER.md).
For each of the 7 tracks, be honest rather than generous — Week 2 assumes Level 2 is
solid, not aspirational.

**Full-week review — answer out loud, without notes, one per track:**
1. **PySpark**: Draw the driver/executor/stage/task hierarchy and mark exactly where a
   shuffle occurs in a `groupBy`.
2. **Kafka**: Explain what `min.insync.replicas=2` with `replication.factor=3`
   guarantees and refuses.
3. **Flink**: Explain why a downstream operator's watermark is the *minimum* across
   its inputs.
4. **Redis**: Predict what survives a hard crash under `appendfsync everysec` vs.
   RDB-only.
5. **Elasticsearch**: Explain the difference between query context and filter context,
   and why it matters for both scoring and caching.
6. **ClickHouse**: Given a table's `ORDER BY` key and a candidate query, predict
   "granule skip" vs. "full scan."
7. **Architecture**: Explain consistent hashing's rebalancing advantage over
   hash-mod partitioning, using a concrete example.

**Checkpoint:** if you can answer all 7 without hesitation, you're solidly at Level 2
across the board — some tracks (ClickHouse, Architecture) likely already trending
toward Level 3 given your production experience. Week 2 goes noticeably deeper on all
seven.

## Next
Week 2 — Internals & Depth — starts with Catalyst/Tungsten codegen, Kafka Streams,
Flink's Table API, Redis replication, Elasticsearch's scatter-gather model, ClickHouse's
vectorized engine, and a survey of core architectural styles.
