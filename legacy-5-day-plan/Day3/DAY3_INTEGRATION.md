# Day 3: System Integration & Architecture

## Time Allocation: 2-3 hours total (multi-system integration)

---

## Integration Architecture: Real-Time Analytics Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
│  Web Events | Mobile App | IoT Devices | API Endpoints      │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │   Apache Kafka          │
        │ (Event Streaming Hub)   │
        │ Topics:                 │
        │ - user_events           │
        │ - transactions          │
        │ - system_logs           │
        └────────┬────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────────┐ ┌─▼──────────┐ │
│Apache Flink│ │ PySpark    │ │
│ Real-Time  │ │ Batch      │ │
│ Processing │ │ Processing │ │
└───┬────────┘ └─┬──────────┘ │
    │            │            │
    └────────────┼────────────┘
                 │
        ┌────────▼──────────────┐
        │    Redis Cache        │
        │  - Session Store      │
        │  - Feature Cache      │
        │  - Leaderboards       │
        └────────┬──────────────┘
                 │
        ┌────────▼──────────────┐
        │  Elasticsearch        │
        │  - Analytics Index    │
        │  - Search Index       │
        │  - Aggregations       │
        └────────┬──────────────┘
                 │
        ┌────────▼──────────────┐
        │   Database / DW       │
        │  - Long-term Storage  │
        │  - Reporting          │
        └───────────────────────┘
```

---

## Part 1: Kafka → Redis → Elasticsearch Pipeline

### Setup: Create Topics & Prepare Systems

```python
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from elasticsearch import Elasticsearch
import redis
import json
import time
from datetime import datetime

# Setup Kafka topics
admin = KafkaAdminClient(bootstrap_servers=['localhost:9092'])

topics = [
    NewTopic(name='raw_events', num_partitions=3, replication_factor=1),
    NewTopic(name='processed_events', num_partitions=2, replication_factor=1),
]

try:
    admin.create_topics(topics)
except Exception as e:
    print(f"Topics already exist: {e}")

# Initialize clients
kafka_producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

kafka_consumer = KafkaConsumer(
    'raw_events',
    bootstrap_servers=['localhost:9092'],
    group_id='enrichment-group',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
es_client = Elasticsearch(['http://localhost:9200'])

print("✓ All systems initialized")
```

### Scenario: User Activity Pipeline

```python
# 1. Producer: Generate user events
def generate_user_events():
    events = [
        {"user_id": "user_1", "action": "login", "timestamp": datetime.now().isoformat()},
        {"user_id": "user_2", "action": "purchase", "product": "laptop", "amount": 999.99},
        {"user_id": "user_1", "action": "view_product", "product": "mouse"},
        {"user_id": "user_3", "action": "add_to_cart", "product": "keyboard", "quantity": 2},
        {"user_id": "user_2", "action": "logout"},
    ]
    
    for event in events:
        event['timestamp'] = datetime.now().isoformat()
        kafka_producer.send('raw_events', value=event)
        print(f"Produced: {event['action']}")
        time.sleep(0.5)

# 2. Enrichment Consumer: Add context from Redis, forward to processed topic
def enrich_events():
    event_count = 0
    
    for message in kafka_consumer:
        event = message.value
        
        # Fetch user profile from Redis
        user_profile = redis_client.hgetall(f"user:{event['user_id']}")
        
        if not user_profile:
            # Create default profile
            user_profile = {
                'name': f"User {event['user_id']}",
                'tier': 'basic',
                'purchases': 0
            }
            redis_client.hset(f"user:{event['user_id']}", mapping=user_profile)
        
        # Enrich event
        enriched = {
            **event,
            'user_tier': user_profile.get('tier', 'basic'),
            'user_name': user_profile.get('name', 'Unknown'),
            'enriched_at': datetime.now().isoformat()
        }
        
        # Update user stats in Redis
        redis_client.hincrby(f"user:{event['user_id']}", 'event_count', 1)
        
        # Forward enriched event
        kafka_producer.send('processed_events', value=enriched)
        
        event_count += 1
        print(f"[Enriched] {enriched['action']} - User Tier: {enriched['user_tier']}")
        
        if event_count >= 5:
            break

# 3. Indexer Consumer: Index into Elasticsearch
def index_to_elasticsearch():
    consumer = KafkaConsumer(
        'processed_events',
        bootstrap_servers=['localhost:9092'],
        group_id='indexer-group',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    # Create mapping
    mapping = {
        "mappings": {
            "properties": {
                "user_id": {"type": "keyword"},
                "action": {"type": "keyword"},
                "user_tier": {"type": "keyword"},
                "amount": {"type": "float"},
                "timestamp": {"type": "date"},
                "enriched_at": {"type": "date"}
            }
        }
    }
    
    if es_client.indices.exists(index='user_events'):
        es_client.indices.delete(index='user_events')
    
    es_client.indices.create(index='user_events', body=mapping)
    
    event_count = 0
    for message in consumer:
        event = message.value
        es_client.index(index='user_events', body=event)
        event_count += 1
        print(f"[Indexed] {event['action']} for {event['user_id']}")
        
        if event_count >= 5:
            break

# Execute pipeline
print("Step 1: Generating events...")
generate_user_events()

time.sleep(2)

print("\nStep 2: Enriching events from Redis...")
enrich_events()

time.sleep(2)

print("\nStep 3: Indexing to Elasticsearch...")
index_to_elasticsearch()

# Verify results
print("\n=== VERIFICATION ===")

# Check Redis cache
user1_profile = redis_client.hgetall('user:user_1')
print(f"User 1 in Redis: {user1_profile}")

# Check Elasticsearch
es_results = es_client.search(index='user_events', body={"query": {"match_all": {}}})
print(f"\nES Events indexed: {es_results['hits']['total']['value']}")

# Analytics query
agg_result = es_client.search(index='user_events', body={
    "size": 0,
    "aggs": {
        "by_user_tier": {
            "terms": {"field": "user_tier"},
            "aggs": {
                "event_count": {"value_count": {"field": "user_id"}}
            }
        }
    }
})

print("\nEvent breakdown by user tier:")
for bucket in agg_result['aggregations']['by_user_tier']['buckets']:
    print(f"  {bucket['key']}: {bucket['doc_count']} events")
```

---

## Part 2: Kafka → Flink → Redis (Real-Time Processing)

### Stream Processing with Flink

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction, ReduceFunction, WindowFunction
from pyflink.datastream.window.time_window import TumblingProcessingTimeWindow
from pyflink.common.typeinfo import Types
import json
from datetime import datetime

env = StreamExecutionEnvironment.get_execution_environment()

# Simulate Kafka source
events = [
    {"user_id": "user_1", "amount": 100, "timestamp": int(time.time() * 1000)},
    {"user_id": "user_2", "amount": 50, "timestamp": int(time.time() * 1000)},
    {"user_id": "user_1", "amount": 75, "timestamp": int(time.time() * 1000)},
    {"user_id": "user_3", "amount": 200, "timestamp": int(time.time() * 1000)},
    {"user_id": "user_2", "amount": 60, "timestamp": int(time.time() * 1000)},
]

# Map to tuple for keying
stream = env.from_collection(events, type_info=Types.MAP(Types.STRING, Types.ANY))

# Extract key and amount
keyed_stream = stream \
    .map(lambda x: (x['user_id'], x['amount']), output_type=Types.TUPLE([Types.STRING, Types.FLOAT])) \
    .key_by(lambda x: x[0])

# Window aggregation (sum per user over 10-second window)
class SumWindow(WindowFunction):
    def apply(self, key, time_window, inputs, out):
        total = sum(x[1] for x in inputs)
        out.collect((key[0], total))

windowed = keyed_stream.window(TumblingProcessingTimeWindow(10000)).apply(SumWindow())

# Output to Redis
class RedisOutputFunction(MapFunction):
    def map(self, value):
        user_id, total = value
        # In real scenario, would write to Redis
        print(f"User {user_id}: Total = ${total}")
        return value

result = windowed.map(RedisOutputFunction())
result.print()

# Execute
env.execute("Real-Time Revenue Aggregation")
```

---

## Part 3: PySpark Batch + Flink Stream Integration

### Scenario: Combining batch historical data with stream

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import time

spark = SparkSession.builder.appName("BatchStreamIntegration").master("local[2]").getOrCreate()

# Batch: Historical user profiles (from database/file)
historical_users = spark.createDataFrame([
    (1, "alice", "premium", 50),
    (2, "bob", "standard", 10),
    (3, "carol", "premium", 30),
], ["id", "name", "tier", "lifetime_purchases"])

# Batch: Today's transactions (from CSV/Parquet)
today_transactions = spark.createDataFrame([
    ("alice", 100, "2024-01-01 10:00:00"),
    ("bob", 50, "2024-01-01 10:05:00"),
    ("alice", 75, "2024-01-01 10:10:00"),
], ["user_name", "amount", "timestamp"])

# Join historical with today's data
joined = historical_users.join(
    today_transactions,
    historical_users.name == today_transactions.user_name,
    "left"
)

# Calculate total value
result = joined.groupBy("name", "tier") \
    .agg(
        sum("amount").alias("today_spent"),
        max("lifetime_purchases").alias("lifetime_purchases")
    ) \
    .withColumn("total_value", col("today_spent") + col("lifetime_purchases"))

result.show()

# Write results (can be consumed by Elasticsearch)
result.write.mode("overwrite").json("daily_summary")
```

---

## Part 4: Integration Patterns Summary

### Pattern 1: Lambda Architecture
```
Batch Layer (PySpark) → Batch View
                     ↓
                 Merge Layer
                     ↑
Speed Layer (Flink) → Real-Time View
```

### Pattern 2: Kappa Architecture
```
Event Stream (Kafka) → Flink Processing → Output
                  ↓
            Reprocessing (if needed)
```

### Pattern 3: Data Lake Architecture
```
Raw Events (Kafka) → Bronze Layer (S3/Hadoop)
                        ↓
                  Silver Layer (Spark)
                        ↓
                  Gold Layer (Analytics)
                        ↓
             ES/Redis/DB (Serving)
```

---

## Advanced Integration Example: Real-Time Recommendation Engine

```python
import redis
import json
from datetime import datetime

class RecommendationEngine:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.es = Elasticsearch(['http://localhost:9200'])
    
    def ingest_user_action(self, user_id, action_type, product_id):
        """Process user action from Kafka"""
        # Store in Redis for real-time access
        self.redis.lpush(f"user:{user_id}:actions", json.dumps({
            'type': action_type,
            'product_id': product_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Update user engagement score
        self.redis.zincrby('user:engagement:score', 1, user_id)
    
    def get_trending_products(self, hours=24):
        """Get trending products from ES aggregation"""
        query = {
            "aggs": {
                "trending": {
                    "terms": {"field": "product_id", "size": 10}
                }
            }
        }
        result = self.es.search(index='user_events', body=query)
        return [b['key'] for b in result['aggregations']['trending']['buckets']]
    
    def recommend_products(self, user_id, num_recommendations=5):
        """Generate recommendations"""
        # Get user's viewed products
        actions = self.redis.lrange(f"user:{user_id}:actions", 0, 100)
        viewed_products = set()
        
        for action_str in actions:
            action = json.loads(action_str)
            if action['type'] == 'view':
                viewed_products.add(action['product_id'])
        
        # Get trending products not yet viewed
        trending = self.get_trending_products()
        recommendations = [p for p in trending if p not in viewed_products]
        
        return recommendations[:num_recommendations]

# Usage
engine = RecommendationEngine()
engine.ingest_user_action('user_1', 'view', 'laptop_001')
engine.ingest_user_action('user_1', 'click', 'mouse_002')

recs = engine.recommend_products('user_1')
print(f"Recommendations for user_1: {recs}")
```

---

## Monitoring Integration

```python
def monitor_pipeline():
    """Monitor all systems health"""
    import subprocess
    
    checks = {
        'Kafka': 'kafka-broker-api-versions --bootstrap-server localhost:9092',
        'Redis': 'redis-cli ping',
        'Elasticsearch': 'curl -s http://localhost:9200/_health',
    }
    
    for service, cmd in checks.items():
        try:
            result = subprocess.run(cmd.split(), capture_output=True, timeout=5)
            status = "✓" if result.returncode == 0 else "✗"
            print(f"{status} {service}")
        except Exception as e:
            print(f"✗ {service} - {e}")

monitor_pipeline()
```

---

## Exercises for Day 3

1. **Build a complete event pipeline**: Produce events → Consume → Enrich → Index
2. **Implement caching layer**: Use Redis to cache frequently accessed data
3. **Create aggregations**: Use Flink for real-time sums/averages
4. **Setup alerts**: Trigger alerts when metrics exceed thresholds
5. **Monitor lag**: Check Kafka consumer lag across groups

---

## Key Design Principles

1. **Idempotency**: Ensure operations can be safely retried
2. **Fault Tolerance**: Design for failure at every layer
3. **Data Consistency**: Choose between strong vs eventual consistency
4. **Scalability**: Ensure each component can scale independently
5. **Monitoring**: Instrument all critical paths

---

## Next: Day 4 - Performance & Optimization
