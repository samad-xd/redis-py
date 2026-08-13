from exceptions import WrongTypeError
from models import Entry, RedisType

from .database import Database


class SortedSetStore:
    @staticmethod
    def _validate_type(entry: Entry):
        if entry.type != RedisType.SORTED_SET:
            raise WrongTypeError(
                "Operation against a key holding the wrong kind of value"
            )

    @staticmethod
    def zadd(db: Database, key: str, score_member_pairs: list[tuple]):
        entry = db.get(key)
        if entry:
            SortedSetStore._validate_type(entry)
        else:
            entry = Entry(type=RedisType.SORTED_SET, data={})
        hash = entry.data
        added_count = 0
        for score, member in score_member_pairs:
            if member not in hash:
                added_count += 1
            hash[member] = score
        db.set(key, entry)
        return added_count

    @staticmethod
    def zscore(db: Database, key: str, member: str):
        entry = db.get(key)
        if entry is None:
            return None
        SortedSetStore._validate_type(entry)
        hash = entry.data
        return hash.get(member)

    @staticmethod
    def zrank(db: Database, key: str, member: str):
        entry = db.get(key)
        if entry is None:
            return None
        SortedSetStore._validate_type(entry)
        hash = entry.data
        score = hash.get(member)
        if score is None:
            return None
        rank = 0
        for m, s in hash.items():
            if s < score or (s == score and m < member):
                rank += 1
        return rank

    @staticmethod
    def zrevrank(db: Database, key: str, member: str):
        entry = db.get(key)
        if entry is None:
            return None
        SortedSetStore._validate_type(entry)
        hash = entry.data
        score = hash.get(member)
        if score is None:
            return None
        rank = 0
        for m, s in hash.items():
            if s > score or (s == score and m > member):
                rank += 1
        return rank

    @staticmethod
    def zrange(db: Database, key: str, start: float, stop: float, with_scores: bool):
        entry = db.get(key)
        if entry is None:
            return []
        SortedSetStore._validate_type(entry)
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

    @staticmethod
    def zrevrange(db: Database, key: str, start: float, stop: float, with_scores: bool):
        entry = db.get(key)
        if entry is None:
            return []
        SortedSetStore._validate_type(entry)
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

    @staticmethod
    def zrem(db: Database, key: str, members: list[str]):
        entry = db.get(key)
        if entry is None:
            return 0
        SortedSetStore._validate_type(entry)
        hash = entry.data
        removed_count = 0
        for member in members:
            if member in hash:
                hash.pop(member)
                removed_count += 1
        if not hash:
            db.delete(key)
        return removed_count

    @staticmethod
    def zcard(db: Database, key: str):
        entry = db.get(key)
        if entry is None:
            return 0
        SortedSetStore._validate_type(entry)
        hash = entry.data
        length = len(hash)
        return length

    @staticmethod
    def zcount(db: Database, key: str, min: float, max: float):
        entry = db.get(key)
        if entry is None:
            return 0
        SortedSetStore._validate_type(entry)
        hash = entry.data
        count = 0
        for score in hash.values():
            if score >= min and score <= max:
                count += 1
        return count
