from itertools import islice

from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_integer, build_simple_string


@executor("TYPE")
async def type(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    value_type = client.db.type(key)

    response = build_simple_string(value_type)
    await client.write_response(response)


@executor("DEL")
async def delete(client: Client, command_parts: list[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments for command")

    count = 0
    for key in islice(command_parts, 1, None):
        value = client.db.delete(key)
        if value is not None:
            count += 1

    response = build_integer(count)
    await client.write_response(response)


@executor("EXISTS")
async def exists(client: Client, command_parts: list[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments for command")

    count = 0
    for key in islice(command_parts, 1, None):
        if client.db.exists(key):
            count += 1

    response = build_integer(count)
    await client.write_response(response)


@executor("DBSIZE")
async def dbsize(client: Client, command_parts: list[str]):
    if len(command_parts) != 1:
        raise ValidationError("wrong number of arguments for command")

    size = client.db.db_size()

    response = build_integer(size)
    await client.write_response(response)


@executor("FLUSHDB")
async def flushdb(client: Client, *args):
    client.db.clear_db()

    response = build_simple_string("OK")
    await client.write_response(response)


@executor("EXPIRE")
async def expire(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        seconds = int(command_parts[2])
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    status = client.db.expire(key, seconds)

    response = build_integer(status)
    await client.write_response(response)


@executor("PEXPIRE")
async def pexpire(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        seconds = int(command_parts[2]) / 1000
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    status = client.db.expire(key, seconds)

    response = build_integer(status)
    await client.write_response(response)


@executor("TTL")
async def ttl(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    time_left = client.db.ttl(key)

    response = build_integer(int(time_left))
    await client.write_response(response)


@executor("PTTL")
async def pttl(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    time_left = client.db.ttl(key)

    if time_left < 0:
        return build_integer(time_left)
    time_left_in_milliseconds = int(time_left * 1000)

    response = build_integer(time_left_in_milliseconds)
    await client.write_response(response)


@executor("PERSIST")
async def persist(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    status = client.db.persist(key)

    response = build_integer(status)
    await client.write_response(response)
