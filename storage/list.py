import asyncio
from collections import deque, defaultdict
from dataclasses import dataclass
from itertools import islice
from models import Entry, RedisType
from exceptions import WrongTypeError


@dataclass
class Waiter:
    future: asyncio.Future
    keys: list[str]
    active: bool = True


class ListStore:
    def __init__(self, db: dict[str, Entry]):
        self._waiters: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
        self.db = db

    def _validate_type(self, entry: Entry):
        if entry.type != RedisType.LIST:
            raise WrongTypeError("value is not a list")

    async def lpush(self, key, items):
        entry = self.db.get(key)
        if entry:
            self._validate_type(entry)
        else:
            entry = Entry(type=RedisType.LIST, data=deque())
        dq = entry.data
        async with self._lock:
            for item in items:
                active_waiter = self._pop_active_waiter(key)
                if active_waiter:
                    self._finish_waiter(active_waiter, [key, item])
                else:
                    dq.appendleft(item)
            if dq:
                self.db[key] = entry
            return len(dq)

    async def rpush(self, key, items):
        entry = self.db.get(key)
        if entry is None:
            entry = Entry(type=RedisType.LIST, data=deque())
        else:
            self._validate_type(entry)
        dq = entry.data
        async with self._lock:
            for item in items:
                active_waiter = self._pop_active_waiter(key)
                if active_waiter:
                    self._finish_waiter(active_waiter, [key, item])
                else:
                    dq.append(item)
            if dq:
                self.db[key] = entry
            return len(dq)

    def lpop(self, key):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        dq = entry.data
        return dq.popleft()

    def lpop_with_count(self, key, count):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        dq = entry.data
        items = []
        for _ in range(count):
            if not dq:
                self.db.pop(key)
                break
            item = dq.popleft()
            items.append(item)
        return items
    
    def rpop(self, key):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        dq = entry.data
        return dq.pop()

    def rpop_with_count(self, key, count):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        dq = entry.data
        items = []
        for _ in range(count):
            if not dq:
                self.db.pop(key)
                break
            item = dq.pop()
            items.append(item)
        return items

    def llen(self, key):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        dq = entry.data
        return len(dq)

    def lrange(self, key, start, stop):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        dq = entry.data
        n = len(dq)
        if start < 0:
            start = n + start
        if stop < 0:
            stop = n + stop + 1
        if stop <= start:
            return []
        items = [item for item in islice(dq, start, min(stop, n))]
        return items

    def lindex(self, key, index):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        dq = entry.data
        return dq[index]

    def ltrim(self, key, start, stop):
        entry = self.db.get(key)
        if entry is None:
            return
        self._validate_type(entry)
        dq = entry.data
        n = len(dq)
        if start < 0:
            start = n + start
        if stop < 0:
            stop = n + stop
        if start <= stop:
            for _ in range(n - 1, stop, -1):
                dq.pop()
            for _ in range(0, start):
                dq.popleft()

    async def blpop(self, keys, timeout):
        async with self._lock:
            for key in keys:
                entry = self.db.get(key)
                if entry:
                    self._validate_type(entry)
                    dq = entry.data
                    item = dq.popleft()
                    return [key, item]
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            waiter = Waiter(future, keys)
            for key in keys:
                self._waiters[key].append(waiter)
        try:
            if timeout == 0:
                result = await future
            else:
                result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            async with self._lock:
                self._deactivate_waiter(waiter)
            return None
        except asyncio.CancelledError:
            async with self._lock:
                self._deactivate_waiter(waiter)
            raise

    async def brpop(self, keys, timeout):
        async with self._lock:
            for key in keys:
                entry = self.db.get(key)
                if entry:
                    self._validate_type(entry)
                    dq = entry.data
                    item = dq.pop()
                    return [key, item]
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            waiter = Waiter(future, keys)
            for key in keys:
                self._waiters[key].append(waiter)
        try:
            if timeout == 0:
                return await future
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            async with self._lock:
                self._deactivate_waiter(waiter)
            return None
        except asyncio.CancelledError:
            async with self._lock:
                self._deactivate_waiter(waiter)
            raise

    def _pop_active_waiter(self, key):
        waiters_q = self._waiters.get(key)
        while waiters_q:
            waiter = waiters_q.popleft()
            if waiter.active and not waiter.future.done():
                return waiter
        return None

    def _deactivate_waiter(self, waiter: Waiter):
        waiter.active = False
        waiter.future.cancel()

    def _finish_waiter(self, waiter: Waiter, pair):
        waiter.active = False
        waiter.future.set_result(pair)
