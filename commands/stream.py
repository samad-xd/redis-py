from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import StreamStore


@executor("XADD")
async def xadd(client: Client, command_parts: list[str]):
    if len(command_parts) < 5:
        raise ValidationError("wrong number of arguments for command")

    if len(command_parts) % 2 == 0:
        raise ValidationError("wrong number of arguments for 'xadd' command")

    key = command_parts[1]
    id = command_parts[2]
    fields_and_values = command_parts[3:]
    last_id = await StreamStore.xadd(client.db, key, id, fields_and_values)

    response = build_bulk_string(last_id)
    await client.write_response(response)


@executor("XRANGE")
async def xrange(client: Client, command_parts: list[str]):
    if len(command_parts) < 4 or len(command_parts) > 5:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    start = command_parts[2]
    end = command_parts[3]
    count = None

    if len(command_parts) == 5:
        try:
            count = int(command_parts[4])
        except ValueError:
            raise ValidationError("value is not an integer or out of range")

    items = StreamStore.xrange(client.db, key, start, end, count)

    response = build_array(items)
    await client.write_response(response)


@executor("XREVRANGE")
async def xrevrange(client: Client, command_parts: list[str]):
    if len(command_parts) < 4 or len(command_parts) > 5:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    start = command_parts[2]
    end = command_parts[3]
    count = None

    if len(command_parts) == 5:
        try:
            count = int(command_parts[4])
        except ValueError:
            raise ValidationError("value is not an integer or out of range")
    items = StreamStore.xrevrange(client.db, key, start, end, count)

    response = build_array(items)
    await client.write_response(response)


@executor("XLEN")
async def xlen(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    length = StreamStore.xlen(client.db, key)

    response = build_integer(length)
    await client.write_response(response)


@executor("XREAD")
async def xread(client: Client, command_parts: list[str]):
    n = len(command_parts)
    if n < 4 or n % 2 != 0:
        raise ValidationError("wrong number of arguments for command")

    i = 1
    block = None
    action = command_parts[i].upper()

    if action == "BLOCK":
        try:
            block = int(command_parts[2]) / 1000
        except ValueError:
            raise ValidationError("value is not an integer or out of range")
        i += 2

    if command_parts[i].upper() != "STREAMS":
        raise ValidationError("syntax error")

    i += 1
    mid = (n - i) // 2
    keys = command_parts[i : i + mid]
    ids = command_parts[i + mid :]
    items = await StreamStore.xread(client.db, block, keys, ids)

    response = build_array(items)
    await client.write_response(response)
