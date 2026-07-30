from exceptions import WrongTypeError
from models import Entry, RedisType


class SortedSetStore:
    def __init__(self, db: dict[str, Entry]):
        self.db = db

    def _validate_type(self, entry: Entry):
        if entry.type != RedisType.SORTED_SET:
            raise WrongTypeError("value is not a sorted set")

    def zadd(self, key: str, score_member_pairs: list[tuple]):
        entry = self.db.get(key)
        if entry:
            self._validate_type(entry)
        else:
            entry = Entry(type=RedisType.SORTED_SET, data={})
        hash = entry.data
        added_count = 0
        for score, member in score_member_pairs:
            if member not in hash:
                added_count += 1
            hash[member] = score
        self.db[key] = entry
        return added_count

    def zscore(self, key: str, member: str):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        hash = entry.data
        return hash.get(member)

    def zrank(self, key: str, member: str):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        hash = entry.data
        score = hash.get(member)
        if score is None:
            return None
        rank = 0
        for m, s in hash.items():
            if s < score or (s == score and m < member):
                rank += 1
        return rank

    def zrevrank(self, key: str, member: str):
        entry = self.db.get(key)
        if entry is None:
            return None
        self._validate_type(entry)
        hash = entry.data
        score = hash.get(member)
        if score is None:
            return None
        rank = 0
        for m, s in hash.items():
            if s > score or (s == score and m > member):
                rank += 1
        return rank

    def zrange(self, key: str, start: float, stop: float, with_scores: bool):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        hash = entry.data
        sorted_members = sorted(hash.items(), key=lambda x: (x[1], x[0]))
        n = len(sorted_members)
        if start < 0:
            start = n + start
        if stop < 0:
            stop = n + stop + 1
        stop = min(stop, n)
        if not start < stop:
            return []
        if with_scores:
            return [value for pair in sorted_members[start:stop] for value in pair]
        return [member for member, _ in sorted_members[start:stop]]

    def zrevrange(self, key: str, start: float, stop: float, with_scores: bool):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        hash = entry.data
        sorted_members = sorted(hash.items(), key=lambda x: (x[1], x[0]), reverse=True)
        n = len(sorted_members)
        if start < 0:
            start = n + start
        if stop < 0:
            stop = n + stop + 1
        stop = min(stop, n)
        if not start < stop:
            return []
        if with_scores:
            return [value for pair in sorted_members[start:stop] for value in pair]
        return [member for member, _ in sorted_members[start:stop]]

    def zrem(self, key: str, members: list[str]):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        hash = entry.data
        removed_count = 0
        for member in members:
            if member in hash:
                hash.pop(member)
                removed_count += 1
        if not hash:
            self.db.pop(key)
        return removed_count

    def zcard(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        hash = entry.data
        length = len(hash)
        return length

    def zcount(self, key: str, min: float, max: float):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        hash = entry.data
        count = 0
        for score in hash.values():
            if score >= min and score <= max:
                count += 1
        return count
