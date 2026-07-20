import random
from typing import List

from exceptions import WrongTypeError
from models import Entry, RedisType


class SetStore:
    def __init__(self, db: dict[str, Entry]):
        self.db = db

    def _validate_type(self, entry: Entry):
        if entry.type != RedisType.SET:
            raise WrongTypeError("value is not a set")

    def sadd(self, key: str, members: List[str]):
        entry = self.db.get(key)
        if entry:
            self._validate_type(entry)
        else:
            entry = Entry(type=RedisType.SET, data=set())
        s: set = entry.data
        added_count = 0
        for member in members:
            if member not in s:
                s.add(member)
                added_count += 1
        self.db[key] = entry
        return added_count

    def srem(self, key: str, members: List[str]):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        s: set = entry.data
        removed_count = 0
        for member in members:
            if member in s:
                s.remove(member)
                removed_count += 1
        if not s:
            self.db.pop(key)
        return removed_count

    def sismember(self, key: str, member: str):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        s: set = entry.data
        if member in s:
            return 1
        return 0

    def smembers(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        s: set = entry.data
        return list(s)

    def scard(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        s: set = entry.data
        return len(s)

    def spop(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        s: set = entry.data
        popped_member = s.pop()
        if not s:
            self.db.pop(key)
        return popped_member

    def spop_with_count(self, key: str, count: int):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        s: set = entry.data
        popped_members = [s.pop() for _ in range(min(len(s), count))]
        if not s:
            self.db.pop(key)
        return popped_members

    def srandmember(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        s: set = entry.data
        return random.choice(list(s))

    def srandmember_with_count(self, key: str, count: int):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        s: set = entry.data
        if count == 0:
            return []
        if count > 0:
            return random.sample(list(s), k=min(len(s), count))
        return random.choices(list(s), k=abs(count))

    def sinter(self, keys: List[str]):
        min_len = float("inf")
        smallest_set = None
        sets = []
        for key in keys:
            entry = self.db.get(key)
            if entry is None:
                return []
            self._validate_type(entry)
            s: set = entry.data
            length = len(s)
            if length < min_len:
                min_len = length
                smallest_set = s
            else:
                sets.append(s)
        inter_members = smallest_set.intersection(*sets)
        return list(inter_members)

    def sunion(self, keys: List[str]):
        sets = []
        for key in keys:
            entry = self.db.get(key)
            if entry is None:
                continue
            self._validate_type(entry)
            s: set = entry.data
            sets.append(s)
        union_members = set().union(*sets)
        return list(union_members)

    def sdiff(self, key: str, keys: List[str]):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        base_set: set = entry.data
        sets = []
        for key in keys:
            entry = self.db.get(key)
            if entry is None:
                continue
            self._validate_type(entry)
            s: set = entry.data
            sets.append(s)
        diff_members = base_set.difference(*sets)
        return list(diff_members)
