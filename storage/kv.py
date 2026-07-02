class KVStore:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def delete(self, key):
        return self._store.pop(key, None)

    def exists(self, key):
        return key in self._store

    def size(self):
        return len(self._store)

    def clear_db(self):
        self._store.clear()


kv_store = KVStore()
