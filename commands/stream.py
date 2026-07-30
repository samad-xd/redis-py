from exceptions import ValidationError
from executor import executor
from resp import build_array, build_bulk_string, build_integer
from storage import Database


@executor("XADD")
async def xadd(db: Database, command_parts: list[str]):
    if len(command_parts) < 4 or len(command_parts) % 2 == 1:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    id = command_parts[1]
    fields_and_values = command_parts[2:]
    last_id = await db.stream_store.xadd(key, id, fields_and_values)
    return build_bulk_string(last_id)


@executor("XRANGE")
def xrange(db: Database, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    start = command_parts[1]
    end = command_parts[2]
    count = None
    if len(command_parts) == 4:
        try:
            count = int(command_parts[3])
        except ValueError:
            raise ValidationError("count must be a number")
    items = db.stream_store.xrange(key, start, end, count)
    return build_array(items)


@executor("XREVRANGE")
def xrevrange(db: Database, command_parts: list[str]):
    if len(command_parts) < 3:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    end = command_parts[1]
    start = command_parts[2]
    count = None
    if len(command_parts) == 4:
        try:
            count = int(command_parts[3])
        except ValueError:
            raise ValidationError("count must be a number")
    items = db.stream_store.xrevrange(key, end, start, count)
    return build_array(items)


@executor("XLEN")
def xlen(db: Database, command_parts: list[str]):
    if len(command_parts) != 1:
        raise ValidationError("wrong number of arguments passed")
    key = command_parts[0]
    length = db.stream_store.xlen(key)
    return build_integer(length)


@executor("XREAD")
async def xread(db: Database, command_parts: list[str]):
    n = len(command_parts)
    if n < 3 or n % 2 == 0:
        raise ValidationError("wrong number of arguments passed")
    i = 0
    block = None
    action = command_parts[i].upper()
    if action == "BLOCK":
        try:
            block = int(command_parts[1]) / 1000
        except ValueError:
            raise ValidationError("block must be a number in milliseconds")
        i += 2
    if command_parts[i].upper() != "STREAMS":
        raise ValidationError("STREAMS expected")
    i += 1
    mid = (n - i) // 2
    keys = command_parts[i : i + mid]
    ids = command_parts[i + mid :]
    items = await db.stream_store.xread(block, keys, ids)
    return build_array(items)
