from executor import executor
from resp import build_bulk_string, build_integer, build_simple_string
from storage import kv_store


@executor("GET")
def get(command_parts):
    key = command_parts[0]
    value = kv_store.get(key)
    return build_bulk_string(value)


@executor("SET")
def set(command_parts):
    key = command_parts[0]
    value = command_parts[1]
    kv_store.set(key, value)
    return build_simple_string("OK")


@executor("DEL")
def delete(command_parts):
    count = 0
    for key in command_parts:
        value = kv_store.delete(key)
        if value is not None:
            count += 1
    return build_integer(count)


@executor("EXISTS")
def exists(command_parts):
    count = 0
    for key in command_parts:
        if kv_store.exists(key):
            count += 1
    return build_integer(count)


@executor("DBSIZE")
def dbsize(*args, **kwargs):
    size = kv_store.size()
    return build_integer(size)


@executor("FLUSHDB")
def flushdb(*args, **kwargs):
    kv_store.clear_db()
    return build_simple_string("OK")
