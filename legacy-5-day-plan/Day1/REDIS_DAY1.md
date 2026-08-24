# Day 1: Redis - Introduction & Setup

## Time Allocation: 30-40 minutes

### What is Redis?

**Redis** (Remote Dictionary Server) is an open-source, in-memory data structure store used as a database, cache, and message broker. It's blazingly fast because it stores data in RAM rather than on disk.

#### Key Characteristics:
- **In-Memory Storage**: Stores data in RAM for microsecond-level response times
- **Key-Value Store**: Simple structure with keys mapping to values
- **Single-Threaded**: Uses event-driven I/O, eliminating race conditions
- **Persistence**: Optional RDB snapshots and AOF (append-only file) for durability
- **Data Structures**: Supports strings, lists, sets, hashes, sorted sets, streams, and more

#### Architecture:
```
Client ----> Redis Server (Single Thread Event Loop) ----> Memory (RAM)
                    |
                    |---> Persistence Layer (RDB/AOF)
                    |---> Replication (Master-Slave)
                    |---> Pub/Sub
```

#### Why Redis?
1. **Speed**: In-memory access = microseconds vs milliseconds on disk
2. **Simplicity**: Single-threaded, no complex locking
3. **Versatility**: Works as cache, session store, job queue, leaderboard
4. **Atomic Operations**: Guarantees atomicity for operations

---

## Installation & Setup

### Option 1: Docker (Recommended)
```bash
docker run -d -p 6379:6379 redis:latest
docker exec -it <container_id> redis-cli
```

### Option 2: Homebrew (macOS)
```bash
brew install redis
redis-server          # Start server
redis-cli             # Connect to server in another terminal
```

### Option 3: From Source
```bash
wget https://github.com/redis/redis/archive/7.0.tar.gz
tar xzf 7.0.tar.gz
cd redis-7.0
make
./src/redis-server
```

---

## Basic Commands & Data Types

### 1. Strings (Simplest Data Type)
Strings are the fundamental data type in Redis. Can store text, numbers, or binary data (up to 512MB).

**Code Example - Python:**
```python
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# SET: Store a string
r.set('user:1:name', 'Alice')
r.set('user:1:age', '25')
r.set('counter', 0)

# GET: Retrieve a string
name = r.get('user:1:name')
print(f"Name: {name}")  # Output: Alice

# APPEND: Add to string
r.append('user:1:name', ' Smith')
print(r.get('user:1:name'))  # Output: Alice Smith

# INCR/DECR: Increment/Decrement numbers
r.incr('counter')
print(r.get('counter'))  # Output: 1

# MSET/MGET: Set/Get multiple keys
r.mset({'user:2:name': 'Bob', 'user:2:age': '30'})
users = r.mget('user:1:name', 'user:2:name')
print(users)  # Output: ['Alice Smith', 'Bob']

# EXPIRE: Set expiration time (TTL)
r.set('temp_token', 'abc123')
r.expire('temp_token', 300)  # Expires in 300 seconds
ttl = r.ttl('temp_token')
print(f"TTL: {ttl} seconds")
```

**CLI Commands:**
```bash
SET user:1:name "Alice"
GET user:1:name
APPEND user:1:name " Smith"
INCR counter
MSET key1 val1 key2 val2
MGET key1 key2
EXPIRE temp_token 300
TTL temp_token
DEL user:1:name
EXISTS user:1:name
```

---

### 2. Lists (Ordered Collections)
Lists are ordered collections of strings. Elements are indexed (0-based). Useful for queues, stacks.

**Code Example - Python:**
```python
# LPUSH: Insert at head (left)
r.lpush('queue', 'task1', 'task2', 'task3')

# RPUSH: Insert at tail (right)
r.rpush('queue', 'task4')

# LRANGE: Get range of elements
tasks = r.lrange('queue', 0, -1)
print(f"All tasks: {tasks}")
# Output: ['task3', 'task2', 'task1', 'task4']

# LPOP/RPOP: Remove from left/right
first = r.lpop('queue')
last = r.rpop('queue')
print(f"Processed: {first}, {last}")

# LLEN: Length
length = r.llen('queue')
print(f"Queue length: {length}")

# LINDEX: Get element at index
element = r.lindex('queue', 0)
print(f"First element: {element}")

# LTRIM: Keep only specified range
r.ltrim('queue', 0, 10)  # Keep first 11 elements
```

**CLI Commands:**
```bash
LPUSH queue task1 task2 task3
RPUSH queue task4
LRANGE queue 0 -1
LPOP queue
RPOP queue
LLEN queue
LINDEX queue 0
```

---

### 3. Hashes (Field-Value Pairs)
Hashes are maps of strings to strings. Perfect for representing objects.

**Code Example - Python:**
```python
# HSET: Set hash fields
r.hset('user:1', mapping={
    'name': 'Alice',
    'age': '25',
    'email': 'alice@example.com',
    'country': 'USA'
})

# HGET: Get single field
name = r.hget('user:1', 'name')
print(f"Name: {name}")  # Output: Alice

# HGETALL: Get all fields
user = r.hgetall('user:1')
print(user)
# Output: {'name': 'Alice', 'age': '25', 'email': 'alice@example.com', 'country': 'USA'}

# HMGET: Get multiple fields
info = r.hmget('user:1', 'name', 'email')
print(info)  # Output: ['Alice', 'alice@example.com']

# HLEN: Number of fields
field_count = r.hlen('user:1')
print(f"Fields: {field_count}")  # Output: 4

# HEXISTS: Check if field exists
has_phone = r.hexists('user:1', 'phone')
print(f"Has phone: {has_phone}")  # Output: False

# HDEL: Delete field
r.hdel('user:1', 'country')

# HKEYS/HVALS: Get all keys/values
keys = r.hkeys('user:1')
values = r.hvals('user:1')
print(f"Keys: {keys}, Values: {values}")
```

**CLI Commands:**
```bash
HSET user:1 name Alice age 25 email alice@example.com
HGET user:1 name
HGETALL user:1
HMGET user:1 name email
HLEN user:1
HEXISTS user:1 phone
HDEL user:1 country
HKEYS user:1
HVALS user:1
```

---

### 4. Sets (Unique Collections)
Sets are unordered collections of unique strings. Useful for tags, memberships, deduplication.

**Code Example - Python:**
```python
# SADD: Add to set
r.sadd('user:1:tags', 'python', 'redis', 'database')
r.sadd('user:2:tags', 'redis', 'nodejs', 'docker')

# SMEMBERS: Get all members
tags = r.smembers('user:1:tags')
print(f"Tags: {tags}")

# SCARD: Count members
count = r.scard('user:1:tags')
print(f"Tag count: {count}")

# SISMEMBER: Check membership
is_member = r.sismember('user:1:tags', 'python')
print(f"Has python tag: {is_member}")  # Output: True

# SINTER: Set intersection
common = r.sinter('user:1:tags', 'user:2:tags')
print(f"Common tags: {common}")  # Output: {'redis'}

# SUNION: Set union
all_tags = r.sunion('user:1:tags', 'user:2:tags')
print(f"All tags: {all_tags}")

# SDIFF: Set difference
unique_to_user1 = r.sdiff('user:1:tags', 'user:2:tags')
print(f"Unique to user1: {unique_to_user1}")

# SREM: Remove member
r.srem('user:1:tags', 'database')
```

**CLI Commands:**
```bash
SADD user:1:tags python redis database
SADD user:2:tags redis nodejs docker
SMEMBERS user:1:tags
SCARD user:1:tags
SISMEMBER user:1:tags python
SINTER user:1:tags user:2:tags
SUNION user:1:tags user:2:tags
SDIFF user:1:tags user:2:tags
SREM user:1:tags database
```

---

### 5. Sorted Sets (Ordered with Score)
Similar to sets but each member has a score. Members are ordered by score. Useful for leaderboards, rankings.

**Code Example - Python:**
```python
# ZADD: Add members with scores
r.zadd('leaderboard', {
    'alice': 1000,
    'bob': 950,
    'charlie': 1100,
    'diana': 850
})

# ZRANGE: Get by rank (lowest to highest score)
# ZRANGE(key, start, stop, withscores=True)
top_players = r.zrange('leaderboard', 0, -1, withscores=True)
print("Top players (ascending):", top_players)

# ZREVRANGE: Get by rank (highest to lowest score)
top_players_desc = r.zrevrange('leaderboard', 0, -1, withscores=True)
print("Top players (descending):", top_players_desc)

# ZRANK: Get rank (0-indexed)
rank = r.zrank('leaderboard', 'alice')
print(f"Alice rank: {rank}")

# ZSCORE: Get score
score = r.zscore('leaderboard', 'alice')
print(f"Alice score: {score}")

# ZCARD: Count members
count = r.zcard('leaderboard')
print(f"Total players: {count}")

# ZINCRBY: Increment score
r.zincrby('leaderboard', 50, 'bob')
print(f"Bob's new score: {r.zscore('leaderboard', 'bob')}")

# ZREM: Remove member
r.zrem('leaderboard', 'diana')

# ZCOUNT: Count members in score range
count_above_900 = r.zcount('leaderboard', 900, float('inf'))
print(f"Players with score > 900: {count_above_900}")
```

**CLI Commands:**
```bash
ZADD leaderboard 1000 alice 950 bob 1100 charlie 850 diana
ZRANGE leaderboard 0 -1 WITHSCORES
ZREVRANGE leaderboard 0 -1 WITHSCORES
ZRANK leaderboard alice
ZSCORE leaderboard alice
ZCARD leaderboard
ZINCRBY leaderboard 50 bob
ZREM leaderboard diana
ZCOUNT leaderboard 900 inf
```

---

## Practical Example: Session Cache

```python
import redis
import json
from datetime import datetime

class SessionManager:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        self.session_ttl = 3600  # 1 hour
    
    def create_session(self, user_id, user_data):
        """Create a new session"""
        session_key = f"session:{user_id}"
        session_data = {
            'user_id': user_id,
            'data': json.dumps(user_data),
            'created_at': datetime.now().isoformat()
        }
        self.r.hset(session_key, mapping=session_data)
        self.r.expire(session_key, self.session_ttl)
        print(f"Session created for user {user_id}")
    
    def get_session(self, user_id):
        """Get session data"""
        session_key = f"session:{user_id}"
        session = self.r.hgetall(session_key)
        if session:
            session['data'] = json.loads(session['data'])
        return session
    
    def update_session(self, user_id, updates):
        """Update session data"""
        session_key = f"session:{user_id}"
        if self.r.exists(session_key):
            self.r.hset(session_key, mapping=updates)
            self.r.expire(session_key, self.session_ttl)
    
    def delete_session(self, user_id):
        """Delete session"""
        session_key = f"session:{user_id}"
        self.r.delete(session_key)

# Usage
sm = SessionManager()
sm.create_session('user123', {'name': 'Alice', 'email': 'alice@example.com'})
print(sm.get_session('user123'))
sm.update_session('user123', {'last_action': 'viewed_product'})
print(sm.get_session('user123'))
```

---

## Key Concepts to Remember

| Concept | Description |
|---------|-------------|
| **String** | Simple text/number value, max 512MB |
| **List** | Ordered collection, allows duplicates |
| **Hash** | Object-like structure with fields and values |
| **Set** | Unordered unique collection |
| **Sorted Set** | Set with score-based ordering |
| **TTL** | Time-to-live, auto-expiration |
| **Atomic** | Operation completes as one unit, no interruption |

---

## Exercises

1. Create a user profile hash with name, age, email
2. Implement a simple task queue using lists (LPUSH/RPOP)
3. Build a tag system using sets and find common tags
4. Create a leaderboard using sorted sets

---

## Next Steps (Day 2)
- Advanced data types (Streams, Bitmaps)
- Transactions and Pub/Sub
- Persistence mechanisms (RDB, AOF)
