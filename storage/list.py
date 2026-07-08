import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import islice


@dataclass
class Waiter:
    future: asyncio.Future
    keys: list[str]
    active: bool = True


class ListStore:
    def __init__(self):
        self._store: dict[str, deque] = defaultdict(deque)
        self._waiters: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def lpush(self, key, items):
        async with self._lock:
            for item in items:
                active_waiter = self._pop_active_waiter(key)
                if active_waiter:
                    self._finish_waiter(active_waiter, [key, item])
                else:
                    self._store[key].appendleft(item)
            return len(self._store[key])

    async def rpush(self, key, items):
        async with self._lock:
            for item in items:
                active_waiter = self._pop_active_waiter(key)
                if active_waiter:
                    self._finish_waiter(active_waiter, [key, item])
                else:
                    self._store[key].append(item)
            return len(self._store[key])

    def lpop(self, key):
        dq = self._store.get(key)
        if not dq:
            return None
        item = dq.popleft()
        return item

    def lpop_with_count(self, key, count):
        dq = self._store.get(key)
        if not dq:
            return None
        items = []
        for _ in range(count):
            if not dq:
                break
            item = dq.popleft()
            items.append(item)
        return items

    def rpop(self, key):
        dq = self._store.get(key)
        if not dq:
            return None
        item = dq.pop()
        return item

    def rpop_with_count(self, key, count):
        dq = self._store.get(key)
        if not dq:
            return None
        items = []
        for _ in range(count):
            if not dq:
                break
            item = dq.pop()
            items.append(item)
        return items

    def llen(self, key):
        dq = self._store.get(key)
        return len(dq)

    def lrange(self, key, start, stop):
        dq = self._store.get(key)
        if not dq:
            return []
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
        dq = self._store.get(key)
        if not dq:
            return None
        return dq[index]

    def ltrim(self, key, start, stop):
        dq = self._store.get(key)
        if not dq:
            return
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
                dq = self._store.get(key)
                if dq:
                    item = dq.popleft()
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

    async def brpop(self, keys, timeout):
        async with self._lock:
            for key in keys:
                dq = self._store.get(key)
                if dq:
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


list_store = ListStore()
