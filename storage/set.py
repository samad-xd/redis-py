import random

from exceptions import WrongTypeError
from models import Entry, RedisType

from .database import Database


class SetStore:
    @staticmethod
    def _validate_type(entry: Entry):
        if entry.type != RedisType.SET:
            raise WrongTypeError(
                "Operation against a key holding the wrong kind of value"
            )

    @staticmethod
    def sadd(db: Database, key: str, members: list[str]):
        entry = db.get(key)
        if entry:
            SetStore._validate_type(entry)
        else:
            entry = Entry(type=RedisType.SET, data=set())
        s: set = entry.data
        added_count = 0
        for member in members:
            if member not in s:
                s.add(member)
                added_count += 1
        db.set(key, entry)
        return added_count

    @staticmethod
    def srem(db: Database, key: str, members: list[str]):
        entry = db.get(key)
        if entry is None:
            return 0
        SetStore._validate_type(entry)
        s: set = entry.data
        removed_count = 0
        for member in members:
            if member in s:
                s.remove(member)
                removed_count += 1
        if not s:
            db.delete(key)
        return removed_count

    @staticmethod
    def sismember(db: Database, key: str, member: str):
        entry = db.get(key)
        if entry is None:
            return 0
        SetStore._validate_type(entry)
        s: set = entry.data
        if member in s:
            return 1
        return 0

    @staticmethod
    def smembers(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            return []
        SetStore._validate_type(entry)
        s: set = entry.data
        return list(s)

    @staticmethod
    def scard(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            return 0
        SetStore._validate_type(entry)
        s: set = entry.data
        return len(s)

    @staticmethod
    def spop(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            return None
        SetStore._validate_type(entry)
        s: set = entry.data
        popped_member = s.pop()
        if not s:
            db.delete(key)
        return popped_member

    @staticmethod
    def spop_with_count(db: Database, key: str, count: int):
        entry = db.get(key)
        if entry is None:
            return []
        SetStore._validate_type(entry)
        s: set = entry.data
        popped_members = [s.pop() for _ in range(min(len(s), count))]
        if not s:
            db.delete(key)
        return popped_members

    @staticmethod
    def srandmember(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            return None
        SetStore._validate_type(entry)
        s: set = entry.data
        return random.choice(list(s))

    @staticmethod
    def srandmember_with_count(db: Database, key: str, count: int):
        entry = db.get(key)
        if entry is None:
            return []
        SetStore._validate_type(entry)
        s: set = entry.data
        if count == 0:
            return []
        if count > 0:
            return random.sample(list(s), k=min(len(s), count))
        return random.choices(list(s), k=abs(count))

    @staticmethod
    def sinter(db: Database, keys: list[str]):
        min_len = float("inf")
        smallest_set = None
        sets = []
        for key in keys:
            entry = db.get(key)
            if entry is None:
                return []
            SetStore._validate_type(entry)
            s: set = entry.data
            length = len(s)
            if length < min_len:
                min_len = length
                smallest_set = s
            else:
                sets.append(s)
        inter_members = smallest_set.intersection(*sets)
        return list(inter_members)

    @staticmethod
    def sunion(db: Database, keys: list[str]):
        sets = []
        for key in keys:
            entry = db.get(key)
            if entry is None:
                continue
            SetStore._validate_type(entry)
            s: set = entry.data
            sets.append(s)
        union_members = set().union(*sets)
        return list(union_members)

    @staticmethod
    def sdiff(db: Database, key: str, keys: list[str]):
        entry = db.get(key)
        if entry is None:
            return []
        SetStore._validate_type(entry)
        base_set: set = entry.data
        sets = []
        for k in keys:
            entry = db.get(k)
            if entry is None:
                continue
            SetStore._validate_type(entry)
            s: set = entry.data
            sets.append(s)
        diff_members = base_set.difference(*sets)
        return list(diff_members)
