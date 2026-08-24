# Day 2: Advanced Topics & Integration

## Time Allocation: 2-3 hours total (40 min per technology + 20 min integration planning)

---

# Redis: Advanced Data Types & Transactions

## Time Allocation: 40 minutes

### 1. Redis Streams (Event Log)

Streams are like logs that store time-ordered events. Perfect for message queues and event sourcing.

```python
import redis
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# XADD: Add entry to stream
stream_key = 'user:actions'

# Automatically generates ID based on timestamp
id1 = r.xadd(stream_key, {'user': 'alice', 'action': 'login'})
id2 = r.xadd(stream_key, {'user': 'bob', 'action': 'purchase', 'amount': '99.99'})
id3 = r.xadd(stream_key, {'user': 'alice', 'action': 'logout'})

print(f"Added entries with IDs: {id1}, {id2}, {id3}")

# XRANGE: Get range of entries
entries = r.xrange(stream_key)
for entry_id, entry_data in entries:
    print(f"ID: {entry_id}, Data: {entry_data}")

# XREAD: Read entries from multiple streams
# Great for consumer patterns
entries = r.xread({stream_key: '0'}, count=2)
for stream, data in entries:
    for entry_id, entry_data in data:
        print(f"Stream: {stream}, Entry: {entry_id}, Data: {entry_data}")

# XLEN: Get length
length = r.xlen(stream_key)
print(f"Stream length: {length}")

# XREVRANGE: Get in reverse order
latest = r.xrevrange(stream_key, count=1)
print(f"Latest: {latest}")

# XDEL: Delete entry
r.xdel(stream_key, id1)
```

### 2. Transactions (MULTI/EXEC)

Execute multiple commands as atomic operation - all or nothing.

```python
# Transaction: Transfer money between accounts
def transfer_money(from_account, to_account, amount):
    pipe = r.pipeline()
    
    try:
        pipe.watch(from_account)  # Watch account for changes
        
        # Check balance
        balance = r.get(from_account)
        if int(balance) < amount:
            print("Insufficient funds")
            return False
        
        # Multi: Start transaction
        pipe.multi()
        
        # Queue commands
        pipe.decrby(from_account, amount)  # Reduce balance
        pipe.incrby(to_account, amount)    # Increase balance
        r.lpush(f"{from_account}:history", f"transfer -{amount} to {to_account}")
        
        # Exec: Execute all commands atomically
        pipe.execute()
        print(f"Transferred ${amount} from {from_account} to {to_account}")
        return True
    except redis.WatchError:
        print("Transaction failed - account was modified")
        return False

# Usage
r.set('alice:balance', 1000)
r.set('bob:balance', 500)

transfer_money('alice:balance', 'bob:balance', 100)
print(f"Alice: ${r.get('alice:balance')}")
print(f"Bob: ${r.get('bob:balance')}")
```

### 3. Pub/Sub (Publish/Subscribe)

Real-time messaging pattern. Publishers send messages to channels, subscribers receive them.

```python
import threading
import time

# Subscriber
def subscriber_thread():
    r_sub = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r_sub.pubsub()
    
    # Subscribe to channel
    pubsub.subscribe('notifications')
    print("Subscriber listening on 'notifications' channel...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"[NOTIFICATION] {message['data']}")

# Start subscriber in background thread
sub_thread = threading.Thread(target=subscriber_thread, daemon=True)
sub_thread.start()

time.sleep(1)  # Let subscriber start

# Publisher
for i in range(3):
    message = f"Alert {i}: System update available"
    r.publish('notifications', message)
    print(f"Published: {message}")
    time.sleep(0.5)

time.sleep(1)
```

### 4. Persistence Mechanisms

**RDB (Snapshots)**: Periodic snapshots of database
```
BGSAVE command → Fork process → Write to disk asynchronously
```

**AOF (Append-Only File)**: Log every write operation
```
Every write → Append to AOF file → Sync to disk (fsync)
```

```python
# Force persistence
r.bgsave()  # Background save (RDB)
print("Background save initiated")

# Get info
info = r.info()
print(f"Last save time: {info['last_save_time']}")
```

---

# Apache Flink: DataStream API & Windowing

## Time Allocation: 40 minutes

### 1. DataStream Transformations

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction, FilterFunction, FlatMapFunction, KeyedProcessFunction
from pyflink.common.typeinfo import Types
from pyflink.datastream.window.window import TimeWindow

# Create environment
env = StreamExecutionEnvironment.get_execution_environment()

# Map: Transform each element
stream = env.from_collection([1, 2, 3, 4, 5])
mapped = stream.map(lambda x: x * 2)

# Filter: Keep elements matching condition
filtered = stream.filter(lambda x: x > 2)

# FlatMap: Map then flatten (can produce 0 or more outputs)
def tokenize(line):
    return line.split()

text_stream = env.from_collection(["hello world", "hello flink"])
words = text_stream.flat_map(tokenize, output_type=Types.STRING)

# Key operations
def process(element):
    return (element % 3, element)  # Group by modulo 3

keyed = stream.map(process, output_type=Types.TUPLE([Types.INT, Types.INT])) \
    .key_by(lambda x: x[0])  # Key by first element (group)
```

### 2. Windowing

**Tumbling Windows**: Fixed non-overlapping windows

```python
from pyflink.datastream.window.time_window import TimeWindow, TumblingProcessingTimeWindow
from pyflink.datastream.functions import ReduceFunction

class Adder(ReduceFunction):
    def reduce(self, v1, v2):
        return v1 + v2

# Stream of integers arriving at different times
stream = env.from_collection([(1, 100), (2, 200), (3, 150), (4, 175)])

result = stream.window_all(TumblingProcessingTimeWindow(5000)) \
    .reduce(Adder())

result.print()
```

**Sliding Windows**: Overlapping windows

```python
from pyflink.datastream.window.time_window import SlidingProcessingTimeWindow

# Window size: 10 seconds, Slide: 5 seconds (50% overlap)
result = stream.window_all(SlidingProcessingTimeWindow(10000, 5000)) \
    .reduce(Adder())
```

### 3. Stateful Processing

```python
from pyflink.datastream.functions import KeyedProcessFunction

class StatefulCounter(KeyedProcessFunction):
    def __init__(self):
        self.state = None
    
    def open(self, runtime_context):
        # Initialize state
        from pyflink.datastream.state import ValueState, ValueStateDescriptor
        from pyflink.common.typeinfo import Types
        
        descriptor = ValueStateDescriptor(
            "count_state",
            Types.INT
        )
        self.state = runtime_context.get_state(descriptor)
    
    def process_element(self, element, ctx):
        # Get current count
        current = self.state.value()
        if current is None:
            current = 0
        
        # Increment
        current += 1
        self.state.update(current)
        
        yield (element, current)

# Usage
stream = env.from_collection([('A', 1), ('B', 2), ('A', 3), ('B', 4), ('A', 5)])
keyed_stream = stream.key_by(lambda x: x[0])
result = keyed_stream.process(StatefulCounter())
```

### 4. Checkpointing (Fault Tolerance)

```python
# Enable checkpointing
env.enable_checkpointing(60000)  # Checkpoint every 60 seconds

# Configure checkpoint mode
from pyflink.datastream.checkpoint_mode import CheckpointingMode
env.get_checkpoint_config().set_checkpoint_mode(CheckpointingMode.EXACTLY_ONCE)

# Configure tolerated checkpoint failure
env.get_checkpoint_config().set_tolerable_checkpoint_failure_number(1)

# Configure minimum pause between checkpoints
env.get_checkpoint_config().set_min_pause_between_checkpoints(30000)

# Configure timeout for checkpoints
env.get_checkpoint_config().set_checkpoint_timeout(600000)
```

---

# PySpark: DataFrames & SQL Queries

## Time Allocation: 40 minutes

### 1. DataFrame Operations Advanced

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.appName("AdvancedDF").master("local[2]").getOrCreate()

# Create sample data
data = [
    (1, "Alice", 25, "USA", 50000),
    (2, "Bob", 30, "USA", 60000),
    (3, "Carol", 28, "Canada", 55000),
    (4, "David", 35, "USA", 70000),
    (5, "Eve", 26, "Canada", 52000),
]

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("country", StringType(), True),
    StructField("salary", DoubleType(), True)
])

df = spark.createDataFrame(data, schema)

# UDF: User Defined Function
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(returnType=StringType())
def salary_bracket(salary):
    if salary < 55000:
        return "Low"
    elif salary < 65000:
        return "Medium"
    else:
        return "High"

df_with_bracket = df.withColumn("bracket", salary_bracket(col("salary")))
df_with_bracket.show()

# Window Functions
from pyspark.sql.window import Window

window_spec = Window.partitionBy("country").orderBy(col("salary").desc())

df_ranked = df.withColumn(
    "rank_by_salary",
    row_number().over(window_spec)
)
df_ranked.show()

# Aggregations
df.groupBy("country").agg(
    count("*").alias("count"),
    avg("salary").alias("avg_salary"),
    max("salary").alias("max_salary"),
    min("age").alias("min_age")
).show()

# Join
departments = spark.createDataFrame([
    (1, "Engineering"),
    (2, "Sales"),
    (3, "Engineering"),
], ["id", "department"])

df_joined = df.join(departments, "id", "left")
df_joined.show()
```

### 2. SQL Queries

```python
# Register DataFrame as SQL table
df.createOrReplaceTempView("employees")

# Run SQL queries
result = spark.sql("""
    SELECT country, 
           COUNT(*) as count,
           AVG(salary) as avg_salary,
           MAX(salary) as max_salary
    FROM employees
    WHERE age >= 25
    GROUP BY country
    HAVING COUNT(*) > 1
    ORDER BY avg_salary DESC
""")

result.show()

# Complex queries with CTE (Common Table Expression)
result = spark.sql("""
    WITH ranked AS (
        SELECT *, 
               ROW_NUMBER() OVER (PARTITION BY country ORDER BY salary DESC) as rank
        FROM employees
    )
    SELECT name, country, salary, rank
    FROM ranked
    WHERE rank <= 2
""")

result.show()
```

### 3. Structured Streaming

```python
# Read streaming data from socket
lines = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

# Transform
words = lines.select(
    explode(split(col("value"), " ")).alias("word")
)

word_counts = words.groupBy("word").count()

# Write stream
query = word_counts.writeStream \
    .format("console") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start()

query.awaitTermination()
```

---

# Elasticsearch: Advanced Queries & Aggregations

## Time Allocation: 40 minutes

### 1. Advanced Query Types

```python
from elasticsearch import Elasticsearch
import json

es = Elasticsearch(["http://localhost:9200"])

# Bool Query: Complex boolean logic
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"category": "electronics"}}
            ],
            "should": [
                {"term": {"brand": "samsung"}},
                {"term": {"brand": "apple"}}
            ],
            "filter": [
                {"range": {"price": {"gte": 100, "lte": 1000}}}
            ],
            "must_not": [
                {"term": {"status": "discontinued"}}
            ]
        }
    }
}

result = es.search(index="products", body=query)
for hit in result['hits']['hits']:
    print(hit['_source'])

# Fuzzy Query: Handle typos
query = {
    "query": {
        "fuzzy": {
            "name": {
                "value": "laptpo",  # Typo
                "fuzziness": "AUTO"
            }
        }
    }
}

# Range Query with dates
query = {
    "query": {
        "range": {
            "created_at": {
                "gte": "2024-01-01",
                "lte": "2024-12-31",
                "format": "yyyy-MM-dd"
            }
        }
    }
}

# Wildcard Query
query = {
    "query": {
        "wildcard": {
            "email": "*@example.com"
        }
    }
}

# Regex Query
query = {
    "query": {
        "regexp": {
            "email": ".*@(gmail|yahoo)\\.com"
        }
    }
}
```

### 2. Advanced Aggregations

```python
# Nested aggregations
query = {
    "size": 0,
    "aggs": {
        "by_category": {
            "terms": {"field": "category", "size": 10},
            "aggs": {
                "by_brand": {
                    "terms": {"field": "brand", "size": 5},
                    "aggs": {
                        "avg_price": {"avg": {"field": "price"}},
                        "price_range": {"range": {
                            "field": "price",
                            "ranges": [
                                {"to": 100},
                                {"from": 100, "to": 500},
                                {"from": 500}
                            ]
                        }}
                    }
                },
                "price_stats": {"stats": {"field": "price"}}
            }
        }
    }
}

result = es.search(index="products", body=query)

# Parse nested results
for category in result['aggregations']['by_category']['buckets']:
    print(f"Category: {category['key']} ({category['doc_count']} items)")
    for brand in category['by_brand']['buckets']:
        print(f"  Brand: {brand['key']} - Avg Price: ${brand['avg_price']['value']}")
```

### 3. Analyzers & Text Analysis

```python
# Create index with custom analyzer
mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "custom_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop", "porter_stem"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "custom_analyzer"
            },
            "description": {
                "type": "text",
                "analyzer": "standard"
            }
        }
    }
}

es.indices.create(index="articles", body=mapping)

# Analyze API: Test analyzer
result = es.indices.analyze(index="articles", body={
    "analyzer": "custom_analyzer",
    "text": "The quick brown foxes are running quickly"
})

for token in result['tokens']:
    print(token['token'])
```

---

# Kafka: Consumer Groups & Offsets

## Time Allocation: 40 minutes

### 1. Consumer Group Management

```python
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
import json

# Admin client
admin = KafkaAdminClient(bootstrap_servers=['localhost:9092'])

# Create topic with multiple partitions
topic = NewTopic(name='events', num_partitions=4, replication_factor=1)
admin.create_topics([topic])

# Consumer group 1: 2 consumers for 4 partitions
consumer1_a = KafkaConsumer(
    'events',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-team',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

consumer1_b = KafkaConsumer(
    'events',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-team',  # Same group
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Each consumer gets subset of partitions
print(f"Consumer A partitions: {consumer1_a.assignment()}")
print(f"Consumer B partitions: {consumer1_b.assignment()}")

# Partitions are distributed evenly
```

### 2. Offset Management

```python
# Auto offset commit
consumer = KafkaConsumer(
    'events',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-team',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,  # Commit every 5 seconds
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Manual offset management
consumer_manual = KafkaConsumer(
    'events',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-team-manual',
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer_manual:
    try:
        event = message.value
        print(f"Processing: {event}")
        
        # Process...
        
        # Manually commit only after successful processing
        consumer_manual.commit()
    except Exception as e:
        print(f"Error: {e}, offset will be retried")
        # Don't commit, will retry

# Get current offset
consumer.position(consumer.assignment())

# Seek to specific offset
from kafka.structs import TopicPartition
tp = TopicPartition('events', 0)
consumer.seek(tp, 0)  # Seek to offset 0 of partition 0
```

### 3. Producer Partitioning Strategy

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 1. No key: Round-robin across partitions
producer.send('events', value={"type": "click"})
producer.send('events', value={"type": "purchase"})

# 2. Same key: Always goes to same partition (for ordering)
# All events for user_123 go to partition 2
producer.send('events', key='user_123', value={"type": "click", "user": "user_123"})
producer.send('events', key='user_123', value={"type": "purchase", "user": "user_123"})

# All events for user_456 go to partition 1  
producer.send('events', key='user_456', value={"type": "click", "user": "user_456"})

# 3. Custom partitioner
class LocationPartitioner:
    def __call__(self, key, all_partitions, available_partitions):
        if key == b'usa':
            return all_partitions[0]
        elif key == b'eu':
            return all_partitions[1]
        else:
            return all_partitions[2]

producer_custom = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    partitioner=LocationPartitioner
)

producer_custom.send('events', key='usa', value={"region": "usa", "users": 1000})
producer_custom.send('events', key='eu', value={"region": "eu", "users": 800})

producer.close()
producer_custom.close()
```

---

## Integration Planning for Day 3

```
Real-Time Analytics Pipeline:
┌─────────────┐
│   Kafka     │ (Event Stream: User actions)
└──────┬──────┘
       │
   ┌───┴───────────────────┐
   │                       │
┌──▼──────────┐    ┌──────▼───┐
│ Flink       │    │ Spark    │
│ Processing  │    │ Batch    │
└──┬──────────┘    └────┬─────┘
   │                    │
   │             ┌──────▼─────┐
   │             │Redis Cache │
   │             └─────────────┘
   │
   └──────┬──────────────────┐
          │                  │
       ┌──▼──┐          ┌───▼────┐
       │ES   │          │Database│
       │Index│          │Storage │
       └─────┘          └────────┘
```

---

## Review Questions

1. When would you use Redis Streams vs Pub/Sub?
2. How does Flink's windowing handle late-arriving data?
3. What are the trade-offs between RDD and DataFrame in Spark?
4. When should you use Elasticsearch over traditional databases?
5. How do Kafka partitions enable parallelism?

---

## Next Steps: Day 3
- Interconnect all systems
- Build unified architecture
- Handle data transformations across systems
