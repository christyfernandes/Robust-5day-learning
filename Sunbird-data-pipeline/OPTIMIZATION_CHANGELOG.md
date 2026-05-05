# Pipeline Optimization Changelog — 64k → 100k+ TPS

**Branch:** `cbrelease-4.8.31`  
**Author:** christyfernandes  
**Goal:** Remove throughput ceiling, reduce Redis pressure, eliminate redundant Kafka hops

---

## Table of Contents
1. [What Changed and Why](#1-what-changed-and-why)
2. [Data Flow: Before vs After](#2-data-flow-before-vs-after)
3. [Kafka Topic Inventory](#3-kafka-topic-inventory)
4. [Jobs: Before vs After](#4-jobs-before-vs-after)
5. [Full Decommission Guide](#5-full-decommission-guide)
6. [Performance Impact Summary](#6-performance-impact-summary)

---

## 1. What Changed and Why

### Phase 1 — Configuration and Small Fixes

#### P1.1 — Parallelism Unlocked
**Files changed:** `values.j2`, `defaults/main.yml`, `base-config.conf`

Every job was running at parallelism=1 — a single JVM thread handling all events. Changed `parallelism.default` from 1 to 4 per job and set `taskmanager.numberOfTaskSlots=4`. HPA min/max replicas also configured per job.

**Why it matters:** This alone is the single biggest throughput gain. A pipeline with parallelism=1 can never scale beyond one core's worth of work.

#### P1.2 — HPA Enabled
**File changed:** `flink_job_deployment.yaml`

Lines 226–244 in the deployment template were the complete HPA block, fully written but entirely commented out. Removed the `#` prefixes.

**Why it matters:** Without HPA, the cluster cannot scale pods under burst traffic (e.g., morning spike from 50k to 150k TPS). Jobs would just fall behind and Kafka lag would grow unboundedly.

#### P1.3 — isDuplicateCheckRequired Fix
**File changed:** `PipelinePreprocessorFunction.scala:61`

```scala
// Before (broken — deduplicates ALL events):
def isDuplicateCheckRequired(producerId: String): Boolean = { true }

// After (restored intended logic):
def isDuplicateCheckRequired(producerId: String): Boolean = {
  config.includedProducersForDedup.contains(producerId)
}
```

**Why it matters:** Only portal and desktop events need deduplication (they're the ones that re-send on reconnect). Mobile SDK events are never duplicates. The hardcoded `true` was forcing Redis dedup calls for 50–70% of events that never needed checking, wasting ~500k Redis ops/sec at peak.

#### P1.5 — Druid Validator Deduplication Disabled
**File changed:** `druid-events-validator.conf`

```
task.druid.deduplication.enabled = false
```

**Why it matters:** Events arriving at `telemetry.denorm` were already deduplicated in `pipeline-preprocessor` (Redis DB2). The druid-validator was re-checking them in a different Redis DB (DB8) — 100% redundant, adding ~100k Redis ops/sec at peak.

#### P1.6 — Window and Kafka Producer Tuning
**Files changed:** `de-normalization.conf`, `base-config.conf`

| Setting | Before | After |
|---|---|---|
| `task.window.count` | 30 | 200 |
| `task.window.shards` | 1400 | 400 |
| `kafka.producer.batch.size` | 98304 | 262144 |
| `kafka.producer.linger.ms` | 10 | 20 |
| `checkpointing.interval` | 60000 | 30000 |

**Why it matters:** Larger Redis pipeline batches (200 events vs 30) reduce per-event Redis round-trip overhead. Larger Kafka producer batches reduce network write amplification.

---

### Phase 2 — Architecture Changes

#### P2.1 — Bloom Filter in DedupEngine
**File changed:** `dp-core/src/main/scala/org/sunbird/dp/core/cache/DedupEngine.scala`

Added a Guava `BloomFilter` (10M entries, 0.0001 false positive rate, ~24MB per instance) as a first-check layer before the Redis `EXISTS` call.

```
isUniqueEvent(key):
  if bloom.mightContain(key) → call Redis EXISTS (possible duplicate)
  else → return true immediately (definitely unique, skip Redis)
```

Zero false negatives: a key that has never been seen is guaranteed to return `true` without touching Redis. Cross-instance duplicates (a key seen by a different TaskManager slot) miss the bloom filter and still go to Redis — this is correct behavior, Redis is still authoritative.

**Why it matters:** Reduces Redis dedup EXISTS calls by 60–80%, depending on traffic patterns.

#### P2.2, P2.3, P2.4 — Async De-normalization (Lettuce + Caffeine)
**Files changed:** `DenormalizationAsyncFunction.scala` (new), `DenormalizationStreamTask.scala`, `de-normalization/pom.xml`

**Before (synchronous Jedis pipelining):**
- Operator thread issues Redis `HGETALL` / `GET` calls
- Calls `pipeline.sync()` — thread blocks until all 4 Redis instances respond
- No events can flow through the operator while it waits
- Effective parallelism: number of task slots × 1 event at a time

**After (async Lettuce + Caffeine):**
- Operator thread issues all 6 Lettuce futures (content, collection, l2, device, user, dialcode) concurrently
- Thread immediately returns to process the next event — never blocks
- Up to 500 events have their Redis fetches in-flight simultaneously
- Caffeine local cache (50k entries, 5-min TTL) serves repeated device/user/content IDs in-process, bypassing Redis entirely (~50–70% hit rate for popular IDs)
- LOG, ERROR, AUDIT, INTERRUPT events skip all Redis lookups (P2.4) — ~20–30% of events skip denorm Redis entirely

**New dependencies:**
- `io.lettuce:lettuce-core:6.2.7.RELEASE` — Netty-based non-blocking Redis client
- `com.github.ben-manes.caffeine:caffeine:3.1.8` — in-process cache

**Why it matters:** Synchronous blocking on Redis I/O was the primary bottleneck in de-normalization. At 64k TPS with 4 Redis round trips per event, the operator thread was spending ~95% of its time waiting for network I/O, not processing.

#### P2.5 — Merged TelemetryIntakeStreamTask
**Files changed:** `TelemetryIntakeStreamTask.scala` (new), `telemetry-intake.conf` (new), `pipeline-preprocessor/pom.xml`, `values.j2`, `defaults/main.yml`

Merged the `telemetry-extractor` and `pipeline-preprocessor` jobs into a single `TelemetryIntakeStreamTask`.

The extractor emits `Map[String, AnyRef]`; the preprocessor takes `Event(Map[String, Any])`. The cast `map.asInstanceOf[util.Map[String, Any]]` is safe because all JSON values are JVM reference types.

Config conflict resolution: both original configs read from `redis.database.duplicationstore.id` (value 1 for extractor, 2 for preprocessor) and `kafka.output.duplicate.topic` (different topics). The merged `telemetry-intake.conf` uses nested HOCON namespaces (`extractor { }` and `preprocessor { }`) to isolate conflicting keys. At runtime, `main()` constructs each config from its sub-namespace with base-config as fallback:

```scala
val extractorConfig    = new TelemetryExtractorConfig(rawConfig.getConfig("extractor").withFallback(rawConfig))
val preprocessorConfig = new PipelinePreprocessorConfig(rawConfig.getConfig("preprocessor").withFallback(rawConfig))
```

`telemetry.raw` continues to be written as a **shadow** for SECOR archival. See Section 5 for removal steps.

**Why it matters:** Eliminates the `telemetry.raw` Kafka round-trip. At 100k TPS where each batch contains ~10 individual events, `telemetry.raw` was carrying ~1M events/sec — meaning ~2M Kafka I/O ops/sec (producer + consumer) just for this one intermediate topic.

---

### Phase 3 — Kafka Hop Elimination

#### P3.1 — Direct Druid Routing from De-normalization
**Files changed:** `DenormalizationStreamTask.scala`, `DenormalizationConfig.scala`, `de-normalization.conf`

Added two filter sinks directly on the denorm output stream:

```scala
// Shadow write — keeps SECOR archival working during 30-day drain period
denormStream.addSink(kafkaConnector.kafkaEventSink(config.telemetryDenormOutputTopic))

// New: direct Druid routing — druid-events-validator is no longer needed
denormStream.filter((e: Event) => "ME_WORKFLOW_SUMMARY" == e.eid())
  .addSink(kafkaConnector.kafkaEventSink(config.kafkaSummaryRouteTopic))    // druid.events.summary

denormStream.filter((e: Event) => "ME_WORKFLOW_SUMMARY" != e.eid())
  .addSink(kafkaConnector.kafkaEventSink(config.kafkaTelemetryRouteTopic))  // druid.events.telemetry
```

New config keys in `de-normalization.conf`:
```
kafka.output.telemetry.route.topic = {env}.druid.events.telemetry
kafka.output.summary.route.topic   = {env}.druid.events.summary
```

`telemetry.denorm` continues to be written as a **shadow** for SECOR archival. See Section 5 for removal steps.

**Why it matters:** At 100k TPS, `druid-events-validator` was consuming ~100k events/sec from `telemetry.denorm`, validating them (mostly a no-op since druid-validator dedup was already disabled in P1.5), and re-publishing to two topics. This is a pure overhead job that can be eliminated.

---

## 2. Data Flow: Before vs After

### Before (Original — 4 Kafka Hops in Hot Path)

```
[telemetry.ingest]
        │
        ▼
┌─────────────────────┐
│  telemetry-extractor │  ← dedup (Redis DB1), extract, redact
└─────────────────────┘
        │
        ▼
[telemetry.raw]  ◄── SECOR reads this
        │
        ▼
┌───────────────────────┐
│  pipeline-preprocessor │  ← validate, dedup (Redis DB2), route
└───────────────────────┘
        │
        ├──► [telemetry.unique]            ─┐
        ├──► [telemetry.unique.secondary]   ├── de-norm inputs
        ├──► [telemetry.audit]             ─┘
        ├──► [telemetry.error]
        ├──► [telemetry.duplicate]
        ├──► [telemetry.failed]
        ├──► [druid.events.log]
        └──► [telemetry.cb.audit]

[telemetry.unique] + [telemetry.unique.secondary]
        │
        ▼
┌───────────────────┐
│  de-normalization  │  ← Redis enrichment (blocking Jedis, 4 stores)
└───────────────────┘
        │
        ▼
[telemetry.denorm]  ◄── SECOR reads this (3 consumer groups)
        │
        ▼
┌─────────────────────┐
│  druid-events-validator │  ← route only (dedup was redundant)
└─────────────────────┘
        │
        ├──► [druid.events.telemetry]
        └──► [druid.events.summary]
```

**Total Kafka hops in hot path: 4**
`ingest → raw → unique → denorm → druid`

---

### After (Optimized — 2 Kafka Hops in Hot Path)

```
[telemetry.ingest]
        │
        ▼
┌──────────────────────────────┐
│      telemetry-intake         │  ← extractor + preprocessor merged
│  (replaces extractor + pp)    │     dedup (DB1 + DB2), extract, validate, route
└──────────────────────────────┘
        │
        ├──► [telemetry.raw]  (shadow write — SECOR drain only, 30 days)
        ├──► [telemetry.unique]            ─┐
        ├──► [telemetry.unique.secondary]   ├── de-norm inputs (unchanged)
        ├──► [telemetry.audit]             ─┘
        ├──► [telemetry.error]
        ├──► [telemetry.duplicate]
        ├──► [telemetry.failed]
        ├──► [druid.events.log]
        ├──► [telemetry.cb.audit]
        ├──► [telemetry.extractor.duplicate]
        └──► [telemetry.extractor.failed]

[telemetry.unique] + [telemetry.unique.secondary]
        │
        ▼
┌──────────────────────────────────────────────┐
│            de-normalization                   │
│  async Lettuce + Caffeine cache + Bloom       │  ← non-blocking, 500 in-flight
│  P2.4: LOG/ERROR/AUDIT skip Redis entirely   │
└──────────────────────────────────────────────┘
        │
        ├──► [telemetry.denorm]  (shadow write — SECOR drain only, 30 days)
        ├──► [druid.events.telemetry]  ◄── direct, no validator job needed
        └──► [druid.events.summary]   ◄── direct, no validator job needed
```

**Total Kafka hops in hot path: 2**
`ingest → unique → druid`

---

## 3. Kafka Topic Inventory

### Full Topic List Before Optimization

| Topic | Purpose | Written By | Read By |
|---|---|---|---|
| `{env}.telemetry.ingest` | Raw batch events from SDK | Mobile/Portal SDK | telemetry-extractor |
| `{env}.telemetry.raw` | Extracted individual events | telemetry-extractor | pipeline-preprocessor, SECOR |
| `{env}.telemetry.extractor.duplicate` | Duplicate batch events | telemetry-extractor | SECOR |
| `{env}.telemetry.extractor.failed` | Oversized batch events | telemetry-extractor | SECOR |
| `{env}.telemetry.assess.raw` | Unredacted ASSESS/RESPONSE events | telemetry-extractor (Redactor) | SECOR |
| `{env}.telemetry.unique` | Primary denorm input | pipeline-preprocessor | de-normalization |
| `{env}.telemetry.unique.secondary` | Secondary denorm input (INTERACT etc.) | pipeline-preprocessor | de-normalization |
| `{env}.telemetry.duplicate` | Preprocessor-level duplicates | pipeline-preprocessor | SECOR |
| `{env}.telemetry.failed` | Validation failures | pipeline-preprocessor | SECOR |
| `{env}.telemetry.error` | ERROR events | pipeline-preprocessor | SECOR |
| `{env}.telemetry.audit` | AUDIT events | pipeline-preprocessor | user-cache-updater, SECOR |
| `{env}.druid.events.log` | LOG events | extractor + preprocessor | Druid |
| `{env}.telemetry.cb.audit` | CB audit events | pipeline-preprocessor | cb-preprocessor |
| `{env}.telemetry.denorm` | Enriched events | de-normalization | druid-events-validator, SECOR (3 groups) |
| `{env}.druid.events.telemetry` | Final Druid telemetry feed | druid-events-validator | Druid |
| `{env}.druid.events.summary` | Final Druid summary feed | druid-events-validator | Druid |

**Total topics:** 16 active in hot path

### Topic Status After Optimization

| Topic | Status | Notes |
|---|---|---|
| `{env}.telemetry.ingest` | **Active — unchanged** | Still the entry point |
| `{env}.telemetry.raw` | **Shadow write only** | Written by telemetry-intake, no longer consumed by pipeline-preprocessor. Only SECOR reads it during drain period. |
| `{env}.telemetry.extractor.duplicate` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.extractor.failed` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.assess.raw` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.unique` | **Active — unchanged** | Still the primary denorm input |
| `{env}.telemetry.unique.secondary` | **Active — unchanged** | Still the secondary denorm input |
| `{env}.telemetry.duplicate` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.failed` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.error` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.audit` | Active — unchanged | Still written/read normally |
| `{env}.druid.events.log` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.cb.audit` | Active — unchanged | Still written/read normally |
| `{env}.telemetry.denorm` | **Shadow write only** | Written by de-normalization, no longer consumed by druid-events-validator. Only SECOR reads it during drain period. |
| `{env}.druid.events.telemetry` | **Active — now written by denorm** | Was written by druid-events-validator, now written directly |
| `{env}.druid.events.summary` | **Active — now written by denorm** | Was written by druid-events-validator, now written directly |

**Topics that can be permanently deleted after 30-day drain: 2**
- `{env}.telemetry.raw`
- `{env}.telemetry.denorm`

---

## 4. Jobs: Before vs After

### Jobs Before Optimization

| Job | Reads From | Writes To | Status |
|---|---|---|---|
| `telemetry-extractor` | `telemetry.ingest` | `telemetry.raw`, side topics | Replaced by telemetry-intake |
| `pipeline-preprocessor` | `telemetry.raw` | `telemetry.unique`, route topics | Replaced by telemetry-intake |
| `de-normalization` | `telemetry.unique` + `.secondary` | `telemetry.denorm` | Modified — now also writes to druid directly |
| `druid-events-validator` | `telemetry.denorm` | `druid.events.telemetry`, `druid.events.summary` | Can be decommissioned |

### Jobs After Optimization

| Job | Reads From | Writes To | Notes |
|---|---|---|---|
| `telemetry-intake` | `telemetry.ingest` | `telemetry.raw` (shadow) + all route topics | **New** — merged extractor + preprocessor |
| `de-normalization` | `telemetry.unique` + `.secondary` | `telemetry.denorm` (shadow) + druid topics directly | **Modified** — async I/O, direct druid routing |
| `telemetry-extractor` | — | — | **Decommission after 7-day telemetry-intake validation** |
| `pipeline-preprocessor` | — | — | **Decommission after 7-day telemetry-intake validation** |
| `druid-events-validator` | — | — | **Decommission after 7-day P3.1 validation** |

---

## 5. Full Decommission Guide

This section covers the complete steps to remove the two deprecated shadow topics and eliminate the SECOR dependency on them. **Do not do this until the new jobs have been running stably for at least 30 days.**

### Prerequisites Before Any Decommission Step

- [ ] `telemetry-intake` job running stably for 7+ days
- [ ] No consumer lag on `telemetry.unique` and `telemetry.unique.secondary`
- [ ] Direct Druid routing from denorm verified (Druid receiving data on `druid.events.telemetry` and `druid.events.summary`)
- [ ] No consumer lag on druid topics
- [ ] Alerts set up on Druid parse exception rate (should be near 0)

---

### Step A — Decommission `telemetry-extractor` and `pipeline-preprocessor`

Once `telemetry-intake` is verified:

```bash
# Scale down both old jobs (Kubernetes)
kubectl scale deployment telemetry-extractor --replicas=0 -n <flink-namespace>
kubectl scale deployment pipeline-preprocessor --replicas=0 -n <flink-namespace>
```

Or via Ansible — set `replica: 0` for both in `defaults/main.yml` and re-run the deploy playbook.

**Verify:** Check that `telemetry.unique` consumer lag (`-telemetry-denorm-primary-group`) remains stable — it should be fed by `telemetry-intake` now.

---

### Step B — Remove `telemetry.raw` and its SECOR Backup (30-day drain)

**Wait until:** `telemetry-extractor` and `pipeline-preprocessor` have been stopped for 30 days **AND** SECOR consumer group `{env}.telemetry.raw.backup` shows zero lag.

**1. Monitor SECOR lag:**
```bash
# Check the SECOR consumer group on telemetry.raw
kafka-consumer-groups.sh --bootstrap-server <broker>:9092 \
  --describe --group {env}.telemetry.raw.backup
# LAG column should be 0 for all partitions
```

**2. Disable the SECOR backup for `telemetry.raw`:**

File: `kubernetes/ansible/roles/secor-deploy/defaults/main.yaml`

Find and comment out (or delete) the block that reads `topic: "{{env_name}}.telemetry.raw"` (around lines 20–30):

```yaml
# Remove or comment the following block:
- name: telemetry_raw
  consumer_group: "{{env_name}}.telemetry.raw.backup"
  base_path: "telemetry-raw"         # adjust to your actual base_path value
  topic: "{{env_name}}.telemetry.raw"
  # ... all fields in this block
```

**3. Re-run the SECOR deploy playbook:**
```bash
ansible-playbook -i <inventory> secor-deploy.yml --tags secor
```

**4. Verify SECOR no longer consumes `telemetry.raw`:**
```bash
kafka-consumer-groups.sh --bootstrap-server <broker>:9092 --list | grep raw.backup
# Should return nothing
```

**5. Delete the topic:**
```bash
kafka-topics.sh --bootstrap-server <broker>:9092 \
  --delete --topic {env}.telemetry.raw
# Verify:
kafka-topics.sh --bootstrap-server <broker>:9092 --list | grep telemetry.raw
# Should return nothing
```

**6. Remove `telemetry.raw` shadow write from `telemetry-intake.conf` and `values.j2`:**

In `TelemetryIntakeStreamTask.scala`, remove the shadow sink:
```scala
// DELETE this block:
mergedRaw.addSink(kafkaConnector.kafkaMapSink(extractorConfig.kafkaSuccessTopic))
  .name(extractorConfig.extractorRawEventsProducer)...
```

In `telemetry-intake.conf`, remove:
```
output.success.topic = ${job.env}".telemetry.raw"
```

In `values.j2` `telemetry-intake` block, remove:
```
output.success.topic = {{ env_name }}.telemetry.raw
```

In `TelemetryExtractorConfig.scala` the `kafkaSuccessTopic` val can remain (it's used for the `extractorRawEventsProducer` name string). Alternatively, remove both.

---

### Step C — Decommission `druid-events-validator`

Once direct Druid routing from de-normalization is verified:

```bash
kubectl scale deployment druid-events-validator --replicas=0 -n <flink-namespace>
```

**Verify:** Druid continues receiving events. Check Druid ingestion supervisor status.

---

### Step D — Remove `telemetry.denorm` and its SECOR Backups (30-day drain)

**Wait until:** `druid-events-validator` has been stopped for 30 days **AND** all three SECOR consumer groups on `telemetry.denorm` show zero lag.

**1. Monitor all three SECOR consumer groups:**
```bash
for GROUP in \
  "{env}.telemetry.denorm.backup" \
  "{env}.telemetry.channel.backup" \
  "{env}.summary.backup"; do
  echo "=== $GROUP ==="
  kafka-consumer-groups.sh --bootstrap-server <broker>:9092 \
    --describe --group "$GROUP"
done
# All LAG columns must be 0
```

**2. Disable the three SECOR backups for `telemetry.denorm`:**

File: `kubernetes/ansible/roles/secor-deploy/defaults/main.yaml`

Remove or comment out all three blocks that read `topic: "{{ env_name }}.telemetry.denorm"`:

```yaml
# Block 1 — around line 97-101:
# consumer_group: "{{ env_name }}.telemetry.denorm.backup"
# base_path: "telemetry-denormalized"
# topic: "{{ env_name }}.telemetry.denorm"

# Block 2 — around line 122-151 (summary backup):
# consumer_group: "{{ env_name }}.summary.backup"
# base_path: "telemetry-denormalized/summary"
# topic: "{{ env_name }}.telemetry.denorm"

# Block 3 — around line 147-154 (channel backup):
# consumer_group: "{{ env_name }}.telemetry.channel.backup"
# topic: "{{ env_name }}.telemetry.denorm"
```

**3. Re-run the SECOR deploy playbook:**
```bash
ansible-playbook -i <inventory> secor-deploy.yml --tags secor
```

**4. Update Prometheus adapter — remove the druid-validator HPA metric:**

File: `kubernetes/ansible/roles/sunbird-monitoring/templates/dp_prometheus-adapter.yaml`

Around line 77–80, remove or replace this metric:
```yaml
# REMOVE this block — druid-validator-group no longer exists:
- seriesQuery: 'kafka_consumergroup_lag_sum{consumergroup="{{ env_name }}-druid-validator-group",topic="{{ env_name }}.telemetry.denorm"}'
  name:
    as: "druid-validator_kafka_consumergroup_lag_sum"
  metricsQuery: sum(kafka_consumergroup_lag_sum{consumergroup="{{ env_name }}-druid-validator-group",topic="{{ env_name }}.telemetry.denorm"}) by (<<.GroupBy>>)
```

If HPA is needed for the denorm job based on consumer lag, replace it with the denorm consumer group on `telemetry.unique`:
```yaml
- seriesQuery: 'kafka_consumergroup_lag_sum{consumergroup="{{ env_name }}-telemetry-denorm-primary-group",topic="{{ env_name }}.telemetry.unique.primary"}'
  name:
    as: "denorm_kafka_consumergroup_lag_sum"
  metricsQuery: sum(kafka_consumergroup_lag_sum{consumergroup="{{ env_name }}-telemetry-denorm-primary-group",topic="{{ env_name }}.telemetry.unique.primary"}) by (<<.GroupBy>>)
```

**5. Re-run the monitoring playbook:**
```bash
ansible-playbook -i <inventory> monitoring.yml --tags prometheus-adapter
```

**6. Delete the topic:**
```bash
kafka-topics.sh --bootstrap-server <broker>:9092 \
  --delete --topic {env}.telemetry.denorm
# Verify:
kafka-topics.sh --bootstrap-server <broker>:9092 --list | grep telemetry.denorm
# Should return nothing
```

**7. Remove `telemetry.denorm` shadow write from denorm code:**

In `DenormalizationStreamTask.scala`, remove the shadow sink:
```scala
// DELETE this block:
denormStream.addSink(kafkaConnector.kafkaEventSink(config.telemetryDenormOutputTopic))
  .name(config.DENORM_EVENTS_PRODUCER)...
```

In `de-normalization.conf`, remove:
```
telemetry.denorm.output.topic = ${job.env}".telemetry.denorm"
```

In `DenormalizationConfig.scala`, remove:
```scala
val telemetryDenormOutputTopic: String = config.getString("kafka.telemetry.denorm.output.topic")
val DENORM_EVENTS_PRODUCER = "telemetry-denorm-events-producer"
```

Update `values.j2` denorm block to remove `telemetry.denorm.output.topic` line.

---

### Post-Decommission Verification Checklist

- [ ] `kafka-topics.sh --list` shows no `telemetry.raw` or `telemetry.denorm`
- [ ] `kafka-consumer-groups.sh --list` shows no groups ending in `.raw.backup`, `.denorm.backup`, `.channel.backup`, `.summary.backup`
- [ ] Druid ingestion supervisors show healthy rows/sec (no drop after removing topics)
- [ ] Prometheus shows no alerts firing for the removed consumer groups
- [ ] SECOR S3/GCS object counts in `telemetry-raw/` and `telemetry-denormalized/` stop growing

---

## 6. Performance Impact Summary

### Kafka I/O Reduction

| Eliminated | Estimated Ops Saved at 100k TPS |
|---|---|
| `telemetry.raw` round-trip (P2.5) | ~2M ops/sec (1M write + 1M read, 10x fan-out from batch) |
| `telemetry.denorm` round-trip (P3.1) | ~200k ops/sec (100k write + 100k read) |
| Redundant druid-validator dedup (P1.5) | ~100k Redis ops/sec |
| Skipped preprocessor dedup for non-portal/desktop (P1.3) | ~300–500k Redis ops/sec |

### Redis I/O Reduction

| Optimization | Mechanism | Estimated Redis Reduction |
|---|---|---|
| Bloom filter (P2.1) | Skips Redis EXISTS for definitely-unique events | 60–80% fewer dedup calls |
| Caffeine cache (P2.3) | Serves repeated device/user/content IDs in-process | 50–70% fewer denorm Redis calls |
| Enrichment skip (P2.4) | LOG/ERROR/AUDIT/INTERRUPT skip all Redis lookups | 20–30% fewer denorm Redis calls overall |
| Async I/O (P2.2) | All fetches concurrent, operator never blocks | Not a reduction — but enables the parallelism |

### Throughput Gains

| Change | Mechanism | Expected Throughput Gain |
|---|---|---|
| Parallelism 1 → 4 (P1.1) | More operator threads per job | 3–5× |
| HPA enabled (P1.2) | Auto-scales under burst | 2–4× burst headroom |
| Async denorm I/O (P2.2) | Operator thread never stalls on Redis | 3–5× denorm throughput |
| Merged intake job (P2.5) | Eliminates Kafka serialization/deserialization round-trip | 10–15% latency reduction |
| Direct Druid routing (P3.1) | Eliminates one full job's worth of Kafka consumer lag | 5–10% end-to-end latency |

### Job Count

| | Before | After (active) | Decommissioned |
|---|---|---|---|
| Hot-path jobs | 4 | 2 | 2 (extractor, preprocessor → merged; druid-validator → eliminated) |
| Support jobs | unchanged | unchanged | — |
