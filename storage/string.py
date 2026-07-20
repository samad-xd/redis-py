from models import Entry, RedisType
from exceptions import WrongTypeError


class StringStore:
    def __init__(self, db: dict[str, Entry]):
        self.db = db

    def _validate_type(self, entry: Entry):
        if entry.type != RedisType.STRING:
            raise WrongTypeError("value is not a string")

    def get(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        return entry.data

    def set(self, key: str, value: str):
        self.db[key] = Entry(type=RedisType.STRING, data=value)

    def incr(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            self.set(key, str(1))
            return 1
        self._validate_type(entry)
        new_value = int(entry.data) + 1
        entry.data = str(new_value)
        return new_value

    def decr(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            self.set(key, str(-1))
            return -1
        self._validate_type(entry)
        new_value = int(entry.data) - 1
        entry.data = str(new_value)
        return new_value

    def incrby(self, key: str, incr_value: int):
        entry = self.db.get(key)
        if entry is None:
            self.set(key, str(incr_value))
            return incr_value
        self._validate_type(entry)
        new_value = int(entry.data) + incr_value
        entry.data = str(new_value)
        return new_value

    def decrby(self, key: str, decr_value: int):
        entry = self.db.get(key)
        if entry is None:
            self.set(key, str(-decr_value))
            return -decr_value
        self._validate_type(entry)
        new_value = int(entry.data) - decr_value
        entry.data = str(new_value)
        return new_value

    def append(self, key, value):
        entry = self.db.get(key)
        if entry is None:
            self.set(key, value)
            return len(value)
        self._validate_type(entry)
        new_value = entry.data + value
        entry.data = new_value
        return len(new_value)

    def strlen(self, key):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        return len(entry.data)
