from client import Client
from exceptions import ValidationError
from executor import executor
from resp import (
    build_array,
    build_bulk_string,
    build_integer,
    build_simple_string,
)
from storage import ListStore


@executor("LPUSH")
async def lpush(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    items = command_parts[2:]
    count = await ListStore.lpush(client.db, key, items)

    response = build_integer(count)
    await client.write_response(response)


@executor("RPUSH")
async def rpush(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    items = command_parts[2:]
    count = await ListStore.rpush(client.db, key, items)

    response = build_integer(count)
    await client.write_response(response)


@executor("LPOP")
async def lpop(client: Client, command_parts: list[str]):
    if len(command_parts) < 2 or len(command_parts) > 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    count = None

    if len(command_parts) == 3:
        try:
            count = int(command_parts[2])
        except ValueError:
            raise ValidationError("value is out of range, must be positive")

    if count is None:
        item = ListStore.lpop(client.db, key)
        response = build_bulk_string(item)
    else:
        if count < 0:
            raise ValidationError("value is out of range, must be positive")
        if count == 0:
            response = build_bulk_string(None)
        else:
            items = ListStore.lpop_with_count(client.db, key, count)
            response = build_array(items)

    await client.write_response(response)


@executor("RPOP")
async def rpop(client: Client, command_parts: list[str]):
    if len(command_parts) < 2 or len(command_parts) > 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    count = None

    if len(command_parts) == 3:
        try:
            count = int(command_parts[2])
        except ValueError:
            raise ValidationError("value is out of range, must be positive")

    if count is None:
        item = ListStore.rpop(client.db, key)
        response = build_bulk_string(item)
    else:
        if count < 0:
            raise ValidationError("value is out of range, must be positive")
        if count == 0:
            response = build_bulk_string(None)
        else:
            items = ListStore.rpop_with_count(client.db, key, count)
            response = build_array(items)

    await client.write_response(response)


@executor("LLEN")
async def llen(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    length = ListStore.llen(client.db, key)

    response = build_integer(length)
    await client.write_response(response)


@executor("LRANGE")
async def lrange(client: Client, command_parts: list[str]):
    if len(command_parts) != 4:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        start = int(command_parts[2])
        stop = int(command_parts[3])
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    items = ListStore.lrange(client.db, key, start, stop)

    response = build_array(items)
    await client.write_response(response)


@executor("LINDEX")
async def lindex(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        index = int(command_parts[2])
        item = ListStore.lindex(client.db, key, index)
    except ValueError:
        raise ValidationError("index must be a number")

    response = build_bulk_string(item)
    await client.write_response(response)


@executor("LTRIM")
async def ltrim(client: Client, command_parts: list[str]):
    if len(command_parts) != 4:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        start = int(command_parts[2])
        stop = int(command_parts[3])
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    ListStore.ltrim(client.db, key, start, stop)

    response = build_simple_string("OK")
    await client.write_response(response)


@executor("BLPOP")
async def blpop(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    try:
        timeout = int(command_parts[-1])
        if timeout < 0:
            raise ValueError
    except ValueError:
        raise ValidationError("timeout is not an interger or not positive")

    keys = command_parts[1:-1]
    pair = await ListStore.blpop(client.db, keys, timeout)

    response = build_array(pair)
    await client.write_response(response)


@executor("BRPOP")
async def brpop(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    try:
        timeout = int(command_parts[-1])
        if timeout < 0:
            raise ValueError
    except ValueError:
        raise ValidationError("timeout is not an interger or not positive")

    keys = command_parts[1:-1]
    pair = await ListStore.brpop(client.db, keys, timeout)

    response = build_array(pair)
    await client.write_response(response)
