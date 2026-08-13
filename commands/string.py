from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_bulk_string, build_integer, build_simple_string
from storage import StringStore


@executor("GET")
async def get(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    value = StringStore.get(client.db, key)

    response = build_bulk_string(value)
    await client.write_response(response)


@executor("SET")
async def set(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    value = command_parts[2]
    response = None

    if len(command_parts) == 5:
        time_type = command_parts[3]

        if time_type not in ("EX", "PX"):
            raise ValidationError("syntax error")

        if time_type == "EX":
            try:
                seconds = int(command_parts[4])
            except ValueError:
                raise ValidationError("value is not an integer or out of range")

        elif time_type == "PX":
            try:
                seconds = int(command_parts[4]) / 1000
            except ValueError:
                raise ValidationError("value is not an integer or out of range")

        StringStore.set(client.db, key, value)
        client.db.expire(key, seconds)

    elif len(command_parts) == 4:
        condition_type = command_parts[2]

        if condition_type not in ("NX", "XX"):
            raise ValidationError("syntax error")

        if condition_type == "NX":
            if client.db.exists(key):
                response = build_bulk_string(None)
            else:
                StringStore.set(client.db, key, value)

        elif condition_type == "XX":
            if client.db.exists(key):
                StringStore.set(client.db, key, value)
            else:
                response = build_bulk_string(None)

    else:
        StringStore.set(client.db, key, value)

    if response is None:
        response = build_simple_string("OK")

    await client.write_response(response)


@executor("INCR")
async def incr(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        value = StringStore.incr(client.db, key)
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    response = build_integer(value)
    await client.write_response(response)


@executor("DECR")
async def decr(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        value = StringStore.decr(client.db, key)
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    response = build_integer(value)
    await client.write_response(response)


@executor("INCRBY")
async def incrby(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        incr_value = int(command_parts[2])
        value = StringStore.incrby(client.db, key, incr_value)
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    response = build_integer(value)
    await client.write_response(response)


@executor("DECRBY")
async def decrby(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        incr_value = int(command_parts[2])
        value = StringStore.decrby(client.db, key, incr_value)
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    response = build_integer(value)
    await client.write_response(response)


@executor("APPEND")
async def append(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    value = command_parts[2]
    length = StringStore.append(client.db, key, value)

    response = build_integer(length)
    await client.write_response(response)


@executor("STRLEN")
async def strlen(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    length = StringStore.strlen(client.db, key)

    response = build_integer(length)
    await client.write_response(response)
