from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import SetStore


@executor("SADD")
async def sadd(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    members = command_parts[2:]
    count = SetStore.sadd(client.db, key, members)

    response = build_integer(count)
    await client.write_response(response)


@executor("SREM")
async def srem(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    members = command_parts[2:]
    count = SetStore.srem(client.db, key, members)

    response = build_integer(count)
    await client.write_response(response)


@executor("SISMEMBER")
async def sismember(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    member = command_parts[2]
    count = SetStore.sismember(client.db, key, member)

    response = build_integer(count)
    await client.write_response(response)


@executor("SMEMBERS")
async def smembers(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    members = SetStore.smembers(client.db, key)

    response = build_array(members)
    await client.write_response(response)


@executor("SCARD")
async def scard(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    length = SetStore.scard(client.db, key)

    response = build_integer(length)
    await client.write_response(response)


@executor("SPOP")
async def spop(client: Client, command_parts: list[str]):
    if len(command_parts) < 2 or len(command_parts) > 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    count = None
    if len(command_parts) == 3:
        try:
            count = int(command_parts[2])
            if count < 0:
                raise ValueError
        except ValueError:
            raise ValidationError("value is out of range, must be positive")

    if count is None:
        popped_member = SetStore.spop(client.db, key)
        response = build_bulk_string(popped_member)
    else:
        popped_members = SetStore.spop_with_count(client.db, key, count)
        response = build_array(popped_members)

    await client.write_response(response)


@executor("SRANDMEMBER")
async def srandmember(client: Client, command_parts: list[str]):
    if len(command_parts) < 2 or len(command_parts) > 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    count = None

    if len(command_parts) == 3:
        try:
            count = int(command_parts[2])
            if count < 0:
                raise ValueError
        except ValueError:
            raise ValidationError("value is out of range, must be positive")

    if count is None:
        random_member = SetStore.srandmember(client.db, key)
        response = build_bulk_string(random_member)
    else:
        random_members = SetStore.srandmember_with_count(client.db, key, count)
        response = build_array(random_members)

    await client.write_response(response)


@executor("SINTER")
async def sinter(client: Client, command_parts: list[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments for command")

    keys = command_parts[1:]
    inter_members = SetStore.sinter(client.db, keys)

    response = build_array(inter_members)
    await client.write_response(response)


@executor("SUNION")
async def sunion(client: Client, command_parts: list[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments for command")

    keys = command_parts[1:]
    inter_members = SetStore.sunion(client.db, keys)

    response = build_array(inter_members)
    await client.write_response(response)


@executor("SDIFF")
async def sdiff(client: Client, command_parts: list[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    keys = command_parts[2:] if len(command_parts) > 2 else []
    diff_members = SetStore.sdiff(client.db, key, keys)

    response = build_array(diff_members)
    await client.write_response(response)
