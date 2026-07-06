from executor import executor
from resp import (
    build_array,
    build_bulk_string,
    build_error,
    build_integer,
    build_simple_string,
)
from storage import list_store


@executor("LPUSH")
def lpush(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key and item")
    if len(command_parts) == 1:
        return build_error("ERR", "missing item")
    key = command_parts[0]
    items = command_parts[1:]
    count = list_store.lpush(key, items)
    return build_integer(count)


@executor("RPUSH")
def rpush(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key and item")
    if len(command_parts) == 1:
        return build_error("ERR", "missing item")
    key = command_parts[0]
    items = command_parts[1:]
    count = list_store.rpush(key, items)
    return build_integer(count)


@executor("LPOP")
def lpop(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    count = None
    if len(command_parts) > 1:
        try:
            count = int(command_parts[1])
        except ValueError:
            build_error("ERR", "count is not a number")
    if count is not None:
        if count < 0:
            return build_error("ERR", "count is out of range")
        if count == 0:
            return build_bulk_string(None)
        items = list_store.lpop_with_count(key, count)
        return build_array(items)
    item = list_store.lpop(key)
    return build_bulk_string(item)


@executor("RPOP")
def rpop(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    count = None
    if len(command_parts) > 1:
        try:
            count = int(command_parts[1])
        except ValueError:
            build_error("ERR", "count is not a number")
    if count is not None:
        if count < 0:
            return build_error("ERR", "count is out of range")
        if count == 0:
            return build_bulk_string(None)
        items = list_store.rpop_with_count(key, count)
        return build_array(items)
    item = list_store.rpop(key)
    return build_bulk_string(item)


@executor("LLEN")
def llen(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    length = list_store.llen(key)
    return build_integer(length)


@executor("LRANGE")
def lrange(command_parts):
    if not command_parts or len(command_parts) < 3:
        return build_error("ERR", "arguments key, start, and stop are required")
    key = command_parts[0]
    try:
        start = int(command_parts[1])
        stop = int(command_parts[2])
    except ValueError:
        return build_error("ERR", "start and stop must be a number")
    items = list_store.lrange(key, start, stop)
    return build_array(items)


@executor("LINDEX")
def lindex(command_parts):
    if not command_parts or len(command_parts) < 2:
        return build_error("ERR", "arguments key and index are required")
    key = command_parts[0]
    try:
        index = int(command_parts[1])
        item = list_store.lindex(key, index)
    except ValueError:
        return build_error("ERR", "index must be a number")
    except IndexError:
        return build_error("ERR", "index is out of range")
    return build_bulk_string(item)


@executor("LTRIM")
def ltrim(command_parts):
    if not command_parts or len(command_parts) < 3:
        return build_error("ERR", "argumnets key, start, and stop are required")
    key = command_parts[0]
    try:
        start = int(command_parts[1])
        stop = int(command_parts[2])
    except ValueError:
        return build_error("ERR", "start and stop must be a number")
    list_store.ltrim(key, start, stop)
    return build_simple_string("OK")
