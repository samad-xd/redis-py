from exceptions import ValidationError
from executor import executor
from resp import build_bulk_string, build_integer, build_simple_string
from storage import Database


@executor("GET")
def get(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    db.ensure_key_life(key)
    value = db.string_store.get(key)
    return build_bulk_string(value)


@executor("SET")
def set(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key and value missing")
    if len(command_parts) == 1:
        raise ValidationError("value missing")
    key = command_parts[0]
    value = command_parts[1]
    if len(command_parts) == 4:
        time_type = command_parts[2]
        if time_type not in ("EX", "PX"):
            raise ValidationError("expecting EX or PX and time")
        if time_type == "EX":
            try:
                seconds = int(command_parts[3])
            except ValueError:
                raise ValidationError("seconds must be a number")
        elif time_type == "PX":
            try:
                seconds = int(command_parts[3]) / 1000
            except ValueError:
                raise ValidationError("milliseconds must be a number")
        db.string_store.set(key, value)
        db.expire(key, seconds)
    elif len(command_parts) == 3:
        condition_type = command_parts[2]
        if condition_type not in ("NX", "XX"):
            raise ValidationError("expecting NX or XX")
        if condition_type == "NX":
            if db.exists(key):
                return build_bulk_string(None)
            else:
                db.string_store.set(key, value)
        elif condition_type == "XX":
            if db.exists(key):
                db.string_store.set(key, value)
            else:
                return build_bulk_string(None)
    else:
        db.string_store.set(key, value)
    return build_simple_string("OK")


@executor("INCR")
def incr(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    db.ensure_key_life(key)
    try:
        value = db.string_store.incr(key)
    except ValueError:
        raise ValidationError("value is not an integer")
    return build_integer(value)


@executor("DECR")
def decr(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key missing")
    key = command_parts[0]
    db.ensure_key_life(key)
    try:
        value = db.string_store.decr(key)
    except ValueError:
        raise ValidationError("value is not an integer")
    return build_integer(value)


@executor("INCRBY")
def incrby(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("key missing")
    if len(command_parts) == 1:
        raise ValidationError("missing incr value")
    key = command_parts[0]
    db.ensure_key_life(key)
    try:
        incr_value = int(command_parts[1])
    except ValueError:
        raise ValidationError("incr value must be a number")
    try:
        value = db.string_store.incrby(key, incr_value)
    except ValueError:
        raise ValidationError("value is not an integer")
    return build_integer(value)


@executor("DECRBY")
def decrby(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("missing key")
    if len(command_parts) == 1:
        raise ValidationError("missing value")
    key = command_parts[0]
    db.ensure_key_life(key)
    try:
        decr_value = int(command_parts[1])
    except ValueError:
        raise ValidationError("decr value must be a number")
    try:
        value = db.string_store.decrby(key, decr_value)
    except ValueError:
        raise ValidationError("value is not an integer")
    return build_integer(value)


@executor("APPEND")
def append(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("missing key")
    if len(command_parts) == 1:
        raise ValidationError("missing append value")
    key = command_parts[0]
    value = command_parts[1]
    db.ensure_key_life(key)
    length = db.string_store.append(key, value)
    return build_integer(length)


@executor("STRLEN")
def strlen(db: Database, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("missing key")
    key = command_parts[0]
    db.ensure_key_life(key)
    length = db.string_store.strlen(key)
    return build_integer(length)
