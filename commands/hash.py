from executor import executor
from resp import build_array, build_bulk_string, build_error, build_integer
from storage import hash_store


@executor("HSET")
def hset(command_parts):
    if len(command_parts) < 3:
        return build_error("ERR", "arguments key field value are required")
    if len(command_parts) % 2 == 0:
        return build_error("ERR", "missing value for a field")
    key = command_parts[0]
    fields_values = command_parts[1:]
    added_count = hash_store.hset(key, fields_values)
    return build_integer(added_count)


@executor("HGET")
def hget(command_parts):
    if len(command_parts) < 2:
        return build_error("ERR", "arguments key and field are required")
    key = command_parts[0]
    field = command_parts[1]
    value = hash_store.hget(key, field)
    return build_bulk_string(value)


@executor("HMGET")
def hmget(command_parts):
    if len(command_parts) < 2:
        return build_error("ERR", "arguments key and field are required")
    key = command_parts[0]
    fields = command_parts[1:]
    values = hash_store.hmget(key, fields)
    return build_array(values)


@executor("HGETALL")
def hgetall(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    fields_values = hash_store.hgetall(key)
    return build_array(fields_values)


@executor("HDEL")
def hdel(command_parts):
    if len(command_parts) < 2:
        return build_error("ERR", "arguments key and field are required")
    key = command_parts[0]
    fields = command_parts[1:]
    deleted_count = hash_store.hdel(key, fields)
    return build_integer(deleted_count)


@executor("HEXISTS")
def hexists(command_parts):
    if len(command_parts) < 2:
        return build_error("ERR", "arguments key and field are required")
    key = command_parts[0]
    field = command_parts[1]
    exists = hash_store.hexists(key, field)
    return build_integer(exists)


@executor("HLEN")
def hlen(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    length = hash_store.hlen(key)
    return build_integer(length)


@executor("HKEYS")
def hkeys(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    fields = hash_store.hkeys(key)
    return build_array(fields)


@executor("HVALS")
def hvals(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    values = hash_store.hvals(key)
    return build_array(values)
