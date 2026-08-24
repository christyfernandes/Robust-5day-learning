# Day 4: Performance Optimization & Advanced Patterns

## Time Allocation: 2-3 hours total (optimization for each system)

---

## Redis: Performance Tuning & Scaling

### 1. Memory Management & Optimization

```python
import redis
from redis.cluster import RedisCluster
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Check memory usage
info = r.info('memory')
print(f"Memory used: {info['used_memory_human']}")
print(f"Memory peak: {info['used_memory_peak_human']}")
print(f"Memory fragmentation: {info['mem_fragmentation_ratio']}")

# Optimization 1: Use appropriate data structures
# WRONG: Store list as JSON string
r.set('items', '["item1", "item2", "item3"]')  # Stores as single string

# RIGHT: Use Redis list
r.lpush('items_list', 'item1', 'item2', 'item3')  # Better memory efficiency

# Optimization 2: Set expiration on all keys
r.set('session:123', 'data', ex=3600)  # Expire after 1 hour

# Optimization 3: Use compression for large values
import json
import zlib

def store_compressed(key, data):
    json_str = json.dumps(data)
    compressed = zlib.compress(json_str.encode('utf-8'))
    r.set(key, compressed)

def get_compressed(key):
    compressed = r.get(key)
    if compressed:
        return json.loads(zlib.decompress(compressed).decode('utf-8'))
    return None

large_data = {'items': list(range(1000))}
store_compressed('large_data', large_data)
result = get_compressed('large_data')

# Optimization 4: Batching operations
pipe = r.pipeline()
for i in range(1000):
    pipe.set(f'key:{i}', f'value:{i}')
pipe.execute()  # Single round-trip

# Optimization 5: Use SCAN instead of KEYS
# WRONG: blocks entire server
# keys = r.keys('user:*')

# RIGHT: iterate using cursor
cursor = 0
keys_batch = []
while True:
    cursor, keys = r.scan(cursor, match='user:*', count=100)
    keys_batch.extend(keys)
    if cursor == 0:
        break
print(f"Found {len(keys_batch)} keys")
```

### 2. Redis Cluster & Replication

```python
# Cluster example (requires cluster setup)
nodes = [
    {"host": "localhost", "port": 7000},
    {"host": "localhost", "port": 7001},
    {"host": "localhost", "port": 7002},
]

# This would connect to Redis Cluster
# rc = RedisCluster(startup_nodes=nodes)

# Replication for high availability
# Master-Slave setup:
# Master (port 6379) → Slave (port 6380)

# Connect to master
master = redis.Redis(host='localhost', port=6379)

# Connect to slave (read-only)
slave = redis.Redis(host='localhost', port=6380)

# Write to master
master.set('data', 'value')

# Read from slave (eventually consistent)
time.sleep(0.1)  # Wait for replication
value = slave.get('data')

print(f"Master: {master.get('data')}")
print(f"Slave: {slave.get('data')}")

# Check replication info
master_info = master.info('replication')
print(f"Role: {master_info['role']}")  # 'master'
print(f"Connected slaves: {master_info['connected_slaves']}")
```

### 3. Pipelining vs MULTI/EXEC

```python
import time

# Test 1: Individual commands (slowest)
def individual_commands():
    for i in range(1000):
        r.set(f'key:{i}', f'value:{i}')

# Test 2: Pipelining (fast)
def pipelining():
    pipe = r.pipeline()
    for i in range(1000):
        pipe.set(f'key:{i}', f'value:{i}')
    pipe.execute()

# Test 3: MULTI/EXEC (atomic)
def transaction():
    pipe = r.pipeline(transaction=True)
    for i in range(1000):
        pipe.set(f'key:{i}', f'value:{i}')
    pipe.execute()

# Benchmark
start = time.time()
individual_commands()
print(f"Individual: {time.time() - start:.2f}s")

start = time.time()
pipelining()
print(f"Pipelining: {time.time() - start:.2f}s")

start = time.time()
transaction()
print(f"Transaction: {time.time() - start:.2f}s")
```

---

## Apache Flink: Performance Optimization

### 1. Parallelism Configuration

```python
from pyflink.datastream import StreamExecutionEnvironment

env = StreamExecutionEnvironment.get_execution_environment()

# Global parallelism
env.set_parallelism(8)  # Process on 8 parallel tasks

# Stream with custom parallelism
stream = env.read_text_file('input.txt') \
    .set_parallelism(4) \
    .map(lambda x: x.upper()).set_parallelism(8) \
    .filter(lambda x: len(x) > 5).set_parallelism(4)

# Resource configuration
configuration = env.get_config()
configuration.set_max_parallelism(32)

print(f"Parallelism: {env.get_parallelism()}")
```

### 2. Checkpointing Strategy

```python
from pyflink.datastream.checkpoint_mode import CheckpointingMode

env = StreamExecutionEnvironment.get_execution_environment()

# Enable checkpointing
env.enable_checkpointing(60000)  # Every 60 seconds

# Checkpoint configuration
checkpoint_config = env.get_checkpoint_config()

# Exactly-once processing
checkpoint_config.set_checkpoint_mode(CheckpointingMode.EXACTLY_ONCE)

# Minimum pause between checkpoints (to avoid too frequent checkpointing)
checkpoint_config.set_min_pause_between_checkpoints(30000)

# Checkpoint timeout (fail if not completed in time)
checkpoint_config.set_checkpoint_timeout(600000)

# Maximum concurrent checkpoints
checkpoint_config.set_max_concurrent_checkpoints(1)

# Enable external checkpoints
checkpoint_config.enable_external_checkpoints()

# Fail job if checkpoint fails
checkpoint_config.set_fail_on_checkpointing_errors(True)

print("Checkpointing configured for high reliability")
```

### 3. Memory Configuration

```python
# Job configuration
config = env.get_config()

# Set per-job memory
# framework memory: JVM overhead
# task manager memory: total memory per task manager

# Example flink-conf.yaml:
# taskmanager.memory.flink.size: 1408m
# taskmanager.memory.jvm-overhead.fraction: 0.1
# taskmanager.memory.managed.fraction: 0.4

# Operator-specific optimization
class OptimizedMapper:
    def __init__(self):
        self.lookup = {}  # Cache for expensive lookups
    
    def map_element(self, element):
        if element not in self.lookup:
            # Expensive operation
            self.lookup[element] = expensive_computation(element)
        return self.lookup[element]

def expensive_computation(x):
    # Simulate expensive lookup
    import time
    time.sleep(0.001)
    return x.upper()
```

### 4. Windowing Best Practices

```python
# Small windows for low latency
stream.window_all(TumblingProcessingTimeWindow(1000)) \
    .reduce(sum_function)

# Large windows for throughput (fewer checkpoints)
stream.window_all(TumblingProcessingTimeWindow(60000)) \
    .reduce(sum_function)

# Session windows for event-driven processing
from pyflink.datastream.window.session_window import EventTimeSessionWindow

stream.key_by(lambda x: x[0]) \
    .window(EventTimeSessionWindow(gap=10000)) \
    .reduce(sum_function)
```

---

## PySpark: Performance Optimization

### 1. Partitioning Strategy

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("SparkOptimization") \
    .config("spark.sql.shuffle.partitions", "200") \
    .master("local[*]").getOrCreate()

df = spark.read.csv("data.csv", header=True)

# Check current partitions
print(f"Partitions: {df.rdd.getNumPartitions()}")

# Repartition for more parallelism
df_repartitioned = df.repartition(32)  # Shuffle to 32 partitions

# Partition by column (range-based)
df_partitioned = df.repartitionByRange(8, 'user_id')

# Coalesce: Reduce partitions without shuffle
df_coalesced = df.coalesce(4)  # Combine partitions

# Bucketing for join optimization
df.write \
    .bucketBy(10, 'user_id') \
    .mode('overwrite') \
    .parquet('bucketed_data')

df_bucketed = spark.read.parquet('bucketed_data')
# Now joins on user_id will be much faster
```

### 2. Caching & Persistence

```python
# Cache dataframe in memory
df.cache()  # Or df.persist()

# Trigger action to materialize cache
df.count()

# Check cache
df.explain()

# Remove from cache
df.unpersist()

# Different storage levels
from pyspark import StorageLevel

df.persist(StorageLevel.MEMORY_ONLY)
df.persist(StorageLevel.MEMORY_AND_DISK)
df.persist(StorageLevel.DISK_ONLY)
```

### 3. Query Optimization

```python
# Catalyst optimizer automatically optimizes

# But you can help it:
# 1. Use DataFrames/SQL (not RDDs)
# 2. Push filters down
df.filter(col('amount') > 100) \
    .select('name', 'amount')

# 3. Use columnar format
df.write.parquet('data.parquet')
df_parquet = spark.read.parquet('data.parquet')

# 4. Avoid UDFs if possible (use built-in functions)
# SLOW:
@udf(returnType=StringType())
def slow_func(s):
    return s.lower()

df.withColumn('lower_name', slow_func(col('name')))

# FAST:
df.withColumn('lower_name', lower(col('name')))

# 5. Use broadcast for small tables
from pyspark.sql.functions import broadcast

small_df = spark.read.csv('small.csv')
large_df = spark.read.csv('large.csv')

result = large_df.join(broadcast(small_df), 'user_id')
```

### 4. Debugging & Metrics

```python
# Check execution plan
df.explain(mode='extended')

# Get metrics
from pyspark.sql import SparkSession
spark.sparkContext.addFile('your_module.py')

# Monitor in Spark UI (http://localhost:4040)

# Check stage info
spark.sparkContext.statusTracker().getExecutorInfos()

# Application metrics
sc = spark.sparkContext
print(f"Default parallelism: {sc.defaultParallelism}")
print(f"Default min partitions: {sc.defaultMinPartitions}")
```

---

## Elasticsearch: Query & Indexing Performance

### 1. Index Optimization

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

# Create index with optimization settings
settings = {
    "settings": {
        "number_of_shards": 5,        # For large indices
        "number_of_replicas": 1,       # For availability
        "index": {
            "codec": "best_compression",  # Trade CPU for space
            "refresh_interval": "30s"     # Less frequent refresh
        }
    },
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "user_id": {"type": "keyword"},  # Exact match, not analyzed
            "message": {"type": "text"},    # Full-text search
            "tags": {"type": "keyword"}
        }
    }
}

es.indices.create(index='optimized', body=settings)

# Disable refresh during bulk indexing
es.indices.put_settings(index='optimized', body={
    "settings": {"index.refresh_interval": "-1"}
})

# Bulk index
from elasticsearch.helpers import bulk

actions = [
    {"_index": "optimized", "_id": i, "_source": {"value": i}}
    for i in range(10000)
]

bulk(es, actions, chunk_size=500)

# Re-enable refresh
es.indices.put_settings(index='optimized', body={
    "settings": {"index.refresh_interval": "1s"}
})
```

### 2. Query Optimization

```python
# Use filter context (cached) vs query context

# SLOW: Uses score calculation
query_slow = {
    "query": {
        "bool": {
            "must": [
                {"match": {"user_id": "123"}},
                {"range": {"date": {"gte": "2024-01-01"}}}
            ]
        }
    }
}

# FASTER: Filter context (no scoring, cached)
query_fast = {
    "query": {
        "bool": {
            "filter": [
                {"term": {"user_id": "123"}},
                {"range": {"date": {"gte": "2024-01-01"}}}
            ]
        }
    }
}

# Use post_filter only if necessary (applied after aggregations)

# Limit result size
query = {
    "query": {"match_all": {}},
    "size": 100,  # Don't fetch all
    "from": 0
}

# Use scroll for large result sets
response = es.search(index='events', body={
    "query": {"match_all": {}},
    "size": 1000,
    "scroll": "5m"
})

scroll_id = response['_scroll_id']
for _ in range(10):
    response = es.scroll(scroll_id=scroll_id, scroll='5m')
    if not response['hits']['hits']:
        break
```

### 3. Aggregation Optimization

```python
# Filter before aggregating
query = {
    "query": {
        "range": {"timestamp": {"gte": "2024-01-01"}}
    },
    "size": 0,
    "aggs": {
        "by_user": {
            "terms": {"field": "user_id", "size": 100}
        }
    }
}

# Use composite aggregation for pagination
query = {
    "aggs": {
        "products": {
            "composite": {
                "sources": [{"product": {"terms": {"field": "product_id"}}}],
                "size": 100
            }
        }
    }
}
```

---

## Kafka: Throughput & Latency Optimization

### 1. Producer Tuning

```python
from kafka import KafkaProducer
import time

# Optimized producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    
    # Batching
    batch_size=32768,          # Batch size in bytes
    linger_ms=100,             # Wait max 100ms to fill batch
    
    # Compression
    compression_type='snappy',  # Or 'gzip', 'lz4'
    
    # Buffer
    buffer_memory=67108864,    # 64MB buffer
    
    # Threads
    max_in_flight_requests_per_connection=5,
    
    # Timeouts
    request_timeout_ms=30000,
    
    acks='all',                # Wait for all replicas
    retries=3
)

# Send messages
for i in range(10000):
    future = producer.send('events', value=str(i).encode())
    # Callbacks for failure handling
    future.add_callback(lambda x: print(f"Sent: {x.topic()}"))
    future.add_errback(lambda x: print(f"Error: {x}"))

producer.flush()  # Wait for all sends
producer.close()
```

### 2. Consumer Tuning

```python
consumer = KafkaConsumer(
    'events',
    bootstrap_servers=['localhost:9092'],
    group_id='optimized-group',
    
    # Fetching
    max_poll_records=500,      # Fetch up to 500 records
    fetch_min_bytes=1024,      # Wait for at least 1KB
    fetch_max_wait_ms=500,     # Or 500ms
    
    # Session
    session_timeout_ms=30000,
    heartbeat_interval_ms=10000,
    
    # Offset
    auto_offset_reset='latest',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,
    
    value_deserializer=lambda x: x.decode('utf-8')
)

# Process in batches for efficiency
for messages in consumer:
    batch = [messages]
    for _ in range(499):
        try:
            msg = consumer.poll(timeout_ms=100)
            if msg:
                batch.extend(msg.values())
        except StopIteration:
            break
    
    # Process entire batch at once
    process_batch(batch)
```

### 3. Partitioning & Replication

```python
from kafka.admin import NewTopic

# Create topic with optimization
topic = NewTopic(
    name='high-throughput',
    num_partitions=12,         # Match CPU cores
    replication_factor=3,      # High availability
    topic_configs={
        'compression.type': 'snappy',
        'retention.ms': str(7 * 24 * 3600 * 1000),  # 7 days
        'min.insync.replicas': '2'
    }
)
```

---

## Performance Monitoring Dashboard

```python
import time
import json

class PipelineMonitor:
    def __init__(self):
        self.metrics = {
            'redis': {},
            'kafka': {},
            'flink': {},
            'spark': {},
            'elasticsearch': {}
        }
    
    def monitor_redis(self, r):
        info = r.info()
        self.metrics['redis'] = {
            'memory_used_mb': info['used_memory'] / 1024 / 1024,
            'commands_per_sec': info['instantaneous_ops_per_sec'],
            'connected_clients': info['connected_clients'],
            'evicted_keys': info.get('evicted_keys', 0)
        }
    
    def monitor_kafka(self, admin_client):
        # Get broker metrics
        # cluster_metadata = admin_client.cluster_metadata()
        self.metrics['kafka'] = {
            'brokers': 3,
            'topics': 10,
            'partitions': 30
        }
    
    def report(self):
        print(json.dumps(self.metrics, indent=2))

monitor = PipelineMonitor()
# Monitor at regular intervals
```

---

## Optimization Checklist

- [ ] Parallelism: Tuned for CPU cores
- [ ] Memory: Monitored and optimized
- [ ] Batching: Used where applicable
- [ ] Caching: Implemented at multiple layers
- [ ] Compression: Enabled for large data
- [ ] Indexing: Optimized for query patterns
- [ ] Partitioning: Aligned with data distribution
- [ ] Monitoring: Alerts configured
- [ ] Scaling: Horizontal scaling tested
- [ ] Backpressure: Handled properly

---

## Exercises for Day 4

1. Profile your Redis usage and optimize memory
2. Tune Flink parallelism and checkpointing
3. Optimize Spark DataFrame operations
4. Create an efficient Elasticsearch query
5. Benchmark Kafka producer/consumer settings

---

## Next: Day 5 - Final Integrated Demo Project
