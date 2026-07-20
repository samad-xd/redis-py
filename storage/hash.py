from models import Entry, RedisType
from exceptions import WrongTypeError


class HashStore:
    def __init__(self, db: dict[str, Entry]):
        self.db = db

    def _validate_type(self, entry: Entry):
        if entry.type != RedisType.HASH:
            raise WrongTypeError("value is not a hash")

    def hset(self, key, fields_values):
        entry = self.db.get(key)
        if entry:
            self._validate_type(entry)
        else:
            entry = Entry(type=RedisType.HASH, data={})
        hash = entry.data
        newly_added_fields_count = 0
        for i in range(0, len(fields_values), 2):
            field = fields_values[i]
            value = fields_values[i + 1]
            if field not in hash:
                newly_added_fields_count += 1
            hash[field] = value
        self.db[key] = entry
        return newly_added_fields_count

    def hget(self, key, field):
        entry = self.db.get(key)
        if not entry:
            return None
        self._validate_type(entry)
        hash = entry.data
        return hash.get(field, None)

    def hmget(self, key, fields):
        values = []
        entry = self.db.get(key)
        if not entry:
            return values
        self._validate_type(entry)
        hash = entry.data
        for field in fields:
            value = hash.get(field, None)
            values.append(value)
        return values

    def hgetall(self, key):
        fields_values = []
        entry = self.db.get(key)
        if not entry:
            return fields_values
        self._validate_type(entry)
        hash = entry.data
        for field, value in hash.items():
            fields_values.append(field)
            fields_values.append(value)
        return fields_values

    def hdel(self, key, fields):
        entry = self.db.get(key)
        if not entry:
            return 0
        self._validate_type(entry)
        hash = entry.data
        deleted_count = 0
        for field in fields:
            if field in hash:
                del hash[field]
                deleted_count += 1
        if len(hash) == 0:
            self.db.pop(key)
        return deleted_count

    def hexists(self, key, field):
        entry = self.db.get(key)
        if not entry:
            return 0
        self._validate_type(entry)
        hash = entry.data
        return 1 if field in hash else 0

    def hlen(self, key):
        entry = self.db.get(key)
        if not entry:
            return 0
        self._validate_type(entry)
        hash = entry.data
        return len(hash)

    def hkeys(self, key):
        entry = self.db.get(key)
        if not entry:
            return []
        self._validate_type(entry)
        hash = entry.data
        return list(hash.keys())

    def hvals(self, key):
        entry = self.db.get(key)
        if not entry:
            return []
        self._validate_type(entry)
        hash = entry.data
        return list(hash.values())
