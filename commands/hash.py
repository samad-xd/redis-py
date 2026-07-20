from typing import List

from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import Database


@executor("HSET")
def hset(db: Database, command_parts: List[str]):
    if len(command_parts) < 3:
        raise ValidationError("key, field(s) and value(s) missing")
    if len(command_parts) % 2 == 0:
        raise ValidationError("missing value for a field")
    key = command_parts[0]
    fields_values = command_parts[1:]
    added_count = db.hash_store.hset(key, fields_values)
    return build_integer(added_count)


@executor("HGET")
def hget(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("key and field missing")
    key = command_parts[0]
    field = command_parts[1]
    value = db.hash_store.hget(key, field)
    return build_bulk_string(value)


@executor("HMGET")
def hmget(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("key and field(s) missing")
    key = command_parts[0]
    fields = command_parts[1:]
    values = db.hash_store.hmget(key, fields)
    return build_array(values)


@executor("HGETALL")
def hgetall(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    fields_values = db.hash_store.hgetall(key)
    return build_array(fields_values)


@executor("HDEL")
def hdel(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("key and field missing")
    key = command_parts[0]
    fields = command_parts[1:]
    deleted_count = db.hash_store.hdel(key, fields)
    return build_integer(deleted_count)


@executor("HEXISTS")
def hexists(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("key and field missing")
    key = command_parts[0]
    field = command_parts[1]
    exists = db.hash_store.hexists(key, field)
    return build_integer(exists)


@executor("HLEN")
def hlen(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    length = db.hash_store.hlen(key)
    return build_integer(length)


@executor("HKEYS")
def hkeys(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    fields = db.hash_store.hkeys(key)
    return build_array(fields)


@executor("HVALS")
def hvals(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    values = db.hash_store.hvals(key)
    return build_array(values)
