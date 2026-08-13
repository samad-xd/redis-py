import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any


class RedisType(str, Enum):
    STRING = "string"
    LIST = "list"
    HASH = "hash"
    SET = "set"
    SORTED_SET = "sorted set"
    STREAM = "stream"


@dataclass
class Entry:
    type: RedisType
    data: Any
    expire: int = 0


@dataclass
class Waiter:
    future: asyncio.Future
    keys: list[str]
    active: bool = True
