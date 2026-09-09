# redis-py

A lightweight Redis server built from scratch in pure Python using `asyncio`.

I started building this project to upskill myself, dive deep into systems programming, and understand what actually happens under the hood of an in-memory database like Redis, from parsing the raw binary wire protocol to managing concurrency, asynchronous blocking operations, and low-level data structures.

It speaks the official **RESP** (Redis Serialization Protocol), meaning you can interact with it directly using the standard `redis-cli` or any official Redis client library. Best of all: **zero external dependencies**, just the Python standard library.

Going forward, this project isn't just about checking off features—it's about diving deeper into performance and memory optimization, profiling bottlenecks, and replacing high-level Python abstractions with custom, minimal data structures tailored for the job.

---

## Highlights

- **Zero Dependencies**: Built entirely with Python's standard library (`asyncio`, `collections`, `dataclasses`).
- **Real RESP Protocol**: Custom hand-crafted parser and serializer compatible with `redis-cli`.
- **Concurrent & Non-blocking**: Uses Python's asynchronous event loop to handle multiple client connections smoothly.
- **6 Core Data Types**: Strings, Lists, Hashes, Sets, Sorted Sets (ZSets), and Streams.
- **Async Blocking Commands**: True non-blocking waiters for `BLPOP`, `BRPOP`, and `XREAD BLOCK` powered by `asyncio.Future`.
- **Pub/Sub Messaging**: Real-time message broadcasting across connected clients with `SUBSCRIBE`, `UNSUBSCRIBE`, and `PUBLISH`.
- **Multiple DBs & Key Expiration**: Configurable databases (`SELECT 0-15`) with passive (lazy) TTL expiration (`EXPIRE`, `PEXPIRE`, `PERSIST`).

---

## Quick Start

### 1. Requirements
- Python 3.10 or higher.

### 2. Run the Server
Clone the repo and start the server:

```bash
python server.py
```

By default, the server listens on `localhost:6379` with 16 database instances. You can customize this with command-line flags:

```bash
python server.py --host 0.0.0.0 --port 6379 --db_count 16
```

### 3. Connect with `redis-cli`
Open another terminal and connect just like you would to any Redis instance:

```bash
redis-cli
```

Or connect programmatically using Python:

```python
import redis

r = redis.Redis(host="localhost", port=6379, protocol=2, decode_responses=True)

r.set("greeting", "Hello from redis-py!")
print(r.get("greeting"))  # Output: Hello from redis-py!
```

---

## Supported Commands

Here's what is implemented so far:

### Strings
- `GET key`
- `SET key value [EX seconds | PX milliseconds] [NX | XX]`
- `INCR key` / `DECR key`
- `INCRBY key increment` / `DECRBY key decrement`
- `APPEND key value`
- `STRLEN key`

### Lists
- `LPUSH key value [value ...]` / `RPUSH key value [value ...]`
- `LPOP key [count]` / `RPOP key [count]`
- `LLEN key`
- `LRANGE key start stop`
- `LINDEX key index`
- `LTRIM key start stop`
- `BLPOP key [key ...] timeout` *(Blocking left pop)*
- `BRPOP key [key ...] timeout` *(Blocking right pop)*

### Hashes
- `HSET key field value [field value ...]`
- `HGET key field`
- `HMGET key field [field ...]`
- `HGETALL key`
- `HDEL key field [field ...]`
- `HEXISTS key field`
- `HLEN key`
- `HKEYS key`
- `HVALS key`

### Sets
- `SADD key member [member ...]`
- `SREM key member [member ...]`
- `SISMEMBER key member`
- `SMEMBERS key`
- `SCARD key`
- `SPOP key [count]`
- `SRANDMEMBER key [count]`
- `SINTER key [key ...]` *(Set intersection)*
- `SUNION key [key ...]` *(Set union)*
- `SDIFF key [key ...]` *(Set difference)*

### Sorted Sets (ZSets)
- `ZADD key score member [score member ...]`
- `ZSCORE key member`
- `ZRANK key member` / `ZREVRANK key member`
- `ZRANGE key start stop [WITHSCORES]`
- `ZREVRANGE key start stop [WITHSCORES]`
- `ZREM key member [member ...]`
- `ZCARD key`
- `ZCOUNT key min max`

### Streams
- `XADD key id field value [field value ...]` *(Supports auto ID `*` and auto-sequence `ms-*`)*
- `XRANGE key start end` *(Supports `-` and `+`)*
- `XREVRANGE key end start`
- `XLEN key`
- `XREAD [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] id [id ...]`

### Pub/Sub
- `SUBSCRIBE channel [channel ...]`
- `UNSUBSCRIBE [channel ...]`
- `PUBLISH channel message`

### Server & Database Management
- `PING [message]`
- `ECHO message`
- `SELECT index`
- `TYPE key`
- `DEL key [key ...]`
- `EXISTS key [key ...]`
- `DBSIZE`
- `FLUSHDB`
- `EXPIRE key seconds` / `PEXPIRE key milliseconds`
- `TTL key` / `PTTL key`
- `PERSIST key`

---

## How It's Structured

If you want to poke around the codebase, here's the lay of the land:

```text
.
├── server.py        # Async TCP server setup and connection loop
├── client.py        # Client connection lifecycle, state, and message dispatching
├── resp.py          # Custom RESP2 protocol parser and response formatter
├── executor.py      # Route registry (@executor decorator) mapping commands to handlers
├── models.py        # Data models (Entry, RedisType, Waiter)
├── arg_parser.py    # Command-line flags parser (--host, --port, --db_count)
├── commands/        # Command handler implementations organized by data type
│   ├── string.py
│   ├── list.py
│   ├── hash.py
│   ├── set.py
│   ├── sorted_set.py
│   ├── stream.py
│   ├── channel.py   # Pub/Sub commands
│   ├── database.py  # Generic key/DB operations
│   └── client.py    # PING, ECHO, SELECT
└── storage/         # Core in-memory storage engines and data structures
    ├── database.py  # Single DB instance with lazy TTL expiration & waiter queue
    ├── store.py     # Thread-safe singleton holding multiple Database instances
    ├── channel.py   # Pub/Sub channels and subscriber connections
    └── ...          # Type-specific storage logic
```

### A peek under the hood

1. **Networking**: `asyncio.start_server()` accepts inbound socket connections. Each connection gets wrapped into a `Client` instance with dedicated reader/writer streams.
2. **RESP Parsing**: Incoming bytes are read from the socket and parsed directly into command arguments based on Redis Serialization Protocol standards.
3. **Execution**: The `Executor` looks up the command in its registered route map and runs the handler asynchronously.
4. **Blocking Operations**: For blocking commands like `BLPOP` or `XREAD BLOCK`, a `Waiter` containing an `asyncio.Future` is registered against the requested key. When another client pushes data to that key, the waiter is popped, its future is resolved, and the waiting client wakes up immediately.

---

## What's Next & Roadmap

This project is an ongoing journey. Beyond adding new capabilities, the upcoming focus is on profiling and optimizing existing bottlenecks, diving into lower-level mechanics, and building custom minimal data structures rather than relying solely on Python's built-in collections.

### Upcoming Milestones

- [ ] **Transactions**: Atomic execution with `MULTI`, `EXEC`, `DISCARD`, and optimistic concurrency control via `WATCH`.
- [ ] **Persistence**: Durability through point-in-time RDB snapshots and Append-Only File (AOF) logging with background rewrite.
- [ ] **Memory Limits & Eviction**: Configurable `maxmemory` threshold and eviction policies (e.g., `allkeys-lru`, `volatile-lru`, `allkeys-lfu`, `volatile-ttl`).
- [ ] **Replication**: Master-replica architecture with handshake, replication stream, and state synchronization.
- [ ] **Authentication & ACL**: Password protection (`AUTH`) and granular Access Control Lists for commands and keys.
- [ ] **Optimizations & Custom Data Structures**:
  - Replacing high-level Python collections with custom, memory-efficient data structures (e.g., a hand-rolled **Skip List** for Sorted Sets).
  - Profiling memory footprint and reducing allocation overhead.
  - Designing a minimal **Radix Tree** for stream indexing and memory efficiency.