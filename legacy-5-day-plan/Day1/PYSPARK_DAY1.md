# Day 1: PySpark - Introduction & Setup

## Time Allocation: 30-40 minutes

### What is PySpark?

**PySpark** is the Python API for Apache Spark, a unified computing engine for large-scale data processing. It's designed for both batch and streaming workloads with fault tolerance and in-memory processing.

#### Key Characteristics:
- **In-Memory Computing**: 10-100x faster than Hadoop MapReduce
- **Lazy Evaluation**: Builds execution plan before running
- **RDD-Based**: Resilient Distributed Datasets - immutable, fault-tolerant
- **DataFrames**: SQL-like interface for structured data
- **Distributed**: Scales across clusters
- **Multi-Language**: Python, Scala, Java, SQL

#### Architecture:
```
┌────────────────────────────────────────────┐
│         Spark Driver (Main Program)        │
│  - DAG Scheduler  - Task Scheduler         │
└────────────────────────────────────────────┘
              ↓              ↓
┌───────────────────────────────────────────┐
│    Cluster Manager (YARN/K8s/Mesos)       │
│  - Resource Allocation  - Monitoring      │
└───────────────────────────────────────────┘
    ↓              ↓              ↓
┌────────┐  ┌────────┐  ┌────────┐
│Executor│  │Executor│  │Executor│ (Worker Nodes)
│ Slot 1 │  │ Slot 2 │  │ Slot 3 │
│ Slot 2 │  │ Slot 3 │  │ Slot 4 │
└────────┘  └────────┘  └────────┘
```

#### Why PySpark?
1. **Speed**: In-memory processing, 10-100x faster than Hadoop
2. **Simplicity**: Expressive APIs in Python
3. **Flexibility**: Batch + streaming + SQL + ML
4. **Fault-Tolerance**: Automatic recovery from node failures
5. **Scalability**: From laptop to 1000s of nodes

---

## Installation & Setup

### Option 1: Docker (Recommended)
```bash
docker run -it python:3.10 bash
pip install pyspark
```

### Option 2: Local Installation (macOS)
```bash
brew install apache-spark
pip install pyspark

# Verify installation
python -c "import pyspark; print(pyspark.__version__)"
```

### Option 3: PySpark with Jupyter
```bash
pip install pyspark jupyter
jupyter notebook
```

### Option 4: Standalone Cluster
```bash
wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar xzf spark-3.5.0-bin-hadoop3.tgz
cd spark-3.5.0-bin-hadoop3

# Start cluster
./sbin/start-master.sh
./sbin/start-slave.sh spark://localhost:7077

# Access UI: http://localhost:8080
```

---

## Spark Concepts

### 1. RDD (Resilient Distributed Dataset)
Immutable, distributed collections of objects that can be processed in parallel.

```
Original Data: [1, 2, 3, 4, 5]
     ↓
Partition 1: [1, 2]
Partition 2: [3, 4]
Partition 3: [5]
     ↓
Processed in parallel on 3 nodes
```

### 2. DataFrame
Similar to SQL tables or pandas DataFrames but distributed. More efficient than RDDs.

```
┌─────────┬───────┬─────────┐
│ ID      │ Name  │ Age     │
├─────────┼───────┼─────────┤
│ 1       │ Alice │ 25      │
│ 2       │ Bob   │ 30      │
│ 3       │ Carol │ 28      │
└─────────┴───────┴─────────┘
```

### 3. DAG (Directed Acyclic Graph)
Spark creates a DAG of transformations and executes it optimally.

```
Read Data
    ↓
Map Function
    ↓
Filter Function
    ↓
Aggregation
    ↓
Write Results
```

### 4. Transformations vs Actions
- **Transformations**: Lazy operations that return RDD/DataFrame (map, filter, groupBy)
- **Actions**: Trigger execution and return results (collect, count, show)

---

## Getting Started: Your First PySpark Job

### Basic Setup & Operations

```python
from pyspark.sql import SparkSession

# Create Spark Session
spark = SparkSession.builder \
    .appName("FirstPySparkApp") \
    .master("local[2]") \
    .getOrCreate()

# Set log level
spark.sparkContext.setLogLevel("WARN")

print(f"Spark Version: {spark.version}")
print(f"App Name: {spark.sparkContext.appName}")

# Example 1: Create RDD from list
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])

# Transformation: map (apply function to each element)
rdd_doubled = rdd.map(lambda x: x * 2)

# Action: collect (bring all data to driver)
result = rdd_doubled.collect()
print(f"Doubled: {result}")  # Output: [2, 4, 6, 8, 10]

# Example 2: Filter transformation
rdd_even = rdd.filter(lambda x: x % 2 == 0)
print(f"Even numbers: {rdd_even.collect()}")  # Output: [2, 4]

# Example 3: Reduce action
total = rdd.reduce(lambda x, y: x + y)
print(f"Sum: {total}")  # Output: 15

# Example 4: Count
count = rdd.count()
print(f"Count: {count}")  # Output: 5
```

---

## DataFrame Operations

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# Create Spark Session
spark = SparkSession.builder.appName("DataFrameDemo").master("local[2]").getOrCreate()

# Define Schema
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("salary", DoubleType(), True)
])

# Create DataFrame from data
data = [
    (1, "Alice", 25, 50000.0),
    (2, "Bob", 30, 60000.0),
    (3, "Carol", 28, 55000.0),
    (4, "David", 35, 70000.0),
    (5, "Eve", 26, 52000.0)
]

df = spark.createDataFrame(data, schema)

# Display
df.show()
"""
+---+-----+---+-------+
| id| name|age|salary |
+---+-----+---+-------+
|  1|Alice| 25|50000.0|
|  2|  Bob| 30|60000.0|
|  3|Carol| 28|55000.0|
|  4|David| 35|70000.0|
|  5|  Eve| 26|52000.0|
+---+-----+---+-------+
"""

# Select specific columns
df.select("name", "age").show()

# Filter: Age > 27
df.filter(df.age > 27).show()

# GroupBy: Average salary by age group
df.groupBy("age").agg({"salary": "avg"}).show()

# Sort: By salary descending
df.orderBy("salary", ascending=False).show()

# Add new column
df_with_bonus = df.withColumn("bonus", df.salary * 0.1)
df_with_bonus.select("name", "salary", "bonus").show()

# Filter and aggregate
high_earners = df.filter(df.salary > 55000).count()
print(f"High earners (>55K): {high_earners}")

# Group and aggregate
avg_salary_by_age = df.groupBy("age").agg({"salary": "avg"})
avg_salary_by_age.show()
```

---

## Reading from CSV/JSON/Parquet

```python
# Read CSV
df_csv = spark.read.csv("data.csv", header=True, inferSchema=True)
df_csv.show()

# Read JSON
df_json = spark.read.json("data.json")
df_json.show()

# Read Parquet
df_parquet = spark.read.parquet("data.parquet")
df_parquet.show()

# Write to different formats
df.write.csv("output.csv", header=True)
df.write.json("output.json")
df.write.parquet("output.parquet")
```

---

## SQL Queries on DataFrames

```python
# Register DataFrame as temporary view
df.createOrReplaceTempView("employees")

# Run SQL query
result = spark.sql("""
    SELECT name, age, salary
    FROM employees
    WHERE age > 27
    ORDER BY salary DESC
""")

result.show()
```

---

## Practical Example: Word Count from Text File

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, explode, split, count

spark = SparkSession.builder.appName("WordCount").master("local[2]").getOrCreate()

# Read text file
text_df = spark.read.text("input.txt")

# Explode lines to words
words = text_df \
    .select(explode(split(lower(col("value")), " ")).alias("word")) \
    .filter(col("word") != "")

# Count words
word_count = words.groupBy("word").count().orderBy(col("count").desc())

word_count.show(20)

# Save results
word_count.write.csv("word_count_output", header=True)
```

---

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **RDD** | Low-level, untyped, distributed collection |
| **DataFrame** | Higher-level, typed, SQL-like interface |
| **Transformation** | Lazy operation returning new RDD/DataFrame |
| **Action** | Triggers computation, returns result |
| **Partition** | Subset of data on a single node |
| **Driver** | Program that coordinates Spark |
| **Executor** | Process that runs tasks on worker nodes |
| **DAG** | Directed acyclic graph of operations |

---

## Important Operations

```python
# RDD Operations
rdd.map(func)              # Apply function to each element
rdd.filter(func)           # Keep elements where func returns True
rdd.flatMap(func)          # Map then flatten
rdd.groupByKey()           # Group by key (for K,V pairs)
rdd.reduceByKey(func)      # Aggregate values by key
rdd.union(other_rdd)       # Combine two RDDs
rdd.distinct()             # Remove duplicates

# DataFrame Operations
df.select(cols)            # Choose columns
df.filter(condition)       # Filter rows
df.groupBy(col).agg(func)  # Group and aggregate
df.join(other_df, on)      # Join two DataFrames
df.orderBy(col)            # Sort
df.limit(n)                # Take first n rows
df.distinct()              # Remove duplicate rows
```

---

## Exercises

1. Create a DataFrame from a list and perform basic operations
2. Read a CSV file and explore its schema
3. Group data by a column and calculate averages
4. Write word count from text file using RDDs and DataFrames
5. Join two DataFrames together

---

## Next Steps (Day 2)
- Advanced DataFrame operations
- Window functions and complex aggregations
- Structured Streaming
- Integration with Kafka
- Performance tuning
