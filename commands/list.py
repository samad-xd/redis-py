from exceptions import ValidationError
from executor import executor
from resp import (
    build_array,
    build_bulk_string,
    build_integer,
    build_simple_string,
)
from storage import Database


@executor("LPUSH")
async def lpush(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key and value(s) missing")
    if len(command_parts) == 1:
        raise ValidationError("missing value(s)")
    key = command_parts[0]
    items = command_parts[1:]
    count = await db.list_store.lpush(key, items)
    return build_integer(count)


@executor("RPUSH")
async def rpush(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key and value(s) missing")
    if len(command_parts) == 1:
        raise ValidationError("missing value(s)")
    key = command_parts[0]
    items = command_parts[1:]
    count = await db.list_store.rpush(key, items)
    return build_integer(count)


@executor("LPOP")
def lpop(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    count = None
    if len(command_parts) > 1:
        try:
            count = int(command_parts[1])
        except ValueError:
            raise ValidationError("count is not a number")
    if count is not None:
        if count < 0:
            raise ValidationError("count is out of range")
        if count == 0:
            return build_bulk_string(None)
        items = db.list_store.lpop_with_count(key, count)
        return build_array(items)
    item = db.list_store.lpop(key)
    return build_bulk_string(item)


@executor("RPOP")
def rpop(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    count = None
    if len(command_parts) > 1:
        try:
            count = int(command_parts[1])
        except ValueError:
            raise ValidationError("count is not a number")
    if count is not None:
        if count < 0:
            raise ValidationError("count is out of range")
        if count == 0:
            return build_bulk_string(None)
        items = db.list_store.rpop_with_count(key, count)
        return build_array(items)
    item = db.list_store.rpop(key)
    return build_bulk_string(item)


@executor("LLEN")
def llen(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    length = db.list_store.llen(key)
    return build_integer(length)


@executor("LRANGE")
def lrange(db: Database, command_parts: list[str]):
    if not command_parts or len(command_parts) < 3:
        raise ValidationError("arguments key, start, and stop are required")
    key = command_parts[0]
    try:
        start = int(command_parts[1])
        stop = int(command_parts[2])
    except ValueError:
        raise ValidationError("start and stop must be a number")
    items = db.list_store.lrange(key, start, stop)
    return build_array(items)


@executor("LINDEX")
def lindex(db: Database, command_parts: list[str]):
    if not command_parts or len(command_parts) < 2:
        raise ValidationError("arguments key and index are required")
    key = command_parts[0]
    try:
        index = int(command_parts[1])
        item = db.list_store.lindex(key, index)
    except ValueError:
        raise ValidationError("index must be a number")
    except IndexError:
        raise ValidationError("index is out of range")
    return build_bulk_string(item)


@executor("LTRIM")
def ltrim(db: Database, command_parts: list[str]):
    if not command_parts or len(command_parts) < 3:
        raise ValidationError("arguments key, start, and stop are required")
    key = command_parts[0]
    try:
        start = int(command_parts[1])
        stop = int(command_parts[2])
    except ValueError:
        raise ValidationError("start and stop must be a number")
    db.list_store.ltrim(key, start, stop)
    return build_simple_string("OK")


@executor("BLPOP")
async def blpop(db: Database, command_parts: list[str]):
    if not command_parts or len(command_parts) < 2:
        raise ValidationError("arguments key(s) and timeout are required")
    try:
        timeout = int(command_parts[-1])
    except ValueError:
        raise ValidationError("timeout must be a number")
    if timeout < 0:
        raise ValidationError("timeout is negative")
    keys = command_parts[:-1]
    pair = await db.list_store.blpop(keys, timeout)
    return build_array(pair)


@executor("BRPOP")
async def brpop(db: Database, command_parts: list[str]):
    if not command_parts or len(command_parts) < 2:
        raise ValidationError("arguments key(s) and timeout are required")
    try:
        timeout = int(command_parts[-1])
    except ValueError:
        raise ValidationError("timeout must be a number")
    if timeout < 0:
        raise ValidationError("timeout is negative")
    keys = command_parts[:-1]
    pair = await db.list_store.brpop(keys, timeout)
    return build_array(pair)
