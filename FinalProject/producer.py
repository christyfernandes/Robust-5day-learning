"""
Day 5 Final Project: Event Producer
Generates realistic e-commerce events and sends them to Kafka
"""

from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime
import argparse

class EventGenerator:
    """Generate realistic e-commerce events"""
    
    PRODUCTS = ['laptop', 'mouse', 'keyboard', 'monitor', 'headphones', 
                'webcam', 'charger', 'dock', 'cable', 'stand']
    
    REGIONS = ['us-east', 'us-west', 'eu-west', 'ap-south', 'au-east']
    
    DEVICES = ['web', 'mobile', 'tablet']
    
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                timeout_ms=10000
            )
            print("✓ Connected to Kafka")
        except Exception as e:
            print(f"✗ Failed to connect to Kafka: {e}")
            raise
    
    def generate_users(self, num_users=100):
        """Pre-generate user database"""
        users = []
        for i in range(num_users):
            users.append({
                'user_id': f'user_{i:05d}',
                'name': f'User {i}',
                'region': random.choice(self.REGIONS),
                'tier': random.choice(['bronze', 'silver', 'gold', 'platinum']),
                'device': random.choice(self.DEVICES)
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
            'device': user['device'],
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
                'payment_method': random.choice(['credit_card', 'paypal', 'apple_pay', 'google_pay'])
            })
        
        elif event_type == 'search':
            event.update({
                'search_query': random.choice(['laptop', 'mouse', 'keyboard', 'gaming', 'wireless']),
                'results_count': random.randint(0, 100)
            })
        
        elif event_type == 'login':
            event.update({
                'login_method': random.choice(['password', 'oauth', 'biometric'])
            })
        
        elif event_type == 'logout':
            event.update({
                'session_duration': random.randint(60, 3600)
            })
        
        return event
    
    def stream_events(self, duration_seconds=300, events_per_second=50):
        """Stream events to Kafka"""
        users = self.generate_users(100)  # 100 active users
        
        event_types = ['page_view', 'search', 'add_to_cart', 'purchase', 'login', 'logout']
        event_weights = [0.35, 0.15, 0.15, 0.10, 0.15, 0.10]
        
        start_time = time.time()
        event_count = 0
        
        print(f"Starting event stream for {duration_seconds} seconds...")
        print(f"Target rate: {events_per_second} events/second")
        
        while time.time() - start_time < duration_seconds:
            for _ in range(events_per_second):
                try:
                    user = random.choice(users)
                    event_type = random.choices(event_types, weights=event_weights)[0]
                    event = self.generate_event(user, event_type)
                    
                    # Send to Kafka with user_id as key
                    future = self.producer.send(
                        'user_events',
                        value=event,
                        key=user['user_id'].encode()
                    )
                    
                    # Wait for send to complete (error handling)
                    record_metadata = future.get(timeout=5)
                    
                    event_count += 1
                    
                    if event_count % 100 == 0:
                        print(f"[Producer] Generated {event_count} events | "
                              f"Topic: {record_metadata.topic}, "
                              f"Partition: {record_metadata.partition}")
                
                except Exception as e:
                    print(f"[ERROR] Failed to send event: {e}")
            
            time.sleep(1)  # Emit events_per_second per second
        
        self.producer.flush()
        self.producer.close()
        print(f"[Producer] Finished. Total events generated: {event_count}")

def main():
    parser = argparse.ArgumentParser(description='Generate e-commerce events')
    parser.add_argument('--duration', type=int, default=300, help='Duration in seconds')
    parser.add_argument('--rate', type=int, default=50, help='Events per second')
    
    args = parser.parse_args()
    
    try:
        gen = EventGenerator()
        gen.stream_events(duration_seconds=args.duration, events_per_second=args.rate)
    except KeyboardInterrupt:
        print("\n[Producer] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == '__main__':
    main()
