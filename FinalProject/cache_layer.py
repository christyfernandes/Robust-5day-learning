"""
Day 5 Final Project: Redis Cache Layer
Session management, metrics, and real-time caching
"""

import redis
import json
from datetime import datetime, timedelta
from functools import wraps
import time

class CacheLayer:
    """Redis-based caching and session management"""
    
    def __init__(self, host='localhost', port=6379):
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self.redis.ping()
            print("✓ Connected to Redis")
        except Exception as e:
            print(f"✗ Failed to connect to Redis: {e}")
            raise
    
    def cache_user_session(self, user_id, session_data, ttl_hours=24):
        """Store user session with TTL"""
        key = f'session:{user_id}'
        try:
            self.redis.hset(key, mapping=session_data)
            self.redis.expire(key, ttl_hours * 3600)
            print(f"[Cache] Cached session for {user_id}")
        except Exception as e:
            print(f"[Cache ERROR] Failed to cache session: {e}")
    
    def get_user_session(self, user_id):
        """Retrieve user session"""
        key = f'session:{user_id}'
        try:
            session = self.redis.hgetall(key)
            return session if session else None
        except Exception as e:
            print(f"[Cache ERROR] Failed to retrieve session: {e}")
            return None
    
    def track_user_activity(self, user_id, event_type, event_data=None):
        """Track user activity for real-time metrics"""
        key = f'activity:{user_id}'
        try:
            activity = {
                'type': event_type,
                'timestamp': datetime.now().isoformat(),
                **(event_data or {})
            }
            self.redis.lpush(key, json.dumps(activity))
            self.redis.ltrim(key, 0, 99)  # Keep last 100 events
            self.redis.expire(key, 3600)  # Expire after 1 hour
        except Exception as e:
            print(f"[Cache ERROR] Failed to track activity: {e}")
    
    def increment_user_metric(self, user_id, metric_name, amount=1):
        """Increment metric for user"""
        key = f'metrics:{user_id}:{metric_name}'
        try:
            self.redis.incrby(key, amount)
            self.redis.expire(key, 86400)  # 24 hour window
        except Exception as e:
            print(f"[Cache ERROR] Failed to increment metric: {e}")
    
    def get_user_metrics(self, user_id):
        """Get all metrics for user"""
        pattern = f'metrics:{user_id}:*'
        metrics = {}
        
        try:
            for key in self.redis.scan_iter(match=pattern):
                metric_name = key.split(':')[-1]
                value = self.redis.get(key)
                metrics[metric_name] = int(value) if value else 0
            
            return metrics
        except Exception as e:
            print(f"[Cache ERROR] Failed to get metrics: {e}")
            return {}
    
    def add_to_leaderboard(self, leaderboard_name, user_id, score):
        """Add/update user in leaderboard (sorted set)"""
        key = f'leaderboard:{leaderboard_name}'
        try:
            self.redis.zadd(key, {user_id: score})
            self.redis.expire(key, 86400)  # 24 hour expiration
        except Exception as e:
            print(f"[Cache ERROR] Failed to add to leaderboard: {e}")
    
    def get_leaderboard_top(self, leaderboard_name, limit=10):
        """Get top N users in leaderboard"""
        key = f'leaderboard:{leaderboard_name}'
        try:
            # Get in descending order (highest score first)
            return self.redis.zrevrange(key, 0, limit-1, withscores=True)
        except Exception as e:
            print(f"[Cache ERROR] Failed to get leaderboard: {e}")
            return []
    
    def get_leaderboard_rank(self, leaderboard_name, user_id):
        """Get user's rank in leaderboard"""
        key = f'leaderboard:{leaderboard_name}'
        try:
            # zrevrank gives rank in descending order (0-indexed)
            rank = self.redis.zrevrank(key, user_id)
            return rank + 1 if rank is not None else None
        except Exception as e:
            print(f"[Cache ERROR] Failed to get rank: {e}")
            return None
    
    def cache_computed_value(self, key, value, ttl_seconds=300):
        """Generic cache set with TTL"""
        try:
            self.redis.set(key, json.dumps(value), ex=ttl_seconds)
        except Exception as e:
            print(f"[Cache ERROR] Failed to cache value: {e}")
    
    def get_cached_value(self, key):
        """Generic cache get"""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"[Cache ERROR] Failed to get cached value: {e}")
            return None
    
    def delete_key(self, key):
        """Delete a key"""
        try:
            return self.redis.delete(key)
        except Exception as e:
            print(f"[Cache ERROR] Failed to delete key: {e}")
            return 0
    
    def get_stats(self):
        """Get Redis statistics"""
        try:
            info = self.redis.info()
            return {
                'memory_used_mb': info['used_memory'] / 1024 / 1024,
                'connected_clients': info['connected_clients'],
                'total_commands': info['total_commands_processed'],
                'uptime_seconds': info['uptime_in_seconds']
            }
        except Exception as e:
            print(f"[Cache ERROR] Failed to get stats: {e}")
            return {}

# Example usage
if __name__ == '__main__':
    cache = CacheLayer()
    
    # Store session
    cache.cache_user_session('user_0001', {
        'name': 'John Doe',
        'tier': 'gold',
        'last_login': datetime.now().isoformat()
    })
    
    # Get session
    session = cache.get_user_session('user_0001')
    print(f"Session: {session}")
    
    # Track activity
    cache.track_user_activity('user_0001', 'purchase', {'amount': 99.99})
    
    # Metrics
    cache.increment_user_metric('user_0001', 'total_purchases')
    cache.increment_user_metric('user_0001', 'total_spent', 99.99)
    
    metrics = cache.get_user_metrics('user_0001')
    print(f"Metrics: {metrics}")
    
    # Leaderboard
    cache.add_to_leaderboard('daily_spenders', 'user_0001', 999.99)
    cache.add_to_leaderboard('daily_spenders', 'user_0002', 850.50)
    cache.add_to_leaderboard('daily_spenders', 'user_0003', 1200.00)
    
    top = cache.get_leaderboard_top('daily_spenders', 5)
    print(f"Top spenders: {top}")
    
    rank = cache.get_leaderboard_rank('daily_spenders', 'user_0001')
    print(f"User_0001 rank: {rank}")
    
    # Stats
    stats = cache.get_stats()
    print(f"Redis stats: {stats}")
