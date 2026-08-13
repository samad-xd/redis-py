from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import SortedSetStore


@executor("ZADD")
async def zadd(client: Client, command_parts: list[str]):
    if len(command_parts) < 4:
        raise ValidationError("wrong number of arguments for command")

    if len(command_parts) % 2 != 0:
        raise ValidationError("syntax error")

    key = command_parts[1]
    score_member_pairs = []

    for i in range(2, len(command_parts), 2):
        try:
            score = float(command_parts[i])
        except ValueError:
            raise ValidationError("value is not a valid float")
        member = command_parts[i + 1]
        score_member_pairs.append((score, member))

    added_count = SortedSetStore.zadd(client.db, key, score_member_pairs)

    response = build_integer(added_count)
    await client.write_response(response)


@executor("ZSCORE")
async def zscore(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    member = command_parts[2]
    score = SortedSetStore.zscore(client.db, key, member)

    response = build_bulk_string(score)
    await client.write_response(response)


@executor("ZRANK")
async def zrank(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    member = command_parts[2]
    rank = SortedSetStore.zrank(client.db, key, member)

    if rank is None:
        response = build_bulk_string(None)
    else:
        response = build_integer(rank)

    await client.write_response(response)


@executor("ZREVRANK")
async def zrevrank(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    member = command_parts[2]
    rev_rank = SortedSetStore.zrevrank(client.db, key, member)

    if rev_rank is None:
        response = build_bulk_string(None)
    else:
        response = build_integer(rev_rank)

    await client.write_response(response)


@executor("ZRANGE")
async def zrange(client: Client, command_parts: list[str]):
    if len(command_parts) < 4 or len(command_parts) > 5:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    try:
        start = int(command_parts[2])
        stop = int(command_parts[3])
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    with_scores = False
    if len(command_parts) == 5:
        if command_parts[4].upper() == "WITHSCORES":
            with_scores = True
        else:
            raise ValidationError("syntax error")
    range_data = SortedSetStore.zrange(client.db, key, start, stop, with_scores)

    response = build_array(range_data)
    await client.write_response(response)


@executor("ZREVRANGE")
async def zrevrange(client: Client, command_parts: list[str]):
    if len(command_parts) < 4 or len(command_parts) > 5:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        start = int(command_parts[2])
        stop = int(command_parts[3])
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    with_scores = False
    if len(command_parts) == 5:
        if command_parts[4].upper() == "WITHSCORES":
            with_scores = True
        else:
            raise ValidationError("syntax error")
    range_data = SortedSetStore.zrevrange(client.db, key, start, stop, with_scores)

    response = build_array(range_data)
    await client.write_response(response)


@executor("ZREM")
async def zrem(client: Client, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    members = command_parts[2:]
    removed_count = SortedSetStore.zrem(client.db, key, members)

    response = build_integer(removed_count)
    await client.write_response(response)


@executor("ZCARD")
async def zcard(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]
    length = SortedSetStore.zcard(client.db, key)

    response = build_integer(length)
    await client.write_response(response)


@executor("ZCOUNT")
async def zcount(client: Client, command_parts: list[str]):
    if len(command_parts) != 4:
        raise ValidationError("wrong number of arguments for command")

    key = command_parts[1]

    try:
        min = float(command_parts[2])
        max = float(command_parts[3])
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    length = SortedSetStore.zcount(client.db, key, min, max)

    response = build_integer(length)
    await client.write_response(response)
