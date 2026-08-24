"""
Day 5 Final Project: Elasticsearch Indexer
Index events and provide search/analytics capabilities
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from datetime import datetime
import time

class ElasticsearchIndexer:
    """Index events and provide search/analytics"""
    
    def __init__(self, host='localhost', port=9200):
        try:
            self.es = Elasticsearch([f'http://{host}:{port}'])
            # Test connection
            self.es.info()
            print("✓ Connected to Elasticsearch")
        except Exception as e:
            print(f"✗ Failed to connect to Elasticsearch: {e}")
            raise
        
        self.index_name = 'user_events'
    
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
                    "device": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "unix_timestamp": {"type": "long"},
                    "total_amount": {"type": "float"},
                    "price": {"type": "float"},
                    "quantity": {"type": "integer"},
                    "product": {"type": "keyword"},
                    "products": {"type": "keyword"},
                    "page": {"type": "keyword"},
                    "search_query": {"type": "text"},
                    "session_duration": {"type": "integer"}
                }
            }
        }
        
        try:
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                print(f"[ES] Deleted existing index: {self.index_name}")
            
            self.es.indices.create(index=self.index_name, body=settings)
            print(f"[ES] Created index: {self.index_name}")
        except Exception as e:
            print(f"[ES ERROR] Failed to create index: {e}")
    
    def index_events_bulk(self, events, batch_size=1000):
        """Bulk index events"""
        
        try:
            actions = [
                {
                    "_index": self.index_name,
                    "_id": f"{e['user_id']}_{e['unix_timestamp']}_{e['event_type']}",
                    "_source": e
                }
                for e in events
            ]
            
            success, failed = bulk(self.es, actions, chunk_size=batch_size)
            print(f"[ES] Indexed {success} documents (failed: {failed})")
            return success
        except Exception as e:
            print(f"[ES ERROR] Failed to bulk index: {e}")
            return 0
    
    def search_by_user(self, user_id, size=100):
        """Search events for specific user"""
        
        try:
            query = {
                "query": {
                    "term": {"user_id": user_id}
                },
                "size": size,
                "sort": [{"unix_timestamp": {"order": "desc"}}]
            }
            
            result = self.es.search(index=self.index_name, body=query)
            return result['hits']['hits']
        except Exception as e:
            print(f"[ES ERROR] Search failed: {e}")
            return []
    
    def search_full_text(self, query_text, size=100):
        """Full-text search on events"""
        
        try:
            query = {
                "query": {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["user_name", "search_query", "product"]
                    }
                },
                "size": size
            }
            
            result = self.es.search(index=self.index_name, body=query)
            return result['hits']['hits']
        except Exception as e:
            print(f"[ES ERROR] Full-text search failed: {e}")
            return []
    
    def get_analytics(self):
        """Get analytics aggregations"""
        
        try:
            query = {
                "size": 0,
                "aggs": {
                    "events_by_type": {
                        "terms": {"field": "event_type", "size": 10}
                    },
                    "revenue_by_region": {
                        "terms": {"field": "user_region", "size": 10},
                        "aggs": {
                            "total_revenue": {"sum": {"field": "total_amount"}},
                            "avg_transaction": {"avg": {"field": "total_amount"}}
                        }
                    },
                    "revenue_by_tier": {
                        "terms": {"field": "user_tier"},
                        "aggs": {
                            "total_spent": {"sum": {"field": "total_amount"}},
                            "avg_amount": {"avg": {"field": "total_amount"}},
                            "transaction_count": {"value_count": {"field": "user_id"}}
                        }
                    },
                    "popular_products": {
                        "terms": {"field": "product", "size": 20}
                    }
                }
            }
            
            result = self.es.search(index=self.index_name, body=query)
            return result['aggregations']
        except Exception as e:
            print(f"[ES ERROR] Analytics aggregation failed: {e}")
            return {}
    
    def top_spenders(self, limit=10):
        """Get top spenders"""
        
        try:
            query = {
                "size": 0,
                "query": {"term": {"event_type": "purchase"}},
                "aggs": {
                    "top_users": {
                        "terms": {
                            "field": "user_id",
                            "size": limit,
                            "order": {"total_spent": "desc"}
                        },
                        "aggs": {
                            "total_spent": {"sum": {"field": "total_amount"}},
                            "purchase_count": {"value_count": {"field": "user_id"}}
                        }
                    }
                }
            }
            
            result = self.es.search(index=self.index_name, body=query)
            
            return [
                {
                    "user_id": b['key'],
                    "total_spent": b['total_spent']['value'],
                    "purchase_count": b['purchase_count']['value']
                }
                for b in result['aggregations']['top_users']['buckets']
            ]
        except Exception as e:
            print(f"[ES ERROR] Top spenders query failed: {e}")
            return []
    
    def count_documents(self):
        """Count total documents in index"""
        
        try:
            result = self.es.count(index=self.index_name)
            return result['count']
        except Exception as e:
            print(f"[ES ERROR] Count failed: {e}")
            return 0
    
    def get_index_stats(self):
        """Get index statistics"""
        
        try:
            stats = self.es.indices.stats(index=self.index_name)
            docs = stats['indices'][self.index_name]['primaries']['docs']
            return {
                'doc_count': docs['count'],
                'deleted_count': docs['deleted']
            }
        except Exception as e:
            print(f"[ES ERROR] Stats query failed: {e}")
            return {}

# Example usage
if __name__ == '__main__':
    indexer = ElasticsearchIndexer()
    indexer.create_index()
    
    # Sample events
    events = [
        {
            "event_type": "purchase",
            "user_id": "user_0001",
            "user_name": "Alice",
            "total_amount": 999.99,
            "user_tier": "gold",
            "user_region": "us-east",
            "device": "web",
            "timestamp": datetime.now().isoformat(),
            "unix_timestamp": int(time.time() * 1000)
        },
        {
            "event_type": "purchase",
            "user_id": "user_0002",
            "user_name": "Bob",
            "total_amount": 499.99,
            "user_tier": "silver",
            "user_region": "eu-west",
            "device": "mobile",
            "timestamp": datetime.now().isoformat(),
            "unix_timestamp": int(time.time() * 1000)
        }
    ]
    
    # Index events
    count = indexer.index_events_bulk(events)
    print(f"Indexed {count} events")
    
    # Get analytics
    analytics = indexer.get_analytics()
    print(f"Analytics: {json.dumps(analytics, indent=2)}")
    
    # Top spenders
    top = indexer.top_spenders(5)
    print(f"Top spenders: {top}")
    
    # Stats
    stats = indexer.get_index_stats()
    print(f"Index stats: {stats}")
