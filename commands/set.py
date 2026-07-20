from typing import List

from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import Database


@executor("SADD")
def sadd(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    if len(command_parts) == 1:
        raise ValidationError("member(s) missing")
    key = command_parts[0]
    members = command_parts[1:]
    count = db.set_store.sadd(key, members)
    return build_integer(count)


@executor("SREM")
def srem(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    if len(command_parts) == 1:
        raise ValidationError("member(s) missing")
    key = command_parts[0]
    members = command_parts[1:]
    count = db.set_store.srem(key, members)
    return build_integer(count)


@executor("SISMEMBER")
def sismember(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    if len(command_parts) == 1:
        raise ValidationError("member missing")
    key = command_parts[0]
    member = command_parts[1]
    count = db.set_store.sismember(key, member)
    return build_integer(count)


@executor("SMEMBERS")
def smembers(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    members = db.set_store.smembers(key)
    return build_array(members)


@executor("SCARD")
def scard(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    length = db.set_store.scard(key)
    return build_integer(length)


@executor("SPOP")
def spop(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    count = None
    if len(command_parts) == 2:
        try:
            count = int(command_parts[1])
            if count < 0:
                raise ValidationError("count must be positive")
        except ValueError:
            raise ValueError("count must be a number")
    if count is None:
        popped_member = db.set_store.spop(key)
        return build_bulk_string(popped_member)
    popped_members = db.set_store.spop_with_count(key, count)
    return build_array(popped_members)


@executor("SRANDMEMBER")
def srandmember(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    count = None
    if len(command_parts) == 2:
        try:
            count = int(command_parts[1])
        except ValueError:
            raise ValueError("count must be a number")
    if count is None:
        random_member = db.set_store.srandmember(key)
        return build_bulk_string(random_member)
    random_members = db.set_store.srandmember_with_count(key, count)
    return build_array(random_members)


@executor("SINTER")
def sinter(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    keys = command_parts
    inter_members = db.set_store.sinter(keys)
    return build_array(inter_members)


@executor("SUNION")
def sunion(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    keys = command_parts
    union_members = db.set_store.sunion(keys)
    return build_array(union_members)


@executor("SDIFF")
def sdiff(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    keys = command_parts[1:]
    diff_members = db.set_store.sdiff(key, keys)
    return build_array(diff_members)
