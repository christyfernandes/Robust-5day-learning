"""
Day 5 Final Project: Main Pipeline Orchestrator
Ties together all components: Producer, Kafka, Redis, Elasticsearch
"""

import threading
import time
import json
from datetime import datetime
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from producer import EventGenerator
from cache_layer import CacheLayer
from es_indexer import ElasticsearchIndexer


class DataPipeline:
    """Orchestrate entire real-time analytics pipeline"""
    
    def __init__(self):
        print("=" * 60)
        print("E-COMMERCE REAL-TIME ANALYTICS PLATFORM")
        print("=" * 60)
        
        self.cache = CacheLayer()
        self.indexer = ElasticsearchIndexer()
        self.should_stop = False
        self.event_count = 0
    
    def setup_kafka(self):
        """Setup Kafka topics"""
        
        try:
            admin = KafkaAdminClient(
                bootstrap_servers=['localhost:9092'],
                client_id='pipeline-admin'
            )
            
            # Create topic
            topic = NewTopic(
                name='user_events',
                num_partitions=3,
                replication_factor=1
            )
            
            try:
                admin.create_topics(new_topics=[topic], validate_only=False)
                print("[Kafka] Created topic: user_events")
            except TopicAlreadyExistsError:
                print("[Kafka] Topic already exists: user_events")
            
            admin.close()
        except Exception as e:
            print(f"[Kafka ERROR] Failed to setup topics: {e}")
    
    def consumer_worker(self, duration_seconds=300):
        """Consume from Kafka and process events"""
        
        try:
            consumer = KafkaConsumer(
                'user_events',
                bootstrap_servers=['localhost:9092'],
                group_id='pipeline-consumer-group',
                auto_offset_reset='earliest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                session_timeout_ms=30000,
                enable_auto_commit=True,
                max_poll_records=100
            )
            
            print("[Consumer] Started consuming events...")
            
            events_buffer = []
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds and not self.should_stop:
                try:
                    message = consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, records in message.items():
                        for record in records:
                            event = record.value
                            
                            # Process event
                            self.process_event(event)
                            
                            events_buffer.append(event)
                            self.event_count += 1
                            
                            # Batch index to Elasticsearch
                            if len(events_buffer) >= 50:
                                self.indexer.index_events_bulk(events_buffer)
                                events_buffer = []
                            
                            if self.event_count % 100 == 0:
                                print(f"[Pipeline] Processed {self.event_count} events")
                
                except Exception as e:
                    print(f"[Consumer ERROR] {e}")
                    continue
            
            # Index remaining events
            if events_buffer:
                self.indexer.index_events_bulk(events_buffer)
            
            consumer.close()
            print(f"[Consumer] Stopped. Total events: {self.event_count}")
        
        except Exception as e:
            print(f"[Consumer ERROR] Failed to consume: {e}")
    
    def process_event(self, event):
        """Process individual event"""
        
        user_id = event['user_id']
        event_type = event['event_type']
        
        # Cache: Track user activity
        self.cache.track_user_activity(user_id, event_type)
        
        # Cache: Update metrics based on event type
        if event_type == 'page_view':
            self.cache.increment_user_metric(user_id, 'page_views')
        
        elif event_type == 'search':
            self.cache.increment_user_metric(user_id, 'searches')
        
        elif event_type == 'add_to_cart':
            self.cache.increment_user_metric(user_id, 'cart_additions')
            if 'price' in event:
                self.cache.increment_user_metric(user_id, 'cart_value', event['price'])
        
        elif event_type == 'purchase':
            self.cache.increment_user_metric(user_id, 'purchases')
            amount = event.get('total_amount', 0)
            self.cache.increment_user_metric(user_id, 'lifetime_value', amount)
            
            # Update leaderboard
            self.cache.add_to_leaderboard('top_spenders', user_id, amount)
        
        elif event_type == 'login':
            self.cache.increment_user_metric(user_id, 'logins')
        
        # Cache: Store session
        session = {
            'tier': event['user_tier'],
            'region': event['user_region'],
            'device': event['device'],
            'last_activity': event['timestamp']
        }
        self.cache.cache_user_session(user_id, session)
    
    def producer_worker(self, duration_seconds=300):
        """Run event producer"""
        
        try:
            gen = EventGenerator()
            gen.stream_events(duration_seconds=duration_seconds, events_per_second=50)
        except KeyboardInterrupt:
            print("\n[Producer] Interrupted")
        except Exception as e:
            print(f"[Producer ERROR] {e}")
    
    def report_results(self):
        """Generate and display results"""
        
        print("\n" + "=" * 60)
        print("PIPELINE RESULTS & ANALYTICS")
        print("=" * 60 + "\n")
        
        # Wait for indexing
        print("[Pipeline] Waiting for indexing to complete...")
        time.sleep(2)
        
        # 1. Redis Metrics
        print("[REDIS] Top 5 Spenders (Leaderboard):")
        top_spenders = self.cache.get_leaderboard_top('top_spenders', 5)
        if top_spenders:
            for i, (user, score) in enumerate(top_spenders, 1):
                print(f"  {i}. {user}: ${score:.2f}")
        else:
            print("  No spenders yet")
        
        # 2. Elasticsearch Document Count
        doc_count = self.indexer.count_documents()
        print(f"\n[ELASTICSEARCH] Total Events Indexed: {doc_count}")
        
        # 3. Elasticsearch Analytics
        print("\n[ELASTICSEARCH] Event Distribution:")
        analytics = self.indexer.get_analytics()
        
        if 'events_by_type' in analytics:
            for bucket in analytics['events_by_type']['buckets']:
                percentage = (bucket['doc_count'] / doc_count * 100) if doc_count > 0 else 0
                print(f"  {bucket['key']}: {bucket['doc_count']} ({percentage:.1f}%)")
        
        # 4. Revenue by Region
        print("\n[ELASTICSEARCH] Revenue by Region:")
        if 'revenue_by_region' in analytics:
            for bucket in analytics['revenue_by_region']['buckets']:
                print(f"  {bucket['key']}: ${bucket['total_revenue']['value']:.2f} "
                      f"(avg: ${bucket['avg_transaction']['value']:.2f})")
        
        # 5. Revenue by Tier
        print("\n[ELASTICSEARCH] Revenue by User Tier:")
        if 'revenue_by_tier' in analytics:
            for bucket in analytics['revenue_by_tier']['buckets']:
                print(f"  {bucket['key']}: ${bucket['total_spent']['value']:.2f} "
                      f"({bucket['transaction_count']['value']} transactions)")
        
        # 6. Popular Products
        print("\n[ELASTICSEARCH] Top 10 Products:")
        if 'popular_products' in analytics:
            for i, bucket in enumerate(analytics['popular_products']['buckets'][:10], 1):
                print(f"  {i}. {bucket['key']}: {bucket['doc_count']} views")
        
        # 7. Top Spenders from ES
        print("\n[ELASTICSEARCH] Top 5 Spenders by Revenue:")
        top_es = self.indexer.top_spenders(5)
        if top_es:
            for i, record in enumerate(top_es, 1):
                print(f"  {i}. {record['user_id']}: ${record['total_spent']:.2f} "
                      f"({record['purchase_count']} purchases)")
        
        # 8. Summary Statistics
        print("\n[SUMMARY]")
        print(f"  Total Events Processed: {self.event_count}")
        print(f"  Total Events Indexed: {doc_count}")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        
        # 9. Redis Statistics
        redis_stats = self.cache.get_stats()
        print(f"\n[REDIS] System Stats:")
        print(f"  Memory Used: {redis_stats.get('memory_used_mb', 0):.2f} MB")
        print(f"  Connected Clients: {redis_stats.get('connected_clients', 0)}")
        
        print("\n" + "=" * 60)
    
    def run(self, duration_seconds=300):
        """Run entire pipeline"""
        
        try:
            # Setup
            print("\n[Setup] Initializing Elasticsearch...")
            self.indexer.create_index()
            
            print("[Setup] Setting up Kafka...")
            self.setup_kafka()
            
            time.sleep(2)
            
            # Start producer in background thread
            print("[Setup] Starting event producer...")
            producer_thread = threading.Thread(
                target=self.producer_worker,
                args=(duration_seconds,),
                daemon=True
            )
            producer_thread.start()
            
            # Give producer time to start
            time.sleep(2)
            
            # Start consumer (blocks until done)
            print("[Setup] Starting consumer and processor...")
            self.consumer_worker(duration_seconds=duration_seconds + 10)
            
            # Report results
            self.report_results()
        
        except KeyboardInterrupt:
            print("\n[Pipeline] Interrupted by user")
        except Exception as e:
            print(f"[Pipeline ERROR] {e}")
            raise


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='E-Commerce Real-Time Analytics Platform')
    parser.add_argument('--duration', type=int, default=60, 
                       help='Duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    pipeline = DataPipeline()
    pipeline.run(duration_seconds=args.duration)


if __name__ == '__main__':
    main()
