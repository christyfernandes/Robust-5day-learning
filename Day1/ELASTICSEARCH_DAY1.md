# Day 1: Elasticsearch - Introduction & Setup

## Time Allocation: 30-40 minutes

### What is Elasticsearch?

**Elasticsearch** is a distributed, open-source search and analytics engine built on top of Apache Lucene. It's designed for fast full-text search, log analytics, and real-time data analysis.

#### Key Characteristics:
- **Distributed**: Horizontal scalability across nodes
- **Real-Time**: Sub-second search latency
- **Full-Text Search**: Advanced text analysis and search capabilities
- **Analytics**: Aggregations for numerical data
- **RESTful API**: HTTP-based interface
- **Schema-less**: Flexible mapping, auto-detection
- **Inverted Index**: Super-fast text search

#### Architecture:
```
┌────────────────────────────────────────┐
│         Elasticsearch Cluster           │
├────────────────────────────────────────┤
│  Node 1         Node 2         Node 3   │
│ ┌──────────┐   ┌──────────┐   ┌──────────┐
│ │ Shard 1  │   │ Shard 2  │   │ Shard 3  │
│ │ Replica 2│   │ Replica 3│   │ Replica 1│
│ └──────────┘   └──────────┘   └──────────┘
└────────────────────────────────────────┘
         ↑          ↑          ↑
      Inverted Indexes
      (Full-Text Search)
```

#### Why Elasticsearch?
1. **Speed**: Sub-millisecond search on millions of documents
2. **Flexibility**: Works with structured and unstructured data
3. **Scalability**: Handles petabytes of data
4. **Reliability**: Automatic replication and failover
5. **Analytics**: Powerful aggregation capabilities

---

## Core Concepts

### 1. Index
A collection of documents with similar characteristics. Like a table in databases.

```
Index: "products"
├── Document 1: {id: 1, name: "Laptop", price: 999}
├── Document 2: {id: 2, name: "Mouse", price: 25}
└── Document 3: {id: 3, name: "Keyboard", price: 75}
```

### 2. Document
A JSON object containing data. The basic unit of information.

```json
{
  "id": 1,
  "name": "Laptop",
  "price": 999,
  "category": "Electronics",
  "tags": ["computer", "portable"],
  "rating": 4.5
}
```

### 3. Shard
Horizontal partition of an index. Enables parallel processing and scalability.

```
Index (100M documents)
├── Shard 1 (25M docs) → Node 1
├── Shard 2 (25M docs) → Node 2
├── Shard 3 (25M docs) → Node 3
└── Shard 4 (25M docs) → Node 4
```

### 4. Replica
Copy of a shard for high availability and failover.

```
Shard 1 → Node 1
  ↓
Replica of Shard 1 → Node 2
```

### 5. Mapping
Schema definition. Specifies field types and how to analyze text.

```json
{
  "mappings": {
    "properties": {
      "name": {"type": "text"},
      "price": {"type": "float"},
      "category": {"type": "keyword"}
    }
  }
}
```

---

## Installation & Setup

### Option 1: Docker (Recommended)
```bash
docker run -d --name elasticsearch \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -p 9200:9200 \
  docker.elastic.co/elasticsearch/elasticsearch:8.0.0

# Verify
curl http://localhost:9200/
```

### Option 2: Homebrew (macOS)
```bash
brew tap elastic/tap
brew install elastic-stack

elasticsearch
# In another terminal: curl http://localhost:9200/
```

### Option 3: From Tar Archive
```bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.0.0-darwin-x86_64.tar.gz
tar xzf elasticsearch-8.0.0-darwin-x86_64.tar.gz
cd elasticsearch-8.0.0
./bin/elasticsearch
```

### Python Client Installation
```bash
pip install elasticsearch
```

---

## Basic Operations

### 1. Creating an Index

**REST API:**
```bash
curl -X PUT http://localhost:9200/products
```

**Python:**
```python
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Create index with mapping
mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "text", "analyzer": "standard"},
            "category": {"type": "keyword"},
            "price": {"type": "float"},
            "rating": {"type": "float"},
            "tags": {"type": "keyword"},
            "description": {"type": "text"}
        }
    }
}

es.indices.create(index="products", body=mapping)
print("Index created!")
```

---

### 2. Indexing Documents

**REST API:**
```bash
curl -X POST http://localhost:9200/products/_doc \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Laptop",
    "category": "Electronics",
    "price": 999.99,
    "rating": 4.5,
    "tags": ["computer", "portable"],
    "description": "High-performance laptop with 16GB RAM"
  }'
```

**Python:**
```python
# Index single document
doc = {
    "id": 1,
    "name": "Laptop",
    "category": "Electronics",
    "price": 999.99,
    "rating": 4.5,
    "tags": ["computer", "portable"],
    "description": "High-performance laptop with 16GB RAM"
}

result = es.index(index="products", id=1, body=doc)
print(f"Document indexed: {result}")

# Bulk index multiple documents
documents = [
    {"index": {"_id": "2"}},
    {"id": 2, "name": "Mouse", "category": "Accessories", "price": 25.99, "rating": 4.0, "tags": ["peripheral"]},
    {"index": {"_id": "3"}},
    {"id": 3, "name": "Keyboard", "category": "Accessories", "price": 75.99, "rating": 4.2, "tags": ["peripheral", "mechanical"]},
    {"index": {"_id": "4"}},
    {"id": 4, "name": "Monitor", "category": "Electronics", "price": 299.99, "rating": 4.3, "tags": ["display"]},
]

from elasticsearch.helpers import bulk
bulk(es, documents, index="products")
print("Bulk indexed!")
```

---

### 3. Searching Documents

**REST API - Simple Match:**
```bash
curl -X GET http://localhost:9200/products/_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match": {
        "name": "laptop"
      }
    }
  }'
```

**Python - Various Query Types:**

```python
# Simple match query (full-text search)
result = es.search(index="products", body={
    "query": {
        "match": {
            "name": "laptop"
        }
    }
})
print(f"Found {result['hits']['total']['value']} documents")
for hit in result['hits']['hits']:
    print(hit['_source'])

# Match all query
result = es.search(index="products", body={
    "query": {"match_all": {}}
})

# Term query (exact match, not analyzed)
result = es.search(index="products", body={
    "query": {
        "term": {
            "category": "Electronics"
        }
    }
})

# Range query (price between 100 and 500)
result = es.search(index="products", body={
    "query": {
        "range": {
            "price": {
                "gte": 100,
                "lte": 500
            }
        }
    }
})

# Bool query (complex queries with AND/OR/NOT)
result = es.search(index="products", body={
    "query": {
        "bool": {
            "must": [
                {"match": {"category": "Electronics"}}
            ],
            "filter": [
                {"range": {"price": {"gte": 500}}}
            ],
            "must_not": [
                {"term": {"rating": 2}}
            ]
        }
    }
})

# Multi-field search
result = es.search(index="products", body={
    "query": {
        "multi_match": {
            "query": "portable computer",
            "fields": ["name", "description"]
        }
    }
})
```

---

### 4. Aggregations (Analytics)

```python
# Average price
result = es.search(index="products", body={
    "size": 0,
    "aggs": {
        "avg_price": {
            "avg": {"field": "price"}
        }
    }
})
print(f"Average price: ${result['aggregations']['avg_price']['value']}")

# Group by category and get average price
result = es.search(index="products", body={
    "size": 0,
    "aggs": {
        "by_category": {
            "terms": {"field": "category", "size": 10},
            "aggs": {
                "avg_price": {
                    "avg": {"field": "price"}
                }
            }
        }
    }
})

for bucket in result['aggregations']['by_category']['buckets']:
    print(f"{bucket['key']}: Count={bucket['doc_count']}, Avg Price=${bucket['avg_price']['value']}")

# Min, Max, Sum
result = es.search(index="products", body={
    "size": 0,
    "aggs": {
        "price_stats": {
            "stats": {"field": "price"}
        }
    }
})
stats = result['aggregations']['price_stats']
print(f"Min: ${stats['min']}, Max: ${stats['max']}, Avg: ${stats['avg']}, Sum: ${stats['sum']}")
```

---

### 5. Updating & Deleting Documents

```python
# Update document
es.update(index="products", id=1, body={
    "doc": {
        "price": 899.99,
        "rating": 4.7
    }
})

# Delete document
es.delete(index="products", id=1)

# Delete by query
es.delete_by_query(index="products", body={
    "query": {
        "range": {
            "price": {"lt": 50}
        }
    }
})
```

---

### 6. Getting Document Count

```python
# Count documents
count = es.count(index="products")
print(f"Total documents: {count['count']}")

# Count with query
count = es.count(index="products", body={
    "query": {
        "term": {"category": "Electronics"}
    }
})
print(f"Electronics: {count['count']}")
```

---

## Practical Example: E-Commerce Product Search

```python
from elasticsearch import Elasticsearch
from datetime import datetime

class ProductSearchEngine:
    def __init__(self, index_name="products"):
        self.es = Elasticsearch(["http://localhost:9200"])
        self.index = index_name
    
    def create_index(self):
        """Create index with mapping"""
        mapping = {
            "mappings": {
                "properties": {
                    "name": {"type": "text", "analyzer": "standard"},
                    "category": {"type": "keyword"},
                    "price": {"type": "float"},
                    "rating": {"type": "float"},
                    "tags": {"type": "keyword"},
                    "description": {"type": "text"},
                    "in_stock": {"type": "boolean"},
                    "created_at": {"type": "date"}
                }
            }
        }
        if self.es.indices.exists(index=self.index):
            self.es.indices.delete(index=self.index)
        self.es.indices.create(index=self.index, body=mapping)
    
    def index_product(self, product_id, product_data):
        """Index a single product"""
        self.es.index(index=self.index, id=product_id, body=product_data)
    
    def search_by_name(self, query):
        """Search products by name"""
        result = self.es.search(index=self.index, body={
            "query": {"match": {"name": query}}
        })
        return result['hits']['hits']
    
    def search_by_price_range(self, min_price, max_price):
        """Find products in price range"""
        result = self.es.search(index=self.index, body={
            "query": {
                "range": {"price": {"gte": min_price, "lte": max_price}}
            }
        })
        return result['hits']['hits']
    
    def search_by_category(self, category):
        """Find products in category"""
        result = self.es.search(index=self.index, body={
            "query": {"term": {"category": category}}
        })
        return result['hits']['hits']
    
    def get_stats(self):
        """Get product statistics"""
        result = self.es.search(index=self.index, body={
            "size": 0,
            "aggs": {
                "avg_price": {"avg": {"field": "price"}},
                "avg_rating": {"avg": {"field": "rating"}},
                "by_category": {"terms": {"field": "category", "size": 10}}
            }
        })
        return result['aggregations']

# Usage
engine = ProductSearchEngine()
engine.create_index()

# Add products
products = [
    (1, {"name": "Laptop", "category": "Electronics", "price": 999, "rating": 4.5, "in_stock": True}),
    (2, {"name": "Mouse", "category": "Accessories", "price": 25, "rating": 4.0, "in_stock": True}),
    (3, {"name": "Keyboard", "category": "Accessories", "price": 75, "rating": 4.2, "in_stock": False}),
]

for pid, pdata in products:
    engine.index_product(pid, pdata)

# Search
print("Laptop search:")
results = engine.search_by_name("laptop")
for hit in results:
    print(hit['_source'])

print("\nPrice range 50-300:")
results = engine.search_by_price_range(50, 300)
for hit in results:
    print(hit['_source'])

print("\nStats:", engine.get_stats())
```

---

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **Index** | Collection of documents (like a table) |
| **Document** | JSON object with data |
| **Shard** | Partition of index for scalability |
| **Replica** | Copy of shard for availability |
| **Mapping** | Schema definition for fields |
| **Query** | Request to search/filter data |
| **Aggregation** | Statistical analysis on data |
| **Analyzer** | Processes text for search |

---

## Exercises

1. Create an index and add sample documents
2. Perform various search queries
3. Calculate statistics using aggregations
4. Build a simple search engine for products
5. Update and delete documents

---

## Next Steps (Day 2)
- Advanced mappings and analyzers
- Complex queries and filters
- Aggregations and analytics
- Index optimization and management
- Integration with other systems
