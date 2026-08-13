import asyncio
import time
from collections import defaultdict, deque

from models import Entry, Waiter


class Database:
    def __init__(self):
        self.db: dict[str, Entry] = {}
        self.waiters: dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()

    def clear_db(self):
        self.db.clear()

    def db_size(self):
        return len(self.db)

    def ensure_key_life(self, key: str):
        if key in self.db:
            expire = self.db.get(key).expire
            if expire != 0 and time.time() >= expire:
                self.db.pop(key)

    def get(self, key: str):
        self.ensure_key_life(key)
        entry = self.db.get(key)
        return entry

    def set(self, key: str, entry: Entry):
        self.db[key] = entry

    def type(self, key):
        self.ensure_key_life(key)
        if key not in self.db:
            return None
        return self.db.get(key).type.value

    def exists(self, key: str):
        self.ensure_key_life(key)
        return key in self.db

    def delete(self, key):
        self.ensure_key_life(key)
        return self.db.pop(key, None)

    def expire(self, key: str, seconds: float):
        self.ensure_key_life(key)
        item = self.db.get(key, None)
        if item is None:
            return 0
        item.expire = time.time() + seconds
        return 1

    def ttl(self, key):
        self.ensure_key_life(key)
        item = self.db.get(key, None)
        if item is None:
            return -2
        expire = item.expire
        if expire == 0:
            return -1
        return expire - time.time()

    def persist(self, key):
        self.ensure_key_life(key)
        item = self.db.get(key, None)
        if item is None:
            return 0
        expire = item.expire
        if expire == 0:
            return 0
        item.expire = 0
        return 1

    def pop_active_waiter(self, key: str):
        waiters_q = self.waiters.get(key)
        while waiters_q:
            waiter = waiters_q.popleft()
            if waiter.active and not waiter.future.done():
                return waiter
        return None

    def deactivate_waiter(self, waiter: Waiter):
        waiter.active = False
        waiter.future.cancel()

    def finish_waiter(self, waiter: Waiter, pair: list[str]):
        waiter.active = False
        waiter.future.set_result(pair)
