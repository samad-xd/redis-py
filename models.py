from dataclasses import dataclass
from enum import Enum
from typing import Any


class RedisType(str, Enum):
    STRING = "string"
    LIST = "list"
    HASH = "hash"
    SET = "set"
    SORTED_SET = "sorted set"


@dataclass
class Entry:
    type: RedisType
    data: Any
    expire: int = 0
