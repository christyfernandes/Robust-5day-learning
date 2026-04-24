# Day 1: Apache Kafka - Introduction & Setup

## Time Allocation: 30-40 minutes

### What is Apache Kafka?

**Apache Kafka** is a distributed event streaming platform that enables you to publish, subscribe to, store, and process streams of records in real-time. It's the central nervous system for event-driven architectures.

#### Key Characteristics:
- **Pub/Sub Model**: Producers publish messages, consumers subscribe to topics
- **Distributed**: Scales horizontally across brokers
- **Fault-Tolerant**: Replication ensures no message loss
- **Durable**: Persistent storage on disk
- **High-Throughput**: Millions of messages per second
- **Low-Latency**: Real-time delivery
- **Stream Processing**: Process events as they happen

#### Architecture:
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Producer 1  │    │  Producer 2  │    │  Producer n  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼─────┐        ┌───▼─────┐       ┌───▼─────┐
    │ Broker 1│        │ Broker 2│       │ Broker 3│
    │ Topic A │        │ Topic A │       │ Topic A │
    │ Part 0  │        │ Part 1  │       │ Part 2  │
    └─────────┘        └─────────┘       └─────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼──────┐       ┌───▼──────┐     ┌───▼──────┐
    │Consumer 1│       │Consumer 2│     │Consumer 3│
    │Group A   │       │Group A   │     │Group B   │
    └──────────┘       └──────────┘     └──────────┘
```

#### Why Kafka?
1. **Scalability**: Handle millions of events per second
2. **Durability**: Data persisted on disk, survives failures
3. **Real-Time**: Sub-second latency for event processing
4. **Flexibility**: Works for different use cases (logs, metrics, events)
5. **Integration**: Works with Spark, Flink, Storm, etc.

---

## Core Concepts

### 1. Topic
Named channel for publishing messages. Think of it as a subject or feed.

```
Topic: "orders"
├── Message 1: {order_id: 1, customer: "Alice", amount: 99.99}
├── Message 2: {order_id: 2, customer: "Bob", amount: 49.99}
├── Message 3: {order_id: 3, customer: "Carol", amount: 199.99}
└── Message 4: {order_id: 4, customer: "David", amount: 79.99}
```

### 2. Partition
Ordered sequence of messages within a topic. Enables parallelism.

```
Topic: "orders" (3 partitions)
├── Partition 0: [Msg 1, Msg 4, Msg 7]  → Consumer 1
├── Partition 1: [Msg 2, Msg 5, Msg 8]  → Consumer 2
└── Partition 2: [Msg 3, Msg 6, Msg 9]  → Consumer 3
```

### 3. Broker
Kafka server instance. Cluster contains multiple brokers.

```
Cluster: 3 Brokers
├── Broker 1 (Leader for Partition 0)
├── Broker 2 (Leader for Partition 1)
└── Broker 3 (Leader for Partition 2)

Each partition has 1 leader + 2 replicas for fault tolerance
```

### 4. Producer
Application that sends messages to topics.

```
Producer → Serialize → Partition Selection → Broker
Message   Message     (based on key)        Storage
```

### 5. Consumer
Application that reads messages from topics.

```
Consumer ← Deserialize ← Broker
         Message      (fetch with offset)
```

### 6. Consumer Group
Set of consumers sharing a topic subscription.

```
Topic "orders" (4 partitions)
├── Consumer Group A
│   ├── Consumer 1 → Partition 0, 1
│   └── Consumer 2 → Partition 2, 3
└── Consumer Group B
    ├── Consumer 1 → All 4 partitions
    ├── Consumer 2 → (idle)
    └── Consumer 3 → (idle)
```

### 7. Offset
Position of message in partition. Used for tracking consumption progress.

```
Partition: [Msg@0, Msg@1, Msg@2, Msg@3, Msg@4]
           └──────────────────┘
           Consumer offset: 2 (next to consume is @3)
```

---

## Installation & Setup

### Option 1: Docker (Recommended)
```bash
# Docker Compose
docker run -d --name zookeeper -e ZOO_CFG_EXTRA="server.1=zookeeper:2888:3888;2181" zookeeper

docker run -d --name kafka \
  -e KAFKA_BROKER_ID=1 \
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092 \
  -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT \
  -e KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT \
  -p 9092:9092 \
  confluentinc/cp-kafka:7.0.0
```

### Option 2: Local Installation (macOS)
```bash
brew install kafka

# Start Zookeeper
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties

# In another terminal, start Kafka
kafka-server-start /usr/local/etc/kafka/server.properties
```

### Option 3: From Tarball
```bash
wget https://archive.apache.org/dist/kafka/3.0.0/kafka_2.13-3.0.0.tgz
tar xzf kafka_2.13-3.0.0.tgz
cd kafka_2.13-3.0.0

# Start Zookeeper
./bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka (in another terminal)
./bin/kafka-server-start.sh config/server.properties
```

### Python Client
```bash
pip install kafka-python
```

---

## Basic Operations

### 1. Creating a Topic

**Command Line:**
```bash
kafka-topics --create --topic orders --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 2
```

**Python:**
```python
from kafka.admin import KafkaAdminClient, NewTopic

# Create admin client
admin_client = KafkaAdminClient(bootstrap_servers=['localhost:9092'])

# Define topic
new_topic = NewTopic(name='orders', num_partitions=3, replication_factor=1)

# Create topic
admin_client.create_topics(new_topics=[new_topic], validate_only=False)
admin_client.close()

print("Topic 'orders' created!")
```

---

### 2. Publishing Messages

**Command Line:**
```bash
echo "order_id:1|customer:Alice|amount:99.99" | \
  kafka-console-producer --topic orders --bootstrap-server localhost:9092
```

**Python:**
```python
from kafka import KafkaProducer
import json

# Create producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send messages
orders = [
    {"order_id": 1, "customer": "Alice", "amount": 99.99},
    {"order_id": 2, "customer": "Bob", "amount": 49.99},
    {"order_id": 3, "customer": "Carol", "amount": 199.99},
]

for order in orders:
    # Partition selection: if key is provided, same key → same partition
    # if no key, round-robin across partitions
    future = producer.send('orders', value=order, key=str(order['customer']).encode('utf-8'))
    record_metadata = future.get(timeout=10)
    print(f"Sent to partition {record_metadata.partition}, offset {record_metadata.offset}")

producer.flush()
producer.close()
```

---

### 3. Consuming Messages

**Command Line:**
```bash
# Consume from beginning
kafka-console-consumer --topic orders --bootstrap-server localhost:9092 \
  --from-beginning

# Consume from latest only
kafka-console-consumer --topic orders --bootstrap-server localhost:9092
```

**Python:**
```python
from kafka import KafkaConsumer
import json

# Create consumer
consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['localhost:9092'],
    group_id='order-processing-group',
    auto_offset_reset='earliest',  # Start from beginning if no offset
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    max_poll_records=100,  # Fetch up to 100 records per poll
    session_timeout_ms=30000  # 30 second session
)

# Consume messages
try:
    for message in consumer:
        print(f"Partition: {message.partition}")
        print(f"Offset: {message.offset}")
        print(f"Key: {message.key}")
        print(f"Value: {message.value}")
        print("---")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

---

### 4. Consumer Groups & Offset Management

```python
from kafka import KafkaConsumer
import json

# Multiple consumers in same group share partitions
consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-group',  # Consumer group ID
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    enable_auto_commit=True,  # Auto-commit offset after processing
    auto_commit_interval_ms=5000  # Commit every 5 seconds
)

# Manual offset management
for message in consumer:
    try:
        order = message.value
        print(f"Processing order: {order}")
        
        # Do processing...
        
        # Manually commit offset
        consumer.commit()
    except Exception as e:
        print(f"Error processing: {e}")
        # Don't commit on error, will retry

consumer.close()
```

---

## Practical Example: Order Processing System

```python
from kafka import KafkaProducer, KafkaConsumer
import json
import time
from datetime import datetime

class OrderProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def send_order(self, order_data):
        """Send order to Kafka"""
        future = self.producer.send('orders', value=order_data)
        record_metadata = future.get(timeout=10)
        return {
            'topic': record_metadata.topic,
            'partition': record_metadata.partition,
            'offset': record_metadata.offset
        }
    
    def close(self):
        self.producer.close()

class OrderProcessor:
    def __init__(self, group_id):
        self.consumer = KafkaConsumer(
            'orders',
            bootstrap_servers=['localhost:9092'],
            group_id=group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=True
        )
    
    def process_orders(self):
        """Process orders from Kafka"""
        print(f"Processor ({self.consumer.config['group_id']}) started")
        
        for message in self.consumer:
            order = message.value
            print(f"\n[{datetime.now()}] Processing Order:")
            print(f"  ID: {order['order_id']}")
            print(f"  Customer: {order['customer']}")
            print(f"  Amount: ${order['amount']}")
            print(f"  Offset: {message.offset}")
            
            # Simulate processing
            time.sleep(0.5)
    
    def close(self):
        self.consumer.close()

# Usage Example
if __name__ == "__main__":
    # Create producer
    producer = OrderProducer()
    
    # Send sample orders
    orders = [
        {"order_id": 1, "customer": "Alice", "amount": 99.99, "timestamp": datetime.now().isoformat()},
        {"order_id": 2, "customer": "Bob", "amount": 49.99, "timestamp": datetime.now().isoformat()},
        {"order_id": 3, "customer": "Carol", "amount": 199.99, "timestamp": datetime.now().isoformat()},
    ]
    
    for order in orders:
        result = producer.send_order(order)
        print(f"Order {order['order_id']} sent - Partition: {result['partition']}, Offset: {result['offset']}")
    
    producer.close()
    
    # Consume orders
    processor = OrderProcessor(group_id='order-processing-v1')
    try:
        processor.process_orders()
    except KeyboardInterrupt:
        processor.close()
```

---

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **Topic** | Named message feed/channel |
| **Partition** | Ordered sequence within topic |
| **Broker** | Kafka server instance |
| **Producer** | Sends messages to topic |
| **Consumer** | Reads messages from topic |
| **Consumer Group** | Multiple consumers sharing subscription |
| **Offset** | Message position in partition |
| **Replica** | Copy of partition for fault tolerance |

---

## Important Commands

```bash
# List topics
kafka-topics --list --bootstrap-server localhost:9092

# Describe topic
kafka-topics --describe --topic orders --bootstrap-server localhost:9092

# Delete topic
kafka-topics --delete --topic orders --bootstrap-server localhost:9092

# Check consumer group
kafka-consumer-groups --list --bootstrap-server localhost:9092

# Describe consumer group
kafka-consumer-groups --describe --group order-processing-group --bootstrap-server localhost:9092

# Reset offset to beginning
kafka-consumer-groups --reset-offsets --topic orders --group order-processing-group \
  --to-earliest --execute --bootstrap-server localhost:9092
```

---

## Exercises

1. Create a Kafka topic with multiple partitions
2. Produce messages from Python
3. Consume messages with a consumer group
4. Observe how partitions distribute messages
5. Monitor consumer lag and offsets

---

## Next Steps (Day 2)
- Partitioning strategies and key selection
- Consumer group rebalancing
- Delivery semantics (exactly-once, at-least-once)
- Kafka Streams for stream processing
- Schema Registry and data serialization
