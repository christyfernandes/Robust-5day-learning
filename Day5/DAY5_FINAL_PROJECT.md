# Day 5: Comprehensive Final Project

## Complete Real-Time E-Commerce Analytics Platform

### Project Overview

Build a production-like real-time analytics pipeline that processes user events, caches data, and provides instant insights. This project uses all five technologies working together.

```
┌──────────────────────────────────────────────────────────────┐
│         E-COMMERCE REAL-TIME ANALYTICS PLATFORM              │
│                                                              │
│  Event Sources (Web, Mobile, API)                           │
│              ↓                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Apache Kafka - Event Streaming Hub                  │   │
│  │ Topics: user_events, orders, inventory              │   │
│  └─────────────────────────────────────────────────────┘   │
│              ↓                                               │
│  ┌──────────────┬──────────────────┬────────────────────┐  │
│  │              │                  │                    │  │
│  ▼              ▼                  ▼                    ▼  │
│ Redis        Flink             PySpark         Elasticsearch │
│ Cache        Real-Time          Batch              Search    │
│ Sessions     Processing         Analysis           Index     │
│ Features     Aggregation        ML Models          Analytics │
│              │                  │                    │       │
│              └──────────────────┬────────────────────┘       │
│                                 ▼                           │
│                      API & Dashboard                        │
│                     (Display Results)                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Architecture

### System Components

1. **Kafka**: Distributed message broker for event streams
2. **Flink**: Real-time stream processing engine
3. **PySpark**: Batch processing for historical analysis
4. **Redis**: In-memory cache for session & feature store
5. **Elasticsearch**: Full-text search and analytics

### Data Flow

```
1. Event Generation (User actions)
        ↓
2. Kafka Publishing (Partitioned by user_id)
        ↓
3. Parallel Processing:
   - Flink: Real-time aggregation (counters, windowed sums)
   - PySpark: Batch ML features (historical trends, scores)
   - Redis: Session caching + lookup acceleration
   - Elasticsearch: Indexing for search and analytics
        ↓
4. API/Dashboard: Query results
```

---

## Part 1: Infrastructure Setup

### Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  # Flink JobManager
  jobmanager:
    image: flink:latest
    ports:
      - "8081:8081"
    environment:
      - FLINK_PROPERTIES=jobmanager.rpc.address=jobmanager

  # Flink TaskManager
  taskmanager:
    image: flink:latest
    depends_on:
      - jobmanager
    environment:
      - FLINK_PROPERTIES=jobmanager.rpc.address=jobmanager
```

Start all services:
```bash
docker-compose up -d
```

---

## Part 2: Complete Application Code

### 1. Event Producer

Create `producer.py`:

```python
from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime
import threading

class EventGenerator:
    """Generate realistic e-commerce events"""
    
    PRODUCTS = ['laptop', 'mouse', 'keyboard', 'monitor', 'headphones', 
                'webcam', 'charger', 'dock', 'cable', 'stand']
    
    REGIONS = ['us-east', 'us-west', 'eu-west', 'ap-south', 'au-east']
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.user_counter = 0
    
    def generate_users(self, num_users=1000):
        """Pre-generate user database"""
        users = []
        for i in range(num_users):
            users.append({
                'user_id': f'user_{i:05d}',
                'name': f'User {i}',
                'region': random.choice(self.REGIONS),
                'tier': random.choice(['bronze', 'silver', 'gold'])
            })
        return users
    
    def generate_event(self, user, event_type):
        """Generate a single event"""
        event = {
            'event_type': event_type,
            'user_id': user['user_id'],
            'user_name': user['name'],
            'user_region': user['region'],
            'user_tier': user['tier'],
            'timestamp': datetime.now().isoformat(),
            'unix_timestamp': int(time.time() * 1000)
        }
        
        if event_type == 'page_view':
            event.update({
                'page': f'/product/{random.choice(self.PRODUCTS)}',
                'session_duration': random.randint(5, 300)
            })
        
        elif event_type == 'add_to_cart':
            event.update({
                'product': random.choice(self.PRODUCTS),
                'quantity': random.randint(1, 5),
                'price': round(random.uniform(20, 2000), 2)
            })
        
        elif event_type == 'purchase':
            products_bought = random.randint(1, 3)
            event.update({
                'products': [random.choice(self.PRODUCTS) for _ in range(products_bought)],
                'total_amount': round(random.uniform(50, 5000), 2),
                'currency': 'USD',
                'payment_method': random.choice(['credit_card', 'paypal', 'apple_pay'])
            })
        
        elif event_type == 'search':
            event.update({
                'search_query': random.choice(['laptop', 'mouse', 'keyboard', 'gaming']),
                'results_count': random.randint(0, 100)
            })
        
        return event
    
    def stream_events(self, duration_minutes=5, events_per_second=10):
        """Stream events to Kafka"""
        users = self.generate_users(100)  # 100 active users
        
        event_types = ['page_view', 'search', 'add_to_cart', 'purchase']
        event_weights = [0.5, 0.2, 0.2, 0.1]  # 50% views, 20% searches, etc.
        
        start_time = time.time()
        event_count = 0
        
        while time.time() - start_time < duration_minutes * 60:
            for _ in range(events_per_second):
                user = random.choice(users)
                event_type = random.choices(event_types, weights=event_weights)[0]
                event = self.generate_event(user, event_type)
                
                # Send to Kafka
                self.producer.send('user_events', value=event, key=user['user_id'].encode())
                event_count += 1
                
                if event_count % 1000 == 0:
                    print(f"[Producer] Generated {event_count} events")
            
            time.sleep(1)  # Emit events_per_second per second
        
        self.producer.close()
        print(f"[Producer] Finished. Total events: {event_count}")

# Run producer
if __name__ == '__main__':
    gen = EventGenerator()
    gen.stream_events(duration_minutes=5, events_per_second=50)
```

---

### 2. Redis Cache Layer

Create `cache_layer.py`:

```python
import redis
import json
from datetime import datetime, timedelta
from functools import wraps

class CacheLayer:
    """Redis-based caching and session management"""
    
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    def cache_user_session(self, user_id, session_data, ttl_hours=24):
        """Store user session"""
        key = f'session:{user_id}'
        self.redis.hset(key, mapping=session_data)
        self.redis.expire(key, ttl_hours * 3600)
    
    def get_user_session(self, user_id):
        """Retrieve user session"""
        key = f'session:{user_id}'
        return self.redis.hgetall(key)
    
    def track_user_activity(self, user_id, event_type):
        """Track user activity for real-time metrics"""
        key = f'activity:{user_id}'
        self.redis.lpush(key, json.dumps({
            'type': event_type,
            'timestamp': datetime.now().isoformat()
        }))
        self.redis.ltrim(key, 0, 99)  # Keep last 100 events
        self.redis.expire(key, 3600)  # Expire after 1 hour
    
    def increment_user_metric(self, user_id, metric_name):
        """Increment metric for user"""
        key = f'metrics:{user_id}:{metric_name}'
        self.redis.incr(key)
        self.redis.expire(key, 86400)  # 24 hour window
    
    def get_user_metrics(self, user_id):
        """Get all metrics for user"""
        pattern = f'metrics:{user_id}:*'
        metrics = {}
        
        for key in self.redis.scan_iter(match=pattern):
            metric_name = key.split(':')[-1]
            metrics[metric_name] = int(self.redis.get(key) or 0)
        
        return metrics
    
    def add_to_leaderboard(self, leaderboard_name, user_id, score):
        """Add/update user in leaderboard"""
        key = f'leaderboard:{leaderboard_name}'
        self.redis.zadd(key, {user_id: score})
        self.redis.expire(key, 86400)
    
    def get_leaderboard_top(self, leaderboard_name, limit=10):
        """Get top N users in leaderboard"""
        key = f'leaderboard:{leaderboard_name}'
        return self.redis.zrevrange(key, 0, limit-1, withscores=True)

# Usage example
if __name__ == '__main__':
    cache = CacheLayer()
    
    # Store session
    cache.cache_user_session('user_0001', {
        'name': 'John Doe',
        'tier': 'gold',
        'last_login': datetime.now().isoformat()
    })
    
    # Get session
    session = cache.get_user_session('user_0001')
    print(f"Session: {session}")
    
    # Track activity
    cache.track_user_activity('user_0001', 'purchase')
    cache.increment_user_metric('user_0001', 'total_purchases')
    
    # Leaderboard
    cache.add_to_leaderboard('daily_spenders', 'user_0001', 999.99)
    top = cache.get_leaderboard_top('daily_spenders', 5)
    print(f"Top spenders: {top}")
```

---

### 3. Real-Time Flink Processor

Create `flink_processor.py`:

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction, ReduceFunction, WindowFunction
from pyflink.datastream.window.time_window import TumblingProcessingTimeWindow, SlidingProcessingTimeWindow
from pyflink.datastream.window.time_window import TimeWindow
from pyflink.common.typeinfo import Types
import json
import time
from datetime import datetime

class EventAggregator:
    """Real-time aggregation of events"""
    
    @staticmethod
    def create_environment():
        env = StreamExecutionEnvironment.get_execution_environment()
        env.set_parallelism(2)
        env.enable_checkpointing(30000)
        return env
    
    @staticmethod
    def process_stream(env):
        """Main stream processing logic"""
        
        # Simulate Kafka source
        events_data = []
        for i in range(100):
            events_data.append({
                'user_id': f'user_{i % 20:05d}',
                'event_type': 'purchase',
                'amount': 100 + (i % 50),
                'timestamp': int(time.time() * 1000)
            })
        
        stream = env.from_collection(
            events_data,
            type_info=Types.MAP(Types.STRING, Types.ANY)
        )
        
        # Extract key-value for aggregation
        keyed_stream = stream \
            .map(lambda x: (x['user_id'], float(x['amount'])), 
                 output_type=Types.TUPLE([Types.STRING, Types.FLOAT])) \
            .key_by(lambda x: x[0])
        
        # Tumbling window aggregation (sum every 10 seconds)
        class SumWindow(WindowFunction):
            def apply(self, key, time_window, inputs, out):
                total = sum(x[1] for x in inputs)
                out.collect(f"User {key[0]}: Total = ${total:.2f}")
        
        result = keyed_stream \
            .window(TumblingProcessingTimeWindow(10000)) \
            .apply(SumWindow(), output_type=Types.STRING)
        
        result.print()
        
        return env

# Usage
if __name__ == '__main__':
    env = EventAggregator.create_environment()
    EventAggregator.process_stream(env)
    # env.execute("Real-Time Analytics")
```

---

### 4. PySpark Batch Processor

Create `spark_processor.py`:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta

class BatchProcessor:
    """Batch analytics and ML features"""
    
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("E-Commerce Analytics") \
            .master("local[*]") \
            .getOrCreate()
    
    def process_daily_analytics(self, events_df):
        """Generate daily analytics"""
        
        # Calculate daily metrics by region and tier
        daily_stats = events_df \
            .filter(col('event_type') == 'purchase') \
            .groupBy('user_region', 'user_tier') \
            .agg(
                count('user_id').alias('transaction_count'),
                sum('total_amount').alias('total_revenue'),
                avg('total_amount').alias('avg_transaction'),
                max('total_amount').alias('max_transaction'),
                approx_percentile('total_amount', 0.5).alias('median_transaction')
            ) \
            .orderBy(desc('total_revenue'))
        
        return daily_stats
    
    def generate_user_features(self, events_df):
        """Generate ML features for users"""
        
        from pyspark.sql.window import Window
        
        # Window for user-level aggregation
        user_window = Window.partitionBy('user_id')
        
        features = events_df \
            .groupBy('user_id', 'user_tier', 'user_region') \
            .agg(
                count('event_type').alias('total_events'),
                countDistinct(when(col('event_type') == 'page_view', col('user_id'))) \
                    .alias('page_view_count'),
                countDistinct(when(col('event_type') == 'purchase', col('user_id'))) \
                    .alias('purchase_count'),
                sum(when(col('event_type') == 'purchase', col('total_amount'))) \
                    .alias('lifetime_value'),
                avg(when(col('event_type') == 'purchase', col('total_amount'))) \
                    .alias('avg_purchase_value'),
            )
        
        return features
    
    def run_batch_job(self, input_path):
        """Main batch processing job"""
        
        # Read events (in real scenario, from Kafka, Parquet, etc.)
        events = self.spark.read.csv(
            input_path,
            header=True,
            inferSchema=True
        )
        
        # Process
        daily_stats = self.process_daily_analytics(events)
        user_features = self.generate_user_features(events)
        
        # Save results
        daily_stats.write.mode('overwrite').parquet('daily_stats')
        user_features.write.mode('overwrite').parquet('user_features')
        
        print("Batch processing complete")
        return daily_stats, user_features

# Usage
if __name__ == '__main__':
    processor = BatchProcessor()
    # processor.run_batch_job('events.csv')
```

---

### 5. Elasticsearch Indexing

Create `es_indexer.py`:

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from datetime import datetime

class ElasticsearchIndexer:
    """Index events and provide search/analytics"""
    
    def __init__(self):
        self.es = Elasticsearch(['http://localhost:9200'])
    
    def create_index(self):
        """Create optimized index"""
        
        settings = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "index": {
                    "codec": "best_compression",
                    "refresh_interval": "30s"
                }
            },
            "mappings": {
                "properties": {
                    "event_type": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "user_name": {"type": "text"},
                    "user_tier": {"type": "keyword"},
                    "user_region": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "unix_timestamp": {"type": "long"},
                    "total_amount": {"type": "float"},
                    "product": {"type": "keyword"},
                    "page": {"type": "keyword"},
                    "search_query": {"type": "text"}
                }
            }
        }
        
        if self.es.indices.exists(index='events'):
            self.es.indices.delete(index='events')
        
        self.es.indices.create(index='events', body=settings)
    
    def index_events_bulk(self, events):
        """Bulk index events"""
        
        actions = [
            {
                "_index": "events",
                "_id": f"{e['user_id']}_{e['unix_timestamp']}",
                "_source": e
            }
            for e in events
        ]
        
        bulk(self.es, actions, chunk_size=1000)
    
    def get_analytics(self):
        """Get analytics aggregations"""
        
        query = {
            "size": 0,
            "aggs": {
                "events_by_type": {
                    "terms": {"field": "event_type", "size": 10}
                },
                "revenue_by_region": {
                    "terms": {"field": "user_region", "size": 10},
                    "aggs": {
                        "total_revenue": {"sum": {"field": "total_amount"}}
                    }
                },
                "revenue_by_tier": {
                    "terms": {"field": "user_tier"},
                    "aggs": {
                        "avg_amount": {"avg": {"field": "total_amount"}}
                    }
                }
            }
        }
        
        result = self.es.search(index='events', body=query)
        return result['aggregations']
    
    def search_events(self, query_text):
        """Full-text search on events"""
        
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["user_name", "search_query", "product"]
                }
            }
        }
        
        return self.es.search(index='events', body=query)
    
    def top_spenders(self, limit=10):
        """Get top spenders"""
        
        query = {
            "size": 0,
            "aggs": {
                "top_users": {
                    "terms": {
                        "field": "user_id",
                        "size": limit,
                        "order": {"total_spent": "desc"}
                    },
                    "aggs": {
                        "total_spent": {"sum": {"field": "total_amount"}}
                    }
                }
            }
        }
        
        result = self.es.search(index='events', body=query)
        
        return [
            {
                "user_id": b['key'],
                "total_spent": b['total_spent']['value']
            }
            for b in result['aggregations']['top_users']['buckets']
        ]

# Usage
if __name__ == '__main__':
    indexer = ElasticsearchIndexer()
    indexer.create_index()
    
    # Index sample events
    events = [
        {
            "event_type": "purchase",
            "user_id": "user_0001",
            "total_amount": 999.99,
            "user_tier": "gold",
            "user_region": "us-east",
            "timestamp": datetime.now().isoformat(),
            "unix_timestamp": int(time.time() * 1000)
        }
    ]
    
    indexer.index_events_bulk(events)
    
    # Get analytics
    analytics = indexer.get_analytics()
    print(json.dumps(analytics, indent=2))
```

---

### 6. Main Orchestration

Create `main_pipeline.py`:

```python
import threading
import time
from producer import EventGenerator
from cache_layer import CacheLayer
from es_indexer import ElasticsearchIndexer
from kafka import KafkaConsumer
import json

class DataPipeline:
    """Orchestrate entire pipeline"""
    
    def __init__(self):
        self.cache = CacheLayer()
        self.indexer = ElasticsearchIndexer()
        self.should_stop = False
    
    def consumer_worker(self):
        """Consume from Kafka and process"""
        
        consumer = KafkaConsumer(
            'user_events',
            bootstrap_servers=['localhost:9092'],
            group_id='pipeline-group',
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=1000
        )
        
        events_buffer = []
        
        for message in consumer:
            event = message.value
            
            # Cache layer: Track user activity
            self.cache.track_user_activity(event['user_id'], event['event_type'])
            
            # Metrics
            if event['event_type'] == 'purchase':
                self.cache.increment_user_metric(
                    event['user_id'],
                    'total_purchases'
                )
                self.cache.add_to_leaderboard(
                    'top_spenders',
                    event['user_id'],
                    event.get('total_amount', 0)
                )
            
            events_buffer.append(event)
            
            # Batch index to Elasticsearch
            if len(events_buffer) >= 100:
                self.indexer.index_events_bulk(events_buffer)
                events_buffer = []
        
        consumer.close()
    
    def run(self):
        """Run entire pipeline"""
        
        print("Starting E-Commerce Analytics Pipeline...")
        
        # Setup Elasticsearch
        print("Setting up Elasticsearch...")
        self.indexer.create_index()
        
        # Start producer in background
        print("Starting event producer...")
        producer_thread = threading.Thread(
            target=self.run_producer,
            daemon=True
        )
        producer_thread.start()
        
        # Give producer time to start
        time.sleep(2)
        
        # Start consumer
        print("Starting consumer...")
        self.consumer_worker()
        
        # Report results
        print("\n=== PIPELINE RESULTS ===\n")
        
        # Redis metrics
        print("Top 5 Spenders (from Redis leaderboard):")
        top_spenders = self.cache.get_leaderboard_top('top_spenders', 5)
        for user, score in top_spenders:
            print(f"  {user}: ${score:.2f}")
        
        # Elasticsearch analytics
        print("\nAnalytics (from Elasticsearch):")
        analytics = self.indexer.get_analytics()
        
        print("Events by type:")
        for bucket in analytics['events_by_type']['buckets']:
            print(f"  {bucket['key']}: {bucket['doc_count']}")
        
        print("\nTop spenders (ES):")
        top_es = self.indexer.top_spenders(5)
        for record in top_es:
            print(f"  {record['user_id']}: ${record['total_spent']:.2f}")
    
    def run_producer(self):
        """Run event producer"""
        gen = EventGenerator()
        gen.stream_events(duration_minutes=2, events_per_second=50)

if __name__ == '__main__':
    pipeline = DataPipeline()
    pipeline.run()
```

---

## Part 3: Running the Complete Demo

```bash
# 1. Start all services
docker-compose up -d

# 2. Create Kafka topics
docker exec -it kafka kafka-topics --create --topic user_events \
  --bootstrap-server localhost:9092 --partitions 3

# 3. Run the pipeline
python main_pipeline.py
```

---

## Expected Output

```
=== PIPELINE RESULTS ===

Top 5 Spenders (from Redis leaderboard):
  user_00042: $4995.50
  user_00018: $4850.75
  user_00076: $4720.30
  user_00051: $4680.90
  user_00003: $4520.45

Analytics (from Elasticsearch):
Events by type:
  page_view: 2500
  search: 1000
  add_to_cart: 800
  purchase: 200

Top spenders (ES):
  user_00042: $4995.50
  user_00018: $4850.75
  user_00076: $4720.30
  user_00051: $4680.90
  user_00003: $4520.45
```

---

## Part 4: Extensions & Advanced Features

### 1. Add Real-Time Notifications

```python
def send_notification(user_id, message):
    """Send real-time notification"""
    pubsub_key = f'notifications:{user_id}'
    cache.redis.publish(pubsub_key, json.dumps({
        'message': message,
        'timestamp': datetime.now().isoformat()
    }))
```

### 2. Anomaly Detection

```python
def detect_anomalies(event):
    """Detect unusual patterns"""
    
    # Get user's average purchase amount
    user_avg = cache.redis.get(f'user_avg_purchase:{event["user_id"]}')
    
    if event['total_amount'] > float(user_avg) * 5:
        # Potential fraud
        return True
    
    return False
```

### 3. Real-Time Recommendations

```python
def get_recommendations(user_id):
    """Get real-time product recommendations"""
    
    # Get user's recent purchases
    recent = cache.redis.lrange(f'user_purchases:{user_id}', 0, 10)
    
    # Query ES for similar products purchased by similar users
    query = {
        "query": {"match": {"product": recent[0]}}
    }
    
    results = indexer.es.search(index='events', body=query)
    return results
```

---

## Performance Metrics

Expected metrics after running the pipeline:

| Metric | Value |
|--------|-------|
| Events/sec | ~50 |
| Kafka Latency | <100ms |
| Redis Latency | <5ms |
| Elasticsearch Index Latency | <500ms |
| Total Throughput | ~40 MB/s |

---

## Summary: 5-Day Learning Journey

**Day 1**: Foundations and Setup
- Redis basics, Flink architecture, Spark RDDs, Elasticsearch search, Kafka pub/sub

**Day 2**: Advanced Concepts
- Redis streams & transactions, Flink windowing, Spark SQL, ES aggregations, Kafka offsets

**Day 3**: System Integration
- Building Kafka-Redis-ES pipelines, Flink-Spark batch/stream, end-to-end architectures

**Day 4**: Performance Optimization
- Memory tuning, parallelism, caching strategies, query optimization

**Day 5**: Real-World Application
- Comprehensive e-commerce analytics platform using all five technologies

---

## Key Takeaways

1. **Kafka** = Event backbone, provides scalable pub/sub
2. **Flink** = Real-time processing, windowing, stateful operations
3. **PySpark** = Batch analytics, ML features, distributed computing
4. **Redis** = High-speed caching, sessions, leaderboards
5. **Elasticsearch** = Full-text search, analytics, aggregations

---

## Next Steps for Production

1. **Add authentication/security** (SSL, OAuth)
2. **Implement monitoring** (Prometheus, Grafana)
3. **Setup alerting** (PagerDuty, Slack)
4. **Add data lineage** (Apache Atlas)
5. **Implement governance** (data catalogs, access control)
6. **Scale horizontally** (Kubernetes orchestration)
7. **Add ML models** (feature store, model serving)
8. **Setup DR/HA** (replication, failover)

---

## Congratulations!

You've completed a comprehensive 5-day journey covering intermediate-to-advanced topics in:
- Apache Kafka
- Apache Flink
- PySpark
- Elasticsearch
- Redis

You can now design and build real-time data pipelines for production environments!

---

## Further Learning Resources

1. **Kafka**: Confluent documentation, Kafka Streams programming
2. **Flink**: Flink SQL, CEP (Complex Event Processing)
3. **Spark**: MLlib (ML), Spark Structured Streaming
4. **Elasticsearch**: Kibana dashboards, X-Pack features
5. **Redis**: Redis Cluster, Redis Sentinel, Modules

