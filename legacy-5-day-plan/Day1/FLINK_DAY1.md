# Day 1: Apache Flink - Introduction & Setup

## Time Allocation: 30-40 minutes

### What is Apache Flink?

**Apache Flink** is a unified stream and batch processing framework that provides high-performance, fault-tolerant data processing with low latency and exactly-once semantics.

#### Key Characteristics:
- **Stream-First**: Processes continuous data streams with microsecond latency
- **Unified**: Handles both streaming and batch workloads (batch = finite stream)
- **Stateful**: Maintains and manages complex state during processing
- **Fault-Tolerant**: Checkpointing and savepoints for recovery
- **Distributed**: Scales horizontally across clusters
- **Event Time**: Supports processing-time, event-time, and ingestion-time

#### Architecture:
```
┌─────────────────────────────────────────────────────┐
│              JobManager (Control Plane)             │
│  - Job Scheduling  - Resource Management           │
│  - Checkpointing   - HA Support                     │
└─────────────────────────────────────────────────────┘
              ↓              ↓              ↓
┌──────────────────────────────────────────────────────┐
│  TaskManager₁      TaskManager₂      TaskManagerₙ   │
│  (Workers)         (Workers)         (Workers)      │
│  - Task Slots      - Task Slots      - Task Slots   │
│  - Memory/CPU      - Memory/CPU      - Memory/CPU   │
└──────────────────────────────────────────────────────┘
        ↓                    ↓                    ↓
    [Source]            [Source]            [Source]
      ↓                    ↓                    ↓
  [Process]            [Process]            [Process]
      ↓                    ↓                    ↓
   [Sink]               [Sink]               [Sink]
```

#### Why Flink?
1. **Low Latency**: Sub-second processing for real-time analytics
2. **Exactly-Once Semantics**: No duplicate processing, guaranteed consistency
3. **State Management**: Complex computations on stateful data
4. **Flexible Windowing**: Tumbling, sliding, session windows
5. **Rich Ecosystem**: Connectors, libraries, SQL support

---

## Installation & Setup

### Option 1: Docker (Recommended)
```bash
docker run -d --name flink-jobmanager -p 8081:8081 \
  -e FLINK_PROPERTIES="jobmanager.rpc.address: flink-jobmanager" \
  flink:latest jobmanager

docker run -d --name flink-taskmanager \
  -e FLINK_PROPERTIES="jobmanager.rpc.address: flink-jobmanager" \
  flink:latest taskmanager
```

### Option 2: Local Standalone Cluster
```bash
# Download and extract
wget https://dlcdn.apache.org/flink/flink-1.17.1/flink-1.17.1-bin-scala_2.12.tgz
tar xzf flink-1.17.1-bin-scala_2.12.tgz
cd flink-1.17.1

# Start cluster
./bin/start-cluster.sh

# Access JobManager UI: http://localhost:8081
# Stop cluster
./bin/stop-cluster.sh
```

### Python Setup
```bash
pip install apache-flink
```

---

## Basic Concepts

### 1. Stream Processing Model
Flink processes data as a continuous stream of events flowing through the system.

```
Data Stream: Event₁ → Event₂ → Event₃ → Event₄ → ...
                ↓        ↓        ↓        ↓
             Process  Process  Process  Process
                ↓        ↓        ↓        ↓
            Result₁  Result₂  Result₃  Result₄
```

### 2. Parallelism
Flink distributes processing across multiple parallel tasks. Higher parallelism = higher throughput but more resources.

```
Parallelism = 3 (3 tasks processing simultaneously)

Task 1 processes: Events 1, 4, 7, 10...
Task 2 processes: Events 2, 5, 8, 11...
Task 3 processes: Events 3, 6, 9, 12...
```

### 3. Data Types
- **DataStream**: Streaming API for continuous data
- **DataSet**: Batch API for bounded data (deprecated in newer versions)

---

## Your First Flink Job: Word Count (Batch)

### Python Implementation:
```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import FilterFunction, FlatMapFunction
from pyflink.common.typeinfo import Types
import re

class Tokenizer(FlatMapFunction):
    """Split line into words"""
    def flat_map(self, value):
        words = re.sub(r'[^a-zA-Z0-9\s]', '', value).lower().split()
        for word in words:
            if word:
                yield (word, 1)

# Create execution environment
env = StreamExecutionEnvironment.get_execution_environment()

# Read from file
data_stream = env.read_text_file('/path/to/input.txt')

# Process: Tokenize, count, and aggregate
result = data_stream \
    .flat_map(Tokenizer(), output_type=Types.TUPLE([Types.STRING, Types.INT])) \
    .key_by(lambda x: x[0]) \
    .sum(1) \
    .map(lambda x: f"{x[0]}: {x[1]}")

# Print results
result.print()

# Execute job
env.execute("Word Count")
```

### Input File (input.txt):
```
Hello World
Hello Flink
Flink Stream Processing
World of Flink
```

### Expected Output:
```
hello: 2
world: 2
flink: 3
stream: 1
processing: 1
of: 1
```

---

## Key Concepts: Time & Windows

### Event Time vs Processing Time

**Event Time**: Timestamp when event occurred (in the data)
```
Event: "Click" occurred at 14:30:05
         ↓
System processes it at 14:30:10 (5 seconds later)
       Processing Time
```

**Processing Time**: When Flink processes the event

```python
# Set Event Time
env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
```

### Windows: Divide Stream into Buckets

**Tumbling Window**: Fixed, non-overlapping periods
```
Time:  0-5s | 5-10s | 10-15s | 15-20s
Data:  ╔════╗ ╔════╗ ╔════╗ ╔════╗
       ║ EV ║ ║ EV ║ ║ EV ║ ║ EV ║
       ╚════╝ ╚════╝ ╚════╝ ╚════╝
```

**Sliding Window**: Overlapping periods
```
Time:  0-10s | 5-15s | 10-20s | 15-25s
Data:  ╔═══════╗
       ║ EV EV ║
       ╚═══════╝
           ╔═══════╗
           ║ EV EV ║
           ╚═══════╝
```

---

## Practical Example: Real-Time Sensor Data

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction
from pyflink.common.typeinfo import Types
import json
from datetime import datetime

class SensorReading:
    def __init__(self, sensor_id, temperature, timestamp):
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.timestamp = timestamp
    
    def __repr__(self):
        return f"Sensor({self.sensor_id}, {self.temperature}°C, {self.timestamp})"

class TemperatureFilter(MapFunction):
    """Filter and parse sensor data"""
    def map(self, value):
        data = json.loads(value)
        return SensorReading(
            data['sensor_id'],
            float(data['temperature']),
            datetime.fromisoformat(data['timestamp'])
        )

# Create environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)

# Simulate sensor data
sensor_data = [
    '{"sensor_id": "S1", "temperature": 22.5, "timestamp": "2024-01-01T10:00:00"}',
    '{"sensor_id": "S2", "temperature": 25.3, "timestamp": "2024-01-01T10:00:01"}',
    '{"sensor_id": "S1", "temperature": 23.1, "timestamp": "2024-01-01T10:00:02"}',
    '{"sensor_id": "S2", "temperature": 24.8, "timestamp": "2024-01-01T10:00:03"}',
]

# Process
stream = env.from_collection(sensor_data)
result = stream \
    .map(TemperatureFilter()) \
    .map(lambda x: f"Processed: {x}")

result.print()

# Execute
env.execute("Sensor Processing")
```

---

## Core Components

| Component | Role |
|-----------|------|
| **Source** | Entry point (Kafka, files, sockets) |
| **Operator** | Transforms data (map, filter, aggregate) |
| **State** | Maintains data across events (counts, sums) |
| **Sink** | Output destination (database, Kafka, files) |
| **JobGraph** | DAG of operators |

---

## Important Concepts

1. **Parallelism**: Degree of parallelism for each operator
2. **Slot**: CPU/Memory unit on TaskManager
3. **Subtask**: Instance of operator running in a slot
4. **Keyspace**: Logical partition based on key
5. **Checkpoint**: Periodic snapshot of state for recovery

---

## Exercises

1. Create a word count job from a text file
2. Implement a sensor filter that only keeps readings > 25°C
3. Count events per key over a tumbling window
4. Use parallelism to process data across multiple slots

---

## Next Steps (Day 2)
- DataStream API transformations (flatMap, keyBy, window)
- Time semantics and windowing
- State management and checkpointing
- Integration with Kafka
