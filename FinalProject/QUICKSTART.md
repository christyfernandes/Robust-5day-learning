# Quick Start Guide for Day 5 Final Project

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+
- Kafka Python client: `pip install kafka-python`
- Redis Python client: `pip install redis`
- Elasticsearch Python client: `pip install elasticsearch`

## Project Structure

```
FinalProject/
├── docker-compose.yml      # Infrastructure setup
├── producer.py             # Event generator
├── cache_layer.py          # Redis caching logic
├── es_indexer.py           # Elasticsearch indexing
├── main_pipeline.py        # Main orchestrator
└── README.md              # This file
```

## Quick Start (5 minutes)

### Step 1: Start Infrastructure

```bash
cd FinalProject
docker-compose up -d

# Verify all services are running
docker-compose ps

# Wait for health checks to pass (2-3 minutes)
```

### Step 2: Install Python Dependencies

```bash
pip install kafka-python redis elasticsearch
```

### Step 3: Run the Pipeline

```bash
# Run for 60 seconds (default)
python main_pipeline.py

# Or run for custom duration
python main_pipeline.py --duration 120
```

## What Happens

1. **Event Producer** generates 50 events/second for 60 seconds
   - Real user activity (page views, searches, purchases, etc.)
   - Events sent to Kafka topic 'user_events'

2. **Kafka** distributes events across 3 partitions
   - Ensures ordered processing per user

3. **Consumer** processes events in real-time
   - Caches user sessions in Redis
   - Tracks metrics (purchases, spend, engagement)
   - Maintains leaderboards

4. **Elasticsearch** indexes all events
   - Enables search and analytics
   - Runs aggregations for insights

5. **Reports** final statistics and analytics

## Expected Output

```
============================================================
E-COMMERCE REAL-TIME ANALYTICS PLATFORM
============================================================

[Pipeline] Processed 1000 events
[Pipeline] Processed 2000 events
[Pipeline] Processed 3000 events

============================================================
PIPELINE RESULTS & ANALYTICS
============================================================

[REDIS] Top 5 Spenders (Leaderboard):
  1. user_00042: $4995.50
  2. user_00018: $4850.75
  3. user_00076: $4720.30
  4. user_00051: $4680.90
  5. user_00003: $4520.45

[ELASTICSEARCH] Total Events Indexed: 3000

[ELASTICSEARCH] Event Distribution:
  page_view: 1050 (35.0%)
  search: 450 (15.0%)
  add_to_cart: 450 (15.0%)
  purchase: 300 (10.0%)
  login: 450 (15.0%)
  logout: 300 (10.0%)

[ELASTICSEARCH] Revenue by Region:
  us-east: $15750.00 (avg: $157.50)
  eu-west: $14200.00 (avg: $142.00)
  us-west: $13500.00 (avg: $135.00)
  ap-south: $9800.00 (avg: $98.00)
  au-east: $8750.00 (avg: $87.50)

[ELASTICSEARCH] Revenue by User Tier:
  gold: $28500.00 (250 transactions)
  silver: $18600.00 (150 transactions)
  platinum: $12000.00 (75 transactions)
  bronze: $8700.00 (50 transactions)

[ELASTICSEARCH] Top 10 Products:
  1. laptop: 450 views
  2. monitor: 380 views
  3. keyboard: 320 views
  ...

[SUMMARY]
  Total Events Processed: 3000
  Total Events Indexed: 3000
  Timestamp: 2024-01-01T12:00:00.000000
```

## Components Explained

### producer.py
- Generates realistic e-commerce events
- 100 active users with different tiers and regions
- Event types: page_view, search, add_to_cart, purchase, login, logout
- Sends to Kafka with user_id as key (preserves ordering per user)

### cache_layer.py
- Redis-based session management
- Tracks user activity in real-time
- Maintains metrics (purchases, spend, engagement)
- Implements leaderboards using sorted sets
- TTL-based auto-expiration

### es_indexer.py
- Creates optimized Elasticsearch index
- Bulk indexing for performance
- Provides search capabilities
- Computes analytics aggregations
- Generates insights (top products, revenue by region, etc.)

### main_pipeline.py
- Orchestrates the entire system
- Sets up Kafka topics
- Runs producer in background thread
- Consumes and processes events in real-time
- Generates final reports

## Monitoring

### Check Docker Logs

```bash
# Kafka
docker-compose logs kafka

# Redis
docker-compose logs redis

# Elasticsearch
docker-compose logs elasticsearch
```

### Access Web UIs

- Flink JobManager: http://localhost:8081
- Elasticsearch: http://localhost:9200

### Manual Testing

```bash
# Check Kafka topics
docker exec kafka kafka-topics \
  --list --bootstrap-server localhost:9092

# Check Redis
docker exec redis redis-cli ping
docker exec redis redis-cli INFO

# Check Elasticsearch
curl http://localhost:9200/_cat/indices
```

## Troubleshooting

### Issue: Port already in use
```bash
# Change ports in docker-compose.yml
# Or kill process using the port
lsof -i :9092  # Find process
kill -9 <PID>
```

### Issue: Out of memory
```bash
# Reduce event rate
python main_pipeline.py --duration 30

# Or reduce batch sizes in es_indexer.py
```

### Issue: Connection refused
```bash
# Ensure all services are healthy
docker-compose ps

# Wait for health checks (check STATUS column)
# If any are "unhealthy", check logs
docker-compose logs <service_name>
```

### Issue: No events indexed
```bash
# Check if events are being produced
docker exec kafka kafka-console-consumer \
  --topic user_events \
  --bootstrap-server localhost:9092 \
  --from-beginning \
  --max-messages 5

# Check Elasticsearch
curl http://localhost:9200/user_events/_count
```

## Performance Tuning

### Increase Event Rate
```python
# In main_pipeline.py or directly:
gen.stream_events(duration_seconds=120, events_per_second=100)
```

### Parallel Consumers
```python
# Run multiple consumer instances (use different group_ids)
```

### Index Optimization
```python
# Modify batch size in es_indexer.py
bulk(self.es, actions, chunk_size=5000)  # Larger batches
```

## Extensions

1. **Add Real-Time Dashboards**: Use Grafana + Elasticsearch
2. **Implement Alerts**: Trigger on anomalies
3. **Add ML Models**: Score customers, predict churn
4. **Implement Spark Batch**: Daily aggregations
5. **Add Monitoring**: Prometheus + custom metrics

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (data)
docker-compose down -v
```

## Next Steps

1. Read the documentation for each component in Day 5/DAY5_FINAL_PROJECT.md
2. Modify the code to experiment with different architectures
3. Add error handling and logging
4. Implement monitoring and alerting
5. Deploy to a distributed cluster

## Learning Outcomes

By completing this project, you should understand:
- ✅ How to build end-to-end data pipelines
- ✅ When and how to use each technology
- ✅ Real-time vs batch processing trade-offs
- ✅ Event-driven architecture patterns
- ✅ Scaling considerations
- ✅ Production deployment concerns

Good luck! 🚀
