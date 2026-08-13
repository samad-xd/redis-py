from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import HashStore


@executor("HSET")
async def hset(client: Client, command_parts: list[str]):
    if len(command_parts) < 4:
        raise ValidationError("wrong number of arguments for command")

    if len(command_parts) % 2 != 0:
        raise ValidationError("wrong number of arguments for 'hset' command")

    key = command_parts[1]
    fields_values = command_parts[2:]
    added_count = HashStore.hset(client.db, key, fields_values)

    response = build_integer(added_count)
    await client.write_response(response)


@executor("HGET")
async def hget(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    field = command_parts[2]
    value = HashStore.hget(client.db, key, field)

    response = build_bulk_string(value)
    await client.write_response(response)


@executor("HMGET")
async def hmget(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    fields = command_parts[2:]
    values = HashStore.hmget(client.db, key, fields)

    response = build_array(values)
    await client.write_response(response)


@executor("HGETALL")
async def hgetall(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    fields_values = HashStore.hgetall(client.db, key)

    response = build_array(fields_values)
    await client.write_response(response)


@executor("HDEL")
async def hdel(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    fields = command_parts[2:]
    deleted_count = HashStore.hdel(client.db, key, fields)

    response = build_integer(deleted_count)
    await client.write_response(response)


@executor("HEXISTS")
async def hexists(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    field = command_parts[2]
    exists = HashStore.hexists(client.db, key, field)

    response = build_integer(exists)
    await client.write_response(response)


@executor("HLEN")
async def hlen(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    length = HashStore.hlen(client.db, key)

    response = build_integer(length)
    await client.write_response(response)


@executor("HKEYS")
async def hkeys(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    fields = HashStore.hkeys(client.db, key)

    response = build_array(fields)
    await client.write_response(response)


@executor("HVALS")
async def hvals(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    values = HashStore.hvals(client.db, key)

    response = build_array(values)
    await client.write_response(response)
