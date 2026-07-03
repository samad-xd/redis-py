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

    def _ensure_life(self, key):
        if key in self._store:
            deadline = self._store.get(key).deadline
            if deadline is not None and time.time() >= deadline:
                self._store.pop(key)

    def get(self, key):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            return None
        return item.value

    def set(self, key, value):
        self._store[key] = Value(value)

    def delete(self, key):
        item = self._store.pop(key, None)
        return item.value if item is not None else None

    def exists(self, key):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            return False
        return True

    def size(self):
        return len(self._store)

    def clear_db(self):
        self._store.clear()

    def expire(self, key, seconds):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            return 0
        item.deadline = time.time() + seconds
        return 1

    def ttl(self, key):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            return -2
        deadline = item.deadline
        if deadline is None:
            return -1
        return deadline - time.time()

    def persist(self, key):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            return 0
        deadline = item.deadline
        if deadline is None:
            return 0
        item.deadline = None
        return 1

    def incr(self, key):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            self.set(key, str(1))
            return 1
        new_value = int(item.value) + 1
        item.value = str(new_value)
        return new_value

    def decr(self, key):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            self.set(key, str(-1))
            return -1
        new_value = int(item.value) - 1
        item.value = str(new_value)
        return new_value

    def incrby(self, key, incr_value):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            self.set(key, str(incr_value))
            return incr_value
        new_value = int(item.value) + incr_value
        item.value = str(new_value)
        return new_value

    def decrby(self, key, decr_value):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            self.set(key, str(-decr_value))
            return -decr_value
        new_value = int(item.value) - decr_value
        item.value = str(new_value)
        return new_value

    def append(self, key, value):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            self.set(key, value)
            return len(value)
        new_value = item.value + value
        item.value = new_value
        return len(new_value)

    def strlen(self, key):
        self._ensure_life(key)
        item = self._store.get(key, None)
        if item is None:
            return 0
        return len(item.value)


kv_store = KVStore()
