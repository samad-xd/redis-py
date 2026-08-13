from exceptions import WrongTypeError
from models import Entry, RedisType

from .database import Database


class StringStore:
    @staticmethod
    def _validate_type(entry: Entry):
        if entry.type != RedisType.STRING:
            raise WrongTypeError(
                "Operation against a key holding the wrong kind of value"
            )

    @staticmethod
    def get(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            return None
        StringStore._validate_type(entry)
        return entry.data

    @staticmethod
    def set(db: Database, key: str, value: str):
        entry = Entry(type=RedisType.STRING, data=value)
        db.set(key, entry)

    @staticmethod
    def incr(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            StringStore.set(key, str(1))
            return 1
        StringStore._validate_type(entry)
        new_value = int(entry.data) + 1
        entry.data = str(new_value)
        return new_value

    @staticmethod
    def decr(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            StringStore.set(key, str(-1))
            return -1
        StringStore._validate_type(entry)
        new_value = int(entry.data) - 1
        entry.data = str(new_value)
        return new_value

    @staticmethod
    def incrby(db: Database, key: str, incr_value: int):
        entry = db.get(key)
        if entry is None:
            StringStore.set(key, str(incr_value))
            return incr_value
        StringStore._validate_type(entry)
        new_value = int(entry.data) + incr_value
        entry.data = str(new_value)
        return new_value

    @staticmethod
    def decrby(db: Database, key: str, decr_value: int):
        entry = db.get(key)
        if entry is None:
            StringStore.set(key, str(-decr_value))
            return -decr_value
        StringStore._validate_type(entry)
        new_value = int(entry.data) - decr_value
        entry.data = str(new_value)
        return new_value

    @staticmethod
    def append(db: Database, key, value):
        entry = db.get(key)
        if entry is None:
            StringStore.set(key, value)
            return len(value)
        StringStore._validate_type(entry)
        new_value = entry.data + value
        entry.data = new_value
        return len(new_value)

    @staticmethod
    def strlen(db: Database, key):
        entry = db.get(key)
        if entry is None:
            return 0
        StringStore._validate_type(entry)
        return len(entry.data)
