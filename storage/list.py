import asyncio
from collections import deque
from itertools import islice

from exceptions import WrongTypeError
from models import Entry, RedisType, Waiter

from .database import Database


class ListStore:
    @staticmethod
    def _validate_type(entry: Entry):
        if entry.type != RedisType.LIST:
            raise WrongTypeError(
                "Operation against a key holding the wrong kind of value"
            )

    @staticmethod
    async def lpush(db: Database, key, items):
        entry = db.get(key)
        if entry:
            ListStore._validate_type(entry)
        else:
            entry = Entry(type=RedisType.LIST, data=deque())
        dq = entry.data
        async with db.lock:
            for item in items:
                active_waiter = db.pop_active_waiter(key)
                if active_waiter:
                    db.finish_waiter(active_waiter, [key, item])
                else:
                    dq.appendleft(item)
            if dq:
                db.set(key, entry)
            return len(dq)

    @staticmethod
    async def rpush(db: Database, key, items):
        entry = db.get(key)
        if entry is None:
            entry = Entry(type=RedisType.LIST, data=deque())
        else:
            ListStore._validate_type(entry)
        dq = entry.data
        async with db.lock:
            for item in items:
                active_waiter = db.pop_active_waiter(key)
                if active_waiter:
                    db.finish_waiter(active_waiter, [key, item])
                else:
                    dq.append(item)
            if dq:
                db.set(key, entry)
            return len(dq)

    @staticmethod
    def lpop(db: Database, key):
        entry = db.get(key)
        if entry is None:
            return None
        ListStore._validate_type(entry)
        dq = entry.data
        item = dq.popleft()
        if not dq:
            db.delete(key)
        return item

    @staticmethod
    def lpop_with_count(db: Database, key, count):
        entry = db.get(key)
        if entry is None:
            return None
        ListStore._validate_type(entry)
        dq = entry.data
        items = []
        for _ in range(count):
            if not dq:
                db.delete(key)
                break
            item = dq.popleft()
            items.append(item)
        return items

    @staticmethod
    def rpop(db: Database, key):
        entry = db.get(key)
        if entry is None:
            return None
        ListStore._validate_type(entry)
        dq = entry.data
        item = dq.pop()
        if not dq:
            db.delete(key)
        return item

    @staticmethod
    def rpop_with_count(db: Database, key, count):
        entry = db.get(key)
        if entry is None:
            return None
        ListStore._validate_type(entry)
        dq = entry.data
        items = []
        for _ in range(count):
            if not dq:
                db.delete(key)
                break
            item = dq.pop()
            items.append(item)
        return items

    @staticmethod
    def llen(db: Database, key):
        entry = db.get(key)
        if entry is None:
            return 0
        ListStore._validate_type(entry)
        dq = entry.data
        return len(dq)

    @staticmethod
    def lrange(db: Database, key, start, stop):
        entry = db.get(key)
        if entry is None:
            return []
        ListStore._validate_type(entry)
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

    @staticmethod
    def lindex(db: Database, key, index):
        entry = db.get(key)
        if entry is None:
            return None
        ListStore._validate_type(entry)
        dq = entry.data
        try:
            return dq[index]
        except IndexError:
            return None

    @staticmethod
    def ltrim(db: Database, key, start, stop):
        entry = db.get(key)
        if entry is None:
            return
        ListStore._validate_type(entry)
        dq = entry.data
        n = len(dq)
        if start < 0:
            start = n + start
        if stop < 0:
            stop = n + stop
        if start <= stop:
            for _ in range(n - 1, stop, -1):
                dq.pop()
            for _ in range(start):
                dq.popleft()

    @staticmethod
    async def blpop(db: Database, keys, timeout):
        async with db.lock:
            for key in keys:
                entry = db.get(key)
                if entry:
                    ListStore._validate_type(entry)
                    dq = entry.data
                    item = dq.popleft()
                    if not dq:
                        db.delete(key)
                    return [key, item]
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            waiter = Waiter(future, keys)
            for key in keys:
                db.waiters[key].append(waiter)
        try:
            if timeout == 0:
                result = await future
            else:
                result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            async with db.lock:
                db.deactivate_waiter(waiter)
            return None
        except asyncio.CancelledError:
            async with db.lock:
                db.deactivate_waiter(waiter)
            raise

    @staticmethod
    async def brpop(db: Database, keys, timeout):
        async with db.lock:
            for key in keys:
                entry = db.get(key)
                if entry:
                    ListStore._validate_type(entry)
                    dq = entry.data
                    item = dq.pop()
                    if not dq:
                        db.delete(key)
                    return [key, item]
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            waiter = Waiter(future, keys)
            for key in keys:
                db.waiters[key].append(waiter)
        try:
            if timeout == 0:
                return await future
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            async with db.lock:
                db.deactivate_waiter(waiter)
            return None
        except asyncio.CancelledError:
            async with db.lock:
                db.deactivate_waiter(waiter)
            raise
