import time


class Value:
    value: str
    deadline: float

    def __init__(self, value, deadline=None):
        self.value = value
        self.deadline = deadline


class KVStore:
    def __init__(self):
        self._store: dict[str, Value] = {}

    def get(self, key):
        item = self._store.get(key, None)
        if item is None:
            return None
        deadline = item.deadline
        if deadline is not None:
            if time.time() >= deadline:
                self._store.pop(key)
                return None
        return item.value

    def set(self, key, value):
        self._store[key] = Value(value)

    def delete(self, key):
        item = self._store.pop(key, None)
        return item.value if item is not None else None

    def exists(self, key):
        item = self._store.get(key, None)
        if item is None:
            return False
        deadline = item.deadline
        if deadline is not None:
            if time.time() >= deadline:
                self._store.pop(key)
                return False
        return True

    def size(self):
        return len(self._store)

    def clear_db(self):
        self._store.clear()

    def expire(self, key, seconds):
        item = self._store.get(key, None)
        if item is None:
            return 0
        deadline = item.deadline
        if deadline is not None:
            if time.time() >= deadline:
                self._store.pop(key)
                return 0
        item.deadline = time.time() + seconds
        return 1

    def ttl(self, key):
        item = self._store.get(key, None)
        if item is None:
            return -2
        deadline = item.deadline
        if deadline is None:
            return -1
        if time.time() >= deadline:
            self._store.pop(key)
            return -2
        return deadline - time.time()

    def persist(self, key):
        item = self._store.get(key, None)
        if item is None:
            return 0
        deadline = item.deadline
        if deadline is None:
            return 0
        if time.time() >= deadline:
            self._store.pop(key)
            return 0
        item.deadline = None
        return 1


kv_store = KVStore()
