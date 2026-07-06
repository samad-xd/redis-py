from collections import deque
from itertools import islice


class ListStore:
    def __init__(self):
        self._store: dict[str, deque] = {}

    def lpush(self, key, items):
        if key not in self._store:
            self._store[key] = deque()
        dq = self._store.get(key)
        for item in items:
            dq.appendleft(item)
        return len(items)

    def rpush(self, key, items):
        if key not in self._store:
            self._store[key] = deque()
        dq = self._store.get(key)
        for item in items:
            dq.append(item)
        return len(items)

    def lpop(self, key):
        dq = self._store.get(key, None)
        if dq is None or not dq:
            return None
        item = dq.popleft()
        if not dq:
            self._store.pop(key)
        return item

    def lpop_with_count(self, key, count):
        dq = self._store.get(key, None)
        if dq is None:
            return None
        items = []
        for _ in range(count):
            if not dq:
                self._store.pop(key)
                break
            item = dq.popleft()
            items.append(item)
        return items

    def rpop(self, key):
        dq = self._store.get(key, None)
        if dq is None or not dq:
            return None
        item = dq.pop()
        if not dq:
            self._store.pop(key)
        return item

    def rpop_with_count(self, key, count):
        dq = self._store.get(key, None)
        if dq is None:
            return None
        items = []
        for _ in range(count):
            if not dq:
                self._store.pop(key)
                break
            item = dq.pop()
            items.append(item)
        return items

    def llen(self, key):
        dq = self._store.get(key, None)
        if dq is None:
            return 0
        return len(dq)

    def lrange(self, key, start, stop):
        dq = self._store.get(key, None)
        if dq is None or not dq:
            return []
        n = len(dq)
        if start < 0:
            start = n + start
        if stop < 0:
            stop = n + stop + 1
        if stop <= start:
            return []
        stop = min(stop, n)
        items = []
        for item in islice(dq, start, stop):
            items.append(item)
        return items

    def lindex(self, key, index):
        dq = self._store.get(key, None)
        if dq is None or not dq:
            return None
        return dq[index]

    def ltrim(self, key, start, stop):
        dq = self._store.get(key, None)
        if dq is None or not dq:
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
        else:
            self._store.pop(key)


list_store = ListStore()
