# Redis-from-Scratch in Python: Phase-Wise Challenge Roadmap

## Ground Rules

Before starting, define your project constraints:

* Use **Python standard library first**: `socket`, `selectors`, `threading`, `time`, `heapq`, `pickle/json/struct`, `logging`, etc.
* Avoid using `redis-py` internally. You may use it only for black-box testing.
* Make the server speak **RESP**, because Redis clients communicate with Redis using the Redis Serialization Protocol over TCP. RESP is designed to be simple, fast to parse, human-readable, and binary-safe. [\[redis.io\]](https://redis.io/docs/latest/develop/reference/protocol-spec/), [\[github.com\]](https://github.com/redis/redis-specifications/blob/master/protocol/RESP2.md)
* Build in small phases. Each phase should leave you with a working server.

***

# Phase 0: Redis Fundamentals & Project Setup

## Requirement

Understand what Redis is before implementing it: an in-memory data structure server used as a database, cache, message broker, stream processor, and more. Redis supports data types such as strings, lists, hashes, sets, sorted sets, and streams. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-stack.io\]](https://redis-stack.io/docs/data-types/)

## Implement

* Project structure:

```text
pyredis/
  server.py
  protocol/
  commands/
  storage/
  persistence/
  replication/
  tests/
  benchmarks/
```

* Basic CLI configuration:
  * `--host`
  * `--port`
  * `--dir`
  * `--dbfilename`
  * `--appendonly`
  * `--maxmemory`
  * `--maxmemory-policy`

## Expected Outcome

You should have a runnable Python process:

```bash
python server.py --port 6379
```

It does not need to support Redis yet, but it should start cleanly and log basic lifecycle events.

## What You Achieve

You establish the skeleton for a real server instead of writing a one-file toy.

## Challenge Completion Criteria

* Server starts and stops cleanly.
* Configuration is parsed.
* Logs show startup information.

***

# Phase 1: TCP Server Basics

## Requirement

Redis clients connect to Redis over TCP, usually on port `6379`; RESP is used on top of a stream-oriented connection such as TCP or Unix sockets. [\[redis.io\]](https://redis.io/docs/latest/develop/reference/protocol-spec/), [\[github.com\]](https://github.com/redis/redis-specifications/blob/master/protocol/RESP2.md)

## Implement

Start with a basic TCP server.

Features:

* Bind to host and port.
* Accept client connections.
* Read bytes from clients.
* Write bytes back.
* Support multiple sequential requests from the same connection.
* Initially, implement an echo server.

## Expected Outcome

You can connect using:

```bash
nc localhost 6379
```

and see your input echoed.

## What You Achieve

You learn the actual network layer beneath Redis.

## Challenge Completion Criteria

* Multiple clients can connect.
* Server does not crash when a client disconnects.
* Large messages do not break the server.
* Logs include connect/disconnect events.

## Stretch Goal

Implement both:

1. Thread-per-client version.
2. `selectors`-based event loop version.

Redis is known for its event-driven design, and learning both models will help you understand why Redis avoids blocking per-client I/O. [\[letsbuilds...utions.com\]](https://letsbuildsolutions.com/blog/system-design/how-redis-works-internally-single-threaded-event-loop-data-structures-persistence-and-replication/), [\[letsbuilds...utions.com\]](https://letsbuildsolutions.com/blog/system-design/how-redis-works-single-threaded-execution-data-structures-and-persistence-mechanics-from-command-to-disk/)

***

# Phase 2: RESP Parser and Encoder

## Requirement

To talk to real Redis clients, your server must parse and emit RESP. RESP supports simple strings, errors, integers, bulk strings, arrays, and null values. Clients send commands as arrays of bulk strings, and Redis replies with command-specific RESP values. [\[redis.io\]](https://redis.io/docs/latest/develop/reference/protocol-spec/), [\[github.com\]](https://github.com/redis/redis-specifications/blob/master/protocol/RESP2.md)

## Implement

RESP2 support first.

Parser must support:

* Simple String: `+OK\r\n`
* Error: `-ERR message\r\n`
* Integer: `:123\r\n`
* Bulk String: `$5\r\nhello\r\n`
* Null Bulk String: `$-1\r\n`
* Array: `*2\r\n$4\r\nPING\r\n$4\r\ntest\r\n`
* Null Array: `*-1\r\n`

Encoder must support:

* Simple string replies.
* Error replies.
* Integer replies.
* Bulk string replies.
* Array replies.
* Null replies.

## Expected Outcome

Your server can parse requests from `redis-cli`.

Example:

```bash
redis-cli -p 6379 PING
```

Response:

```text
PONG
```

## What You Achieve

You now speak the real Redis wire protocol.

## Challenge Completion Criteria

* Partial TCP reads are handled.
* Multiple commands in one buffer are handled.
* Invalid RESP returns proper errors instead of crashing.
* Parser is unit-tested independently.

## Stretch Goal

Add RESP3 later, but do not start with it. RESP2 is enough for most classic Redis client compatibility. Redis 6 introduced RESP3 opt-in support, but RESP2 remains widely supported. [\[redis.io\]](https://redis.io/docs/latest/develop/reference/protocol-spec/), [\[redis-stack.io\]](https://redis-stack.io/docs/reference/protocol-spec/)

***

# Phase 3: Command Dispatcher

## Requirement

Redis accepts a command name and arguments, then dispatches to the command implementation. This lets the server grow cleanly as commands increase.

## Implement

A command registry:

```text
PING -> ping_handler
ECHO -> echo_handler
SET  -> set_handler
GET  -> get_handler
```

Features:

* Case-insensitive command names.
* Argument count validation.
* Uniform error format.
* Command metadata:
  * name
  * arity
  * read/write flag
  * allowed in transaction?
  * allowed in pub/sub mode?

## Expected Outcome

Supported commands:

* `PING`
* `ECHO`
* `COMMAND` minimal placeholder
* Unknown command handling

## What You Achieve

You build the core execution pipeline.

## Challenge Completion Criteria

```bash
redis-cli PING
redis-cli ECHO hello
redis-cli UNKNOWN
```

all behave predictably.

## Stretch Goal

Add a `HELP` or internal command list for debugging.

***

# Phase 4: Basic Key-Value Store

## Requirement

Redis is fundamentally an in-memory data structure server. The simplest type is a string, which represents a sequence of bytes and can store text, serialized objects, counters, or binary data. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-stack.io\]](https://redis-stack.io/docs/data-types/)

## Implement

Internal storage:

```text
db = {
  key: RedisObject(type="string", value=bytes, ...)
}
```

Commands:

* `SET key value`
* `GET key`
* `DEL key [key ...]`
* `EXISTS key [key ...]`
* `TYPE key`
* `DBSIZE`
* `FLUSHDB`

## Expected Outcome

You can use your server like a basic Redis key-value database.

## What You Achieve

You now have a working in-memory Redis subset.

## Challenge Completion Criteria

```bash
redis-cli SET name Samad
redis-cli GET name
redis-cli EXISTS name
redis-cli DEL name
redis-cli GET name
```

works correctly.

## Stretch Goal

Add:

* `MSET`
* `MGET`
* `GETDEL`
* `GETSET`

***

# Phase 5: Expiry and TTL Engine

## Requirement

Redis keys can expire. Expiration can be enforced lazily when keys are accessed and actively in the background. Redis also supports cache-style behavior where keys disappear after a TTL. [\[redis.io\]](https://redis.io/docs/latest/develop/reference/eviction/), [\[redis-stack.io\]](https://redis-stack.io/docs/reference/eviction/)

## Implement

Maintain:

```text
expires = {
  key: expire_at_unix_ms
}
```

Commands:

* `EXPIRE key seconds`
* `PEXPIRE key milliseconds`
* `TTL key`
* `PTTL key`
* `PERSIST key`
* `SET key value EX seconds`
* `SET key value PX milliseconds`
* `SET key value NX`
* `SET key value XX`

Expiration logic:

* Lazy delete on access.
* Active expiry loop every N milliseconds.
* Expiry must remove key and metadata.

## Expected Outcome

Keys automatically disappear after their TTL.

## What You Achieve

You build a core cache behavior.

## Challenge Completion Criteria

```bash
redis-cli SET session abc EX 2
redis-cli GET session
sleep 3
redis-cli GET session
```

returns null after expiry.

## Stretch Goal

Add expiration events internally for pub/sub or debugging later.

***

# Phase 6: Numeric String Commands

## Requirement

Redis strings can also act as atomic counters through commands such as `INCR`, `DECR`, and related operations. Redis strings are the most basic data type but support counter-like operations. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-doc-...thedocs.io\]](https://redis-doc-test.readthedocs.io/en/latest/topics/data-types/)

## Implement

Commands:

* `INCR key`
* `DECR key`
* `INCRBY key increment`
* `DECRBY key decrement`
* `APPEND key value`
* `STRLEN key`

Rules:

* If key does not exist, numeric commands treat it as `0`.
* If value is not an integer, return an error.
* Store numbers as strings, like Redis does conceptually.

## Expected Outcome

Your Redis clone supports counters.

## What You Achieve

You learn command semantics and type validation.

## Challenge Completion Criteria

```bash
redis-cli INCR counter
redis-cli INCRBY counter 10
redis-cli GET counter
```

works correctly.

## Stretch Goal

Add overflow checks similar to Redis integer behavior.

***

# Phase 7: Lists

## Requirement

Redis lists are ordered sequences of strings, sorted by insertion order. They support fast push/pop operations at both ends, making them useful for queues and timelines. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-doc-...thedocs.io\]](https://redis-doc-test.readthedocs.io/en/latest/topics/data-types/)

## Implement

Internal representation:

```text
collections.deque
```

Commands:

* `LPUSH key element [element ...]`
* `RPUSH key element [element ...]`
* `LPOP key [count]`
* `RPOP key [count]`
* `LLEN key`
* `LRANGE key start stop`
* `LINDEX key index`
* `LTRIM key start stop`

Rules:

* Negative indexes supported.
* Empty list should delete the key.
* Wrong type errors must be returned.

## Expected Outcome

You can use your server as a queue.

## What You Achieve

You implement your first non-string Redis data type.

## Challenge Completion Criteria

```bash
redis-cli RPUSH jobs a b c
redis-cli LPOP jobs
redis-cli LRANGE jobs 0 -1
```

works correctly.

## Stretch Goal

Add blocking list commands:

* `BLPOP`
* `BRPOP`

This requires connection state and waiting clients.

***

# Phase 8: Hashes

## Requirement

Redis hashes are field-value maps stored under a single Redis key, similar to Python dictionaries or Java HashMaps. They are useful for storing objects and records. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-stack.io\]](https://redis-stack.io/docs/data-types/)

## Implement

Internal representation:

```text
dict[field] = value
```

Commands:

* `HSET key field value [field value ...]`
* `HGET key field`
* `HMGET key field [field ...]`
* `HGETALL key`
* `HDEL key field [field ...]`
* `HEXISTS key field`
* `HLEN key`
* `HKEYS key`
* `HVALS key`

## Expected Outcome

You can store object-like structures.

## What You Achieve

You learn nested data structures and multi-field command parsing.

## Challenge Completion Criteria

```bash
redis-cli HSET user:1 name Samad role Analyst
redis-cli HGET user:1 name
redis-cli HGETALL user:1
```

works correctly.

## Stretch Goal

Add:

* `HINCRBY`
* `HSETNX`

***

# Phase 9: Sets

## Requirement

Redis sets are unordered collections of unique strings. They support membership checks, additions, removals, and set algebra. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-stack.io\]](https://redis-stack.io/docs/data-types/)

## Implement

Internal representation:

```text
set()
```

Commands:

* `SADD key member [member ...]`
* `SREM key member [member ...]`
* `SISMEMBER key member`
* `SMEMBERS key`
* `SCARD key`
* `SPOP key [count]`
* `SRANDMEMBER key [count]`
* `SINTER key [key ...]`
* `SUNION key [key ...]`
* `SDIFF key [key ...]`

## Expected Outcome

You support uniqueness and set operations.

## What You Achieve

You implement Redis-style collection semantics.

## Challenge Completion Criteria

```bash
redis-cli SADD tags python redis cache
redis-cli SISMEMBER tags redis
redis-cli SMEMBERS tags
```

works correctly.

## Stretch Goal

Add destination variants:

* `SINTERSTORE`
* `SUNIONSTORE`
* `SDIFFSTORE`

***

# Phase 10: Sorted Sets

## Requirement

Redis sorted sets contain unique strings ordered by associated scores. They are heavily used for leaderboards, rankings, scheduling, and priority queues. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-stack.io\]](https://redis-stack.io/docs/data-types/)

## Implement

Start simple.

Internal representation:

```text
dict[member] = score
```

For range queries, sort on demand first. Later optimize with skip lists or balanced trees.

Commands:

* `ZADD key score member [score member ...]`
* `ZSCORE key member`
* `ZRANK key member`
* `ZREVRANK key member`
* `ZRANGE key start stop [WITHSCORES]`
* `ZREVRANGE key start stop [WITHSCORES]`
* `ZREM key member [member ...]`
* `ZCARD key`
* `ZCOUNT key min max`

## Expected Outcome

You can build leaderboards.

## What You Achieve

You understand score-based ordering.

## Challenge Completion Criteria

```bash
redis-cli ZADD leaderboard 100 alice 200 bob 150 charlie
redis-cli ZRANGE leaderboard 0 -1 WITHSCORES
```

works correctly.

## Stretch Goal

Implement a skip list to avoid sorting every time. Redis internally uses specialized encodings and data structures for performance; your Python version can evolve gradually. [\[letsbuilds...utions.com\]](https://letsbuildsolutions.com/blog/system-design/how-redis-works-internally-single-threaded-event-loop-data-structures-persistence-and-replication/), [\[letsbuilds...utions.com\]](https://letsbuildsolutions.com/blog/system-design/how-redis-works-single-threaded-execution-data-structures-and-persistence-mechanics-from-command-to-disk/)

***

# Phase 11: Streams

## Requirement

Redis streams are append-only log-like data structures. They record events in order and are useful for event processing and message workflows. [\[redis.io\]](https://redis.io/docs/latest/develop/data-types/), [\[redis-stack.io\]](https://redis-stack.io/docs/data-types/)

## Implement

Internal representation:

```text
stream = [
  (ms_time, sequence, {field: value})
]
```

Commands:

* `XADD key id field value [field value ...]`
* `XRANGE key start end [COUNT n]`
* `XREVRANGE key end start [COUNT n]`
* `XLEN key`
* `XREAD [BLOCK ms] STREAMS key [key ...] id [id ...]`

ID rules:

* `*` generates current millisecond timestamp and sequence.
* `1526919030474-0` explicit IDs.
* Validate monotonic IDs.

## Expected Outcome

You can append and read event logs.

## What You Achieve

You implement Redis-like streaming primitives.

## Challenge Completion Criteria

```bash
redis-cli XADD events '*' type login user samad
redis-cli XRANGE events - +
redis-cli XREAD STREAMS events 0-0
```

works correctly.

## Stretch Goal

Add consumer groups:

* `XGROUP`
* `XREADGROUP`
* `XACK`
* Pending entry list.

This is complex; treat it as an advanced challenge.

***

# Phase 12: Pub/Sub

## Requirement

Redis Pub/Sub implements publish/subscribe messaging using commands such as `SUBSCRIBE`, `UNSUBSCRIBE`, and `PUBLISH`. Subscribers receive messages published to channels, and Redis Pub/Sub has at-most-once delivery semantics, meaning lost messages are not retried. [\[redis.io\]](https://redis.io/docs/latest/develop/pubsub/), [\[redis.io\]](https://redis.io/docs/latest/develop/use-cases/pub-sub/)

## Implement

State:

```text
channels = {
  channel: set(client_connections)
}
```

Commands:

* `SUBSCRIBE channel [channel ...]`
* `UNSUBSCRIBE [channel ...]`
* `PUBLISH channel message`
* `PSUBSCRIBE pattern [pattern ...]`
* `PUNSUBSCRIBE [pattern ...]`

Rules:

* In RESP2 subscribed mode, only a restricted command set should be allowed.
* Push messages to subscribed clients.
* Return subscriber count from `PUBLISH`.

## Expected Outcome

You can build a simple chat or notification broadcaster.

## What You Achieve

You learn connection modes and server-pushed responses.

## Challenge Completion Criteria

Terminal 1:

```bash
redis-cli SUBSCRIBE news
```

Terminal 2:

```bash
redis-cli PUBLISH news hello
```

Terminal 1 receives the message.

## Stretch Goal

Add pattern subscriptions using glob matching.

***

# Phase 13: Transactions

## Requirement

Redis transactions are based on `MULTI`, `EXEC`, `DISCARD`, and `WATCH`. Commands in a transaction are queued and then executed sequentially when `EXEC` is called; Redis guarantees that another client’s request is not served in the middle of transaction execution. [\[redis.io\]](https://redis.io/docs/latest/develop/using-commands/transactions/), [\[redis-stack.io\]](https://redis-stack.io/docs/interact/transactions/)

## Implement

Per-client state:

```text
client.in_multi = True/False
client.queue = []
client.watched_keys = set()
```

Commands:

* `MULTI`
* `EXEC`
* `DISCARD`
* `WATCH key [key ...]`
* `UNWATCH`

Rules:

* After `MULTI`, queue commands and return `QUEUED`.
* `EXEC` executes queued commands in order.
* `DISCARD` clears queue.
* `WATCH` implements optimistic locking.
* Track key modification versions.

## Expected Outcome

You support atomic command batches.

## What You Achieve

You learn transaction isolation and optimistic concurrency.

## Challenge Completion Criteria

```bash
redis-cli MULTI
redis-cli SET a 1
redis-cli INCR a
redis-cli EXEC
```

returns an array of command results.

## Stretch Goal

Implement Redis-like error behavior:

* Queue-time errors.
* Execution-time errors.
* WATCH invalidation.

***

# Phase 14: Persistence - AOF

## Requirement

Redis AOF persistence logs every write operation received by the server. On restart, the server replays the log to reconstruct the dataset. AOF commands are logged using the Redis protocol format. [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), [\[redis.io\]](https://redis.io/docs/latest/develop/reference/eviction/)

## Implement

Append Only File:

* Log every mutating command.
* Use RESP format for logged commands.
* Replay AOF at startup.
* Config:
  * `appendonly yes/no`
  * `appendfsync always/everysec/no`

Commands:

* `BGREWRITEAOF` simplified
* `CONFIG GET appendonly`
* `CONFIG SET appendonly`

## Expected Outcome

Data survives restart.

## What You Achieve

You build crash recovery through command replay.

## Challenge Completion Criteria

```bash
redis-cli SET durable yes
kill server
restart server
redis-cli GET durable
```

returns `yes`.

## Stretch Goal

AOF rewrite:

* Create compact temp AOF from current dataset.
* Atomically rename temp file.
* Continue writing new commands during rewrite.

***

# Phase 15: Persistence - RDB Snapshots

## Requirement

Redis RDB persistence creates compact point-in-time snapshots of the dataset. Redis supports RDB, AOF, no persistence, and combinations of RDB plus AOF. RDB is useful for backups and fast restarts, while AOF provides a more complete write history. [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)

## Implement

Simple snapshot format first:

Option 1:

* JSON or MessagePack-like custom format.

Option 2:

* Python `pickle` for learning only.

Commands:

* `SAVE`
* `BGSAVE`
* `LASTSAVE`

Features:

* Write snapshot to temp file.
* Atomic rename.
* Load snapshot at startup.
* Include:
  * keys
  * types
  * values
  * expiry timestamps

## Expected Outcome

Your database can be snapshotted and restored.

## What You Achieve

You learn point-in-time persistence.

## Challenge Completion Criteria

```bash
redis-cli SET snapshot works
redis-cli SAVE
restart server
redis-cli GET snapshot
```

returns `works`.

## Stretch Goal

Implement partial compatibility with Redis RDB file format later. Treat that as advanced because real RDB parsing is binary and versioned.

***

# Phase 16: Memory Limit and Eviction

## Requirement

Redis allows configuring `maxmemory` and eviction policies. When memory usage exceeds the limit, Redis evicts keys according to policies such as `noeviction`, `allkeys-lru`, `allkeys-lfu`, `volatile-lru`, `volatile-ttl`, and random variants. [\[redis.io\]](https://redis.io/docs/latest/develop/reference/eviction/), [\[redis-stack.io\]](https://redis-stack.io/docs/reference/eviction/)

## Implement

Track approximate memory usage:

* Key size.
* Value size.
* Metadata size approximation.

Policies:

* `noeviction`
* `allkeys-random`
* `volatile-random`
* `volatile-ttl`
* `allkeys-lru`
* `volatile-lru`
* Optional:
  * `allkeys-lfu`
  * `volatile-lfu`

Metadata:

```text
last_access_time
access_count
```

Commands:

* `CONFIG SET maxmemory`
* `CONFIG SET maxmemory-policy`
* `INFO memory`

## Expected Outcome

Your Redis clone behaves like a bounded cache.

## What You Achieve

You understand cache memory pressure management.

## Challenge Completion Criteria

* Setting low maxmemory triggers eviction.
* `noeviction` rejects writes when memory is full.
* TTL-only policies only evict expiring keys.

## Stretch Goal

Use sampling-based LRU/LFU instead of exact tracking, since Redis uses approximations for performance. [\[redis-stack.io\]](https://redis-stack.io/docs/reference/eviction/), [\[redis.io\]](https://redis.io/docs/latest/develop/reference/eviction/)

***

# Phase 17: Non-Blocking Event Loop

## Requirement

Redis is famous for its event-driven architecture. It processes commands sequentially while using non-blocking I/O so slow clients do not block the entire server. [\[letsbuilds...utions.com\]](https://letsbuildsolutions.com/blog/system-design/how-redis-works-internally-single-threaded-event-loop-data-structures-persistence-and-replication/), [\[letsbuilds...utions.com\]](https://letsbuildsolutions.com/blog/system-design/how-redis-works-single-threaded-execution-data-structures-and-persistence-mechanics-from-command-to-disk/)

## Implement

Replace thread-per-client with:

```text
selectors.DefaultSelector
```

Features:

* Non-blocking sockets.
* Per-client input buffer.
* Per-client output buffer.
* Read readiness.
* Write readiness.
* Time events:
  * active expiry
  * cron tasks
  * replication heartbeats later

## Expected Outcome

Your server handles many clients more efficiently.

## What You Achieve

You understand why Redis architecture is simple but fast.

## Challenge Completion Criteria

* 1,000 idle clients do not create 1,000 threads.
* Slow clients do not block fast clients.
* Pipelining works.

## Stretch Goal

Benchmark thread-per-client vs event-loop versions.

***

# Phase 18: Pipelining

## Requirement

Redis clients can send multiple commands without waiting for each response; this is called pipelining. RESP supports this naturally because requests are framed. [\[redis.io\]](https://redis.io/docs/latest/develop/reference/protocol-spec/), [\[github.com\]](https://github.com/redis/redis-specifications/blob/master/protocol/RESP2.md)

## Implement

* Parse multiple complete RESP arrays from one input buffer.
* Execute them in order.
* Append replies to output buffer.
* Flush when socket is writable.

## Expected Outcome

A client can send many commands at once and receive many replies.

## What You Achieve

You improve throughput and protocol correctness.

## Challenge Completion Criteria

Use a script to send:

```text
PING
PING
SET a 1
GET a
```

without waiting between commands.

## Stretch Goal

Add output buffer limits to protect the server from slow clients.

***

# Phase 19: Replication - Basic Master/Replica

## Requirement

Redis replication is leader-follower. A master sends a stream of commands to replicas so they maintain copies of the dataset. When reconnecting, replicas may attempt partial resynchronization; otherwise full resynchronization is required. Redis replication is asynchronous by default. [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [\[redis-doc-...thedocs.io\]](https://redis-doc-test.readthedocs.io/en/latest/topics/replication/)

## Implement

Start simple.

Modes:

```bash
python server.py --port 6379
python server.py --port 6380 --replicaof localhost 6379
```

Commands:

* `INFO replication`
* `REPLCONF`
* `PSYNC` simplified
* `WAIT` simplified

Replication flow:

1. Replica connects to master.
2. Replica sends handshake.
3. Master sends snapshot.
4. Master streams write commands.
5. Replica applies commands.

## Expected Outcome

Writes on master appear on replica.

## What You Achieve

You understand data distribution and async replication.

## Challenge Completion Criteria

```bash
redis-cli -p 6379 SET color red
redis-cli -p 6380 GET color
```

returns `red`.

## Stretch Goal

Implement replication offset and backlog for partial resync. Redis uses `PSYNC` with replication ID and offset to resume replication streams when possible. [\[redis.io\]](https://redis.io/docs/latest/commands/psync/), [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)

***

# Phase 20: Read-Only Replica Behavior

## Requirement

Redis replicas usually receive writes from the master and should not normally accept direct client writes unless configured otherwise. Replication is meant to keep replicas as copies of the master. [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [\[redis-doc-...thedocs.io\]](https://redis-doc-test.readthedocs.io/en/latest/topics/replication/)

## Implement

* Reject write commands on replicas.
* Allow read commands.
* Support:

```text
READONLY
READWRITE
```

at least as placeholders.

## Expected Outcome

Replica behaves like a read replica.

## What You Achieve

You separate command permissions by server role.

## Challenge Completion Criteria

```bash
redis-cli -p 6380 SET x y
```

returns an error if the server is a replica.

## Stretch Goal

Add replica lag metrics.

***

# Phase 21: Lua or Server-Side Scripting Lite

## Requirement

Redis supports server-side programmability, but full Lua compatibility is a large project. For your clone, implement a restricted scripting phase only if you want to explore atomic server-side execution.

## Implement

Safer alternatives:

* `EVAL` placeholder.
* Tiny expression language.
* Or embedded Python disabled by default.

Commands:

* `EVAL script numkeys key [key ...] arg [arg ...]`
* `SCRIPT LOAD`
* `EVALSHA`

## Expected Outcome

You understand why server-side execution is powerful and risky.

## What You Achieve

You explore atomic custom logic.

## Challenge Completion Criteria

A script can read/write keys atomically in your single-threaded event loop.

## Stretch Goal

Do not expose arbitrary Python execution in production mode. Keep it sandboxed or educational only.

***

# Phase 22: Authentication and ACL Basics

## Requirement

Production Redis supports authentication and access control. Your clone should at least support password-based authentication and simple command categories.

## Implement

Commands:

* `AUTH password`
* `ACL SETUSER`
* `ACL USERS`
* `ACL GETUSER`
* `ACL DELUSER`

Simplified model:

```text
users = {
  "default": {
    "password_hash": "...",
    "enabled": True,
    "allowed_commands": {"GET", "SET"}
  }
}
```

Features:

* Password hashing.
* Auth-required mode.
* Per-connection authenticated user.
* Command permission checks.

## Expected Outcome

Clients must authenticate before issuing commands.

## What You Achieve

You add basic security boundaries.

## Challenge Completion Criteria

* Unauthenticated client gets `NOAUTH`.
* Authenticated client can run allowed commands.
* Disallowed commands are rejected.

## Stretch Goal

Add categories:

* `@read`
* `@write`
* `@admin`
* `@pubsub`
* `@transaction`

***

# Phase 23: Observability and Introspection

## Requirement

Redis exposes operational information through commands like `INFO`, and this is essential for debugging and production operation.

## Implement

Commands:

* `INFO`
* `MONITOR` simplified
* `CLIENT LIST`
* `CLIENT KILL`
* `SLOWLOG GET`
* `CONFIG GET`
* `CONFIG SET`

Track metrics:

* connected clients
* commands processed
* memory used
* key count
* expired keys
* evicted keys
* rejected connections
* replication role
* uptime
* ops/sec approximation

## Expected Outcome

You can inspect your server.

## What You Achieve

You move from toy implementation to debuggable system.

## Challenge Completion Criteria

```bash
redis-cli INFO
redis-cli CLIENT LIST
```

return useful data.

## Stretch Goal

Expose Prometheus-style metrics over HTTP.

***

# Phase 24: Clustering - Educational Version

## Requirement

Redis Cluster distributes data across hash slots. Redis Cluster uses 16,384 hash slots, maps keys to slots, and redirects clients using errors like `MOVED` and `ASK` during topology changes or slot migration. [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [\[redis.io\]](https://redis.io/docs/latest/commands/cluster-slots/)

## Implement

Start with static clustering.

Features:

* Hash key to slot.
* Slot ownership table.
* `CLUSTER SLOTS`
* `CLUSTER NODES`
* Redirect using `MOVED`.
* Only support DB 0, like Redis Cluster. Redis Cluster does not support multiple databases. [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [\[redis-doc-...thedocs.io\]](https://redis-doc-test.readthedocs.io/en/latest/topics/cluster-spec/)

Commands:

* `CLUSTER SLOTS`
* `CLUSTER KEYSLOT key`
* `CLUSTER NODES`
* `CLUSTER MEET` simplified

## Expected Outcome

Multiple server instances can split key ownership.

## What You Achieve

You understand sharding and client redirection.

## Challenge Completion Criteria

* Key `a` belongs to node 1.
* Key `b` belongs to node 2.
* Wrong node returns `MOVED`.

## Stretch Goal

Implement basic slot migration with `ASK` redirection. During migration, Redis uses `MOVED` for permanent redirects and `ASK` for temporary redirects. [\[redis.io\]](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/), [\[redis-doc-...thedocs.io\]](https://redis-doc-test.readthedocs.io/en/latest/commands/cluster-setslot/)

***

# Phase 25: Testing Strategy

## Requirement

A Redis clone has many edge cases. Without tests, every new command can break old behavior.

## Implement

Test layers:

### 1. Unit Tests

* RESP parser.
* RESP encoder.
* Command validation.
* Expiry logic.
* Data type operations.

### 2. Integration Tests

Run server in subprocess and test using:

* raw sockets
* `redis-cli`
* optionally `redis-py`

### 3. Compatibility Tests

Compare your server against real Redis for selected commands.

### 4. Fuzz Tests

Randomly generate RESP payloads and make sure server does not crash.

## Expected Outcome

You can safely refactor.

## What You Achieve

You make your clone reliable.

## Challenge Completion Criteria

* CI pipeline runs all tests.
* Every command has happy-path and error-path tests.
* Tests cover wrong type errors.

## Stretch Goal

Create a Redis command compatibility matrix.

***

# Phase 26: Benchmarking

## Requirement

Redis is valued for performance, so your clone should be measured, even if Python cannot match Redis written in C.

## Implement

Benchmarks:

* Single client GET/SET.
* Pipelined GET/SET.
* Concurrent clients.
* Large values.
* Expiry-heavy workload.
* List queue workload.
* Pub/Sub fanout.

Metrics:

* ops/sec
* p50 latency
* p95 latency
* p99 latency
* memory usage
* CPU usage

Tools:

* Python benchmark script.
* `redis-benchmark` if compatible.
* Compare against real Redis.

## Expected Outcome

You know where your implementation is slow.

## What You Achieve

You learn performance engineering.

## Challenge Completion Criteria

Produce a benchmark report:

```text
Command     YourRedis ops/s     RealRedis ops/s     Gap
SET         ...
GET         ...
LPUSH       ...
LRANGE      ...
```

## Stretch Goal

Profile with:

```bash
python -m cProfile
```

and optimize hot paths.

***

# Recommended Milestone Tracks

## Track A: Minimal Redis Clone

If you want a quick working version:

1. TCP server
2. RESP
3. Dispatcher
4. Strings
5. Expiry
6. AOF
7. Basic tests

Outcome: Can handle `PING`, `SET`, `GET`, `DEL`, `EXPIRE`.

***

## Track B: Practical Redis Clone

If you want something impressive:

1. Everything in Track A
2. Lists
3. Hashes
4. Sets
5. Pub/Sub
6. Transactions
7. RDB snapshots
8. Event loop
9. Benchmarks

Outcome: Usable mini Redis.

***

## Track C: Advanced Redis Clone

If you want a serious systems project:

1. Everything in Track B
2. Streams
3. Replication
4. Memory eviction
5. ACL
6. Observability
7. Cluster basics
8. Slot migration
9. Compatibility matrix

Outcome: Portfolio-grade Redis-like database.

***

# Suggested Build Order

If I were building this from scratch, I would follow this exact order:

```text
01. TCP echo server
02. RESP parser/encoder
03. PING/ECHO
04. Command dispatcher
05. SET/GET/DEL/EXISTS
06. Expiry and TTL
07. INCR/DECR counters
08. Lists
09. Hashes
10. Sets
11. Sorted sets
12. AOF persistence
13. RDB snapshots
14. Pub/Sub
15. Transactions
16. Event loop rewrite
17. Pipelining
18. Streams
19. Replication
20. Eviction
21. Auth/ACL
22. Observability
23. Cluster basics
24. Benchmarks
25. Documentation
```

***

# Final Deliverable Checklist

By the end, your project should have:

* Redis-compatible TCP server.
* RESP2 protocol parser and encoder.
* String, list, hash, set, sorted set, and stream support.
* Expiry and TTL.
* AOF persistence.
* Snapshot persistence.
* Pub/Sub.
* Transactions.
* Event-loop networking.
* Pipelining.
* Basic replication.
* Memory eviction.
* Authentication.
* INFO and operational metrics.
* Test suite.
* Benchmark report.
* Clear README with supported commands.
