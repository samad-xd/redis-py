from typing import List

from exceptions import ValidationError
from executor import executor
from resp import build_integer, build_simple_string
from storage import Database


@executor("TYPE")
def type(db: Database, command_parts: List[str]):
    key = command_parts[0]
    value_type = db.type(key)
    return build_simple_string(value_type)


@executor("DEL")
def delete(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    count = 0
    for key in command_parts:
        value = db.delete(key)
        if value is not None:
            count += 1
    return build_integer(count)


@executor("EXISTS")
def exists(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    count = 0
    for key in command_parts:
        if db.exists(key):
            count += 1
    return build_integer(count)


@executor("DBSIZE")
def dbsize(db: Database, *args, **kwargs):
    size = db.db_size()
    return build_integer(size)


@executor("FLUSHDB")
def flushdb(db: Database, *args, **kwargs):
    db.clear_db()
    return build_simple_string("OK")


@executor("EXPIRE")
def expire(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key and seconds missing")
    if len(command_parts) == 1:
        raise ValidationError("seconds missing")
    key = command_parts[0]
    try:
        seconds = int(command_parts[1])
    except ValueError:
        raise ValidationError("seconds must be a number")
    status = db.expire(key, seconds)
    return build_integer(status)


@executor("PEXPIRE")
def pexpire(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key and seconds missing")
    if len(command_parts) == 1:
        raise ValidationError("seconds missing")
    key = command_parts[0]
    try:
        seconds = int(command_parts[1]) / 1000
    except ValueError:
        raise ValidationError("milliseconds must be a number")
    status = db.expire(key, seconds)
    return build_integer(status)


@executor("TTL")
def ttl(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    time_left = db.ttl(key)
    return build_integer(int(time_left))


@executor("PTTL")
def pttl(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    time_left = db.ttl(key)
    if time_left < 0:
        return build_integer(time_left)
    time_left_in_milliseconds = int(time_left * 1000)
    return build_integer(time_left_in_milliseconds)


@executor("PERSIST")
def persist(db: Database, command_parts: List[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    status = db.persist(key)
    return build_integer(status)
