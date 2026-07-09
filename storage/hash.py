from collections import defaultdict


class HashStore:
    def __init__(self):
        self._store: dict[str, dict] = defaultdict(dict)

    def hset(self, key, fields_values):
        hash = self._store[key]
        newly_added_fields_count = 0
        for i in range(0, len(fields_values), 2):
            field = fields_values[i]
            value = fields_values[i + 1]
            if field not in hash:
                newly_added_fields_count += 1
            hash[field] = value
        return newly_added_fields_count

    def hget(self, key, field):
        if key in self._store:
            hash = self._store.get(key)
            if field in hash:
                return hash.get(field)
        return None

    def hmget(self, key, fields):
        if key not in self._store:
            return [None] * len(fields)
        values = []
        hash = self._store.get(key)
        for field in fields:
            values.append(hash.get(field))
        return values

    def hgetall(self, key):
        if key not in self._store:
            return []
        fields_values = []
        hash = self._store.get(key)
        for field, value in hash.items():
            fields_values.append(field)
            fields_values.append(value)
        return fields_values

    def hdel(self, key, fields):
        if key not in self._store:
            return 0
        hash = self._store.get(key)
        deleted_count = 0
        for field in fields:
            if field in hash:
                del hash[field]
                deleted_count += 1
        return deleted_count

    def hexists(self, key, field):
        if key not in self._store:
            return 0
        hash = self._store.get(key)
        if field not in hash:
            return 0
        return 1

    def hlen(self, key):
        if key not in self._store:
            return 0
        hash = self._store.get(key)
        return len(hash)

    def hkeys(self, key):
        if key not in self._store:
            return []
        hash = self._store.get(key)
        fields = []
        for field in hash.keys():
            fields.append(field)
        return fields

    def hvals(self, key):
        if key not in self._store:
            return []
        hash = self._store.get(key)
        values = []
        for value in hash.values():
            values.append(value)
        return values


hash_store = HashStore()