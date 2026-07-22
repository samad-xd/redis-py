from typing import List

from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import Database


@executor("ZADD")
def zadd(db: Database, command_parts: List[str]):
    n = len(command_parts)
    if n < 3 or n % 2 == 0:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    score_member_pairs = []
    for i in range(1, n, 2):
        try:
            score = float(command_parts[i])
        except ValueError:
            raise ValidationError("score must be a number")
        member = command_parts[i + 1]
        score_member_pairs.append((score, member))
    added_count = db.sorted_set_store.zadd(key, score_member_pairs)
    return build_integer(added_count)


@executor("ZSCORE")
def zscore(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    member = command_parts[1]
    score = db.sorted_set_store.zscore(key, member)
    return build_bulk_string(score)


@executor("ZRANK")
def zrank(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    member = command_parts[1]
    rank = db.sorted_set_store.zrank(key, member)
    if rank is None:
        return build_bulk_string(None)
    return build_integer(rank)


@executor("ZREVRANK")
def zrevrank(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    member = command_parts[1]
    rev_rank = db.sorted_set_store.zrevrank(key, member)
    if rev_rank is None:
        return build_bulk_string(None)
    return build_integer(rev_rank)


@executor("ZRANGE")
def zrange(db: Database, command_parts: List[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    try:
        start = int(command_parts[1])
        stop = int(command_parts[2])
    except ValueError:
        raise ValidationError("start and stop indexes must be int")
    with_scores = (
        True
        if len(command_parts) == 4 and command_parts[3].upper() == "WITHSCORES"
        else False
    )
    range_data = db.sorted_set_store.zrange(key, start, stop, with_scores)
    return build_array(range_data)


@executor("ZREVRANGE")
def zrevrange(db: Database, command_parts: List[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    try:
        start = int(command_parts[1])
        stop = int(command_parts[2])
    except ValueError:
        raise ValidationError("start and stop indexes must be int")
    with_scores = (
        True
        if len(command_parts) == 4 and command_parts[3].upper() == "WITHSCORES"
        else False
    )
    range_data = db.sorted_set_store.zrevrange(key, start, stop, with_scores)
    return build_array(range_data)


@executor("ZREM")
def zrem(db: Database, command_parts: List[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    members = command_parts[1:]
    removed_count = db.sorted_set_store.zrem(key, members)
    return build_integer(removed_count)


@executor("ZCARD")
def zcard(db: Database, command_parts: List[str]):
    if len(command_parts) != 1:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    length = db.sorted_set_store.zcard(key)
    return build_integer(length)


@executor("ZCOUNT")
def zcount(db: Database, command_parts: List[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    try:
        min = float(command_parts[1])
        max = float(command_parts[2])
    except ValueError:
        raise ValidationError("start and stop indexes must be float")
    length = db.sorted_set_store.zcount(key, min, max)
    return build_integer(length)
