from executor import executor
from resp import build_bulk_string, build_error, build_integer, build_simple_string
from storage import kv_store


@executor("GET")
def get(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    value = kv_store.get(key)
    return build_bulk_string(value)


@executor("SET")
def set(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key and value")
    if len(command_parts) == 1:
        return build_error("ERR", "missing value")
    key = command_parts[0]
    value = command_parts[1]
    if len(command_parts) == 4:
        time_type = command_parts[2]
        if time_type not in ("EX", "PX"):
            return build_error("ERR", "expecting EX or PX and time")
        if time_type == "EX":
            try:
                seconds = int(command_parts[3])
            except ValueError:
                return build_error("ERR", "seconds must be a number")
        elif time_type == "PX":
            try:
                seconds = int(command_parts[3]) / 1000
            except ValueError:
                return build_error("ERR", "milliseconds must be a number")
        kv_store.set(key, value)
        kv_store.expire(key, seconds)
    elif len(command_parts) == 3:
        condition_type = command_parts[2]
        if condition_type not in ("NX", "XX"):
            return build_error("ERR", "expecting NX or XX")
        if condition_type == "NX":
            if not kv_store.exists(key):
                kv_store.set(key, value)
            else:
                return build_bulk_string(None)
        elif condition_type == "XX":
            if kv_store.exists(key):
                kv_store.set(key, value)
            else:
                return build_bulk_string(None)
    else:
        kv_store.set(key, value)
    return build_simple_string("OK")


@executor("DEL")
def delete(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    count = 0
    for key in command_parts:
        value = kv_store.delete(key)
        if value is not None:
            count += 1
    return build_integer(count)


@executor("EXISTS")
def exists(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
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


@executor("EXPIRE")
def expire(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key and seconds")
    if len(command_parts) == 1:
        return build_error("ERR", "missing seconds")
    key = command_parts[0]
    try:
        seconds = int(command_parts[1])
    except ValueError:
        return build_error("ERR", "seconds must be a number")
    status = kv_store.expire(key, seconds)
    return build_integer(status)


@executor("PEXPIRE")
def pexpire(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key and seconds")
    if len(command_parts) == 1:
        return build_error("ERR", "missing seconds")
    key = command_parts[0]
    try:
        seconds = int(command_parts[1]) / 1000
    except ValueError:
        return build_error("ERR", "milliseconds must be a number")
    status = kv_store.expire(key, seconds)
    return build_integer(status)


@executor("TTL")
def ttl(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    time_left = kv_store.ttl(key)
    return build_integer(int(time_left))


@executor("PTTL")
def pttl(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    time_left = kv_store.ttl(key)
    if time_left < 0:
        return build_integer(time_left)
    time_left_in_milliseconds = int(time_left * 1000)
    return build_integer(time_left_in_milliseconds)


@executor("PERSIST")
def persist(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    status = kv_store.persist(key)
    return build_integer(status)


@executor("INCR")
def incr(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    try:
        value = kv_store.incr(key)
    except ValueError:
        return build_error("ERR", "value is not an integer")
    return build_integer(value)


@executor("DECR")
def decr(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    try:
        value = kv_store.decr(key)
    except ValueError:
        return build_error("ERR", "value is not an integer")
    return build_integer(value)


@executor("INCRBY")
def incrby(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    if len(command_parts) == 1:
        return build_error("ERR", "missing incr value")
    key = command_parts[0]
    try:
        incr_value = int(command_parts[1])
    except ValueError:
        return build_error("ERR", "incr value must be a number")
    try:
        value = kv_store.incrby(key, incr_value)
    except ValueError:
        return build_error("ERR", "value is not an integer")
    return build_integer(value)


@executor("DECRBY")
def decrby(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    if len(command_parts) == 1:
        return build_error("ERR", "missing decr value")
    key = command_parts[0]
    try:
        decr_value = int(command_parts[1])
    except ValueError:
        return build_error("ERR", "decr value must be a number")
    try:
        value = kv_store.decrby(key, decr_value)
    except ValueError:
        return build_error("ERR", "value is not an integer")
    return build_integer(value)


@executor("APPEND")
def append(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    if len(command_parts) == 1:
        return build_error("ERR", "missing append value")
    key = command_parts[0]
    value = command_parts[1]
    length = kv_store.append(key, value)
    return build_integer(length)


@executor("STRLEN")
def strlen(command_parts):
    if not command_parts:
        return build_error("ERR", "missing key")
    key = command_parts[0]
    length = kv_store.strlen(key)
    return build_integer(length)
