from exceptions import WrongTypeError
from models import Entry, RedisType

from .database import Database


class HashStore:
    @staticmethod
    def _validate_type(entry: Entry):
        if entry.type != RedisType.HASH:
            raise WrongTypeError(
                "Operation against a key holding the wrong kind of value"
            )

    @staticmethod
    def hset(db: Database, key, fields_values):
        entry = db.get(key)
        if entry:
            HashStore._validate_type(entry)
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
        db.set(key, entry)
        return newly_added_fields_count

    @staticmethod
    def hget(db: Database, key, field):
        entry = db.get(key)
        if not entry:
            return None
        HashStore._validate_type(entry)
        hash = entry.data
        return hash.get(field, None)

    @staticmethod
    def hmget(db: Database, key, fields):
        values = []
        entry = db.get(key)
        if not entry:
            return values
        HashStore._validate_type(entry)
        hash = entry.data
        for field in fields:
            value = hash.get(field, None)
            values.append(value)
        return values

    @staticmethod
    def hgetall(db: Database, key):
        fields_values = []
        entry = db.get(key)
        if not entry:
            return fields_values
        HashStore._validate_type(entry)
        hash = entry.data
        for field, value in hash.items():
            fields_values.append(field)
            fields_values.append(value)
        return fields_values

    @staticmethod
    def hdel(db: Database, key, fields):
        entry = db.get(key)
        if not entry:
            return 0
        HashStore._validate_type(entry)
        hash = entry.data
        deleted_count = 0
        for field in fields:
            if field in hash:
                del hash[field]
                deleted_count += 1
        if len(hash) == 0:
            db.pop(key)
        return deleted_count

    @staticmethod
    def hexists(db: Database, key, field):
        entry = db.get(key)
        if not entry:
            return 0
        HashStore._validate_type(entry)
        hash = entry.data
        return 1 if field in hash else 0

    @staticmethod
    def hlen(db: Database, key):
        entry = db.get(key)
        if not entry:
            return 0
        HashStore._validate_type(entry)
        hash = entry.data
        return len(hash)

    @staticmethod
    def hkeys(db: Database, key):
        entry = db.get(key)
        if not entry:
            return []
        HashStore._validate_type(entry)
        hash = entry.data
        return list(hash.keys())

    @staticmethod
    def hvals(db: Database, key):
        entry = db.get(key)
        if not entry:
            return []
        HashStore._validate_type(entry)
        hash = entry.data
        return list(hash.values())
