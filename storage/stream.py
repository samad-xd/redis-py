import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from exceptions import ValidationError, WrongTypeError
from models import Entry, RedisType


@dataclass
class Waiter:
    future: asyncio.Future
    keys: list[str]
    active: bool = True


class StreamStore:
    def __init__(self, db: dict[str, Entry]):
        self.db = db
        self._waiters: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    def _validate_type(self, entry: Entry):
        if entry.type != RedisType.STREAM:
            raise WrongTypeError("value is not a stream")

    async def xadd(self, key: str, id: str, fields_and_values: list[str]):
        entry = self.db.get(key)
        if entry is None:
            entry = Entry(type=RedisType.STREAM, data=[])
        else:
            self._validate_type(entry)
        stream = entry.data

        last_ms = 0
        last_seq = 0
        if stream:
            last_ms, last_seq, _ = stream[-1]

        if id == "*":
            curr_ms = int(time.time() * 1000)
            if curr_ms == last_ms:
                curr_seq = last_seq + 1
            else:
                curr_seq = 0
                if curr_ms < last_ms:
                    curr_ms = last_ms
                    curr_seq = last_seq + 1

        elif id.endswith("-*"):
            try:
                curr_ms = int(id[:-2])
            except ValueError:
                raise ValidationError("Invalid ID")
            curr_seq = last_seq + 1 if curr_ms == last_ms else 0

        else:
            if "-" in id:
                parts = id.split("-")
                try:
                    curr_ms = int(parts[0])
                    curr_seq = int(parts[1])
                except ValueError:
                    raise ValidationError("Invalid ID format")
            else:
                try:
                    curr_ms = int(id)
                    curr_seq = 0
                except ValueError:
                    raise ValidationError("Invalid ID format")

        if curr_ms == 0 and curr_seq == 0:
            raise ValidationError("The ID must be greater than 0-0")

        if (curr_ms < last_ms) or (curr_ms == last_ms and curr_seq <= last_seq):
            raise ValidationError("ID must be grater than last stream ID")

        curr_id = f"{curr_ms}-{curr_seq}"

        async with self._lock:
            active_waiter = self._pop_active_waiter(key)
            if active_waiter:
                result = [key, [curr_id, fields_and_values]]
                self._finish_waiter(active_waiter, result)
            data = {}
            for i in range(0, len(fields_and_values), 2):
                field = fields_and_values[i]
                value = fields_and_values[i + 1]
                data[field] = value
            stream.append((curr_ms, curr_seq, data))
            self.db[key] = entry
            return curr_id

    @staticmethod
    def get_start_index(stream: list[tuple], id: str):
        if id == "-":
            return 0

        def parse_id(id):
            parts = id.split("-")
            ms = int(parts[0])
            seq = int(parts[1]) if len(parts) == 2 else 0
            return ms, seq

        target = parse_id(id)
        left = 0
        right = len(stream)

        while left < right:
            mid = left + (right - left) // 2
            mid_ms, mid_seq, _ = stream[mid]
            mid_id = (mid_ms, mid_seq)

            if mid_id < target:
                left = mid + 1
            else:
                right = mid

        return left

    @staticmethod
    def get_end_index(stream: list[tuple], id: str):
        if id == "+":
            return len(stream) - 1

        def parse_id(id):
            parts = id.split("-")
            ms = int(parts[0])
            seq = int(parts[1]) if len(parts) == 2 else float("inf")
            return ms, seq

        target = parse_id(id)
        left = 0
        right = len(stream)

        while left < right:
            mid = left + (right - left) // 2
            mid_ms, mid_seq, _ = stream[mid]
            mid_id = (mid_ms, mid_seq)

            if mid_id > target:
                right = mid
            else:
                left = mid + 1

        return left - 1

    def xrange(self, key: str, start_id: str, end_id: str, count: int | None):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        stream = entry.data
        start_index = StreamStore.get_start_index(stream, start_id)
        end_index = StreamStore.get_end_index(stream, end_id)
        if count is not None:
            end_index = min(end_index, start_index + count)
        items = []
        for i in range(start_index, end_index + 1):
            ms, seq, data = stream[i]
            data_items = []
            for field, value in data.items():
                data_items.append(field)
                data_items.append(value)
            id = f"{ms}-{seq}"
            items.append([id, data_items])
        return items

    def xrevrange(self, key: str, end_id: str, start_id: str, count: int | None):
        entry = self.db.get(key)
        if entry is None:
            return []
        self._validate_type(entry)
        stream = entry.data
        start_index = StreamStore.get_start_index(stream, start_id)
        end_index = StreamStore.get_end_index(stream, end_id)
        if count is not None:
            start_index = max(start_index, end_index - count)
        items = []
        for i in range(end_index, start_index - 1, -1):
            ms, seq, data = stream[i]
            data_items = []
            for field, value in data.items():
                data_items.append(field)
                data_items.append(value)
            id = f"{ms}-{seq}"
            items.append([id, data_items])
        return items

    def xlen(self, key: str):
        entry = self.db.get(key)
        if entry is None:
            return 0
        self._validate_type(entry)
        stream = entry.data
        return len(stream)

    async def xread(self, block: int, keys: list[str], ids: list[str]):
        keys_items = []
        for key, id in zip(keys, ids):
            entry = self.db.get(key)
            if entry is None:
                continue
            self._validate_type(entry)
            stream = entry.data
            start_index = StreamStore.get_start_index(stream, id)
            if start_index >= len(stream):
                continue
            if "-" not in id:
                id = f"{id}-0"
            ms, seq, _ = stream[start_index]
            curr_id = f"{ms}-{seq}"
            if id == curr_id:
                start_index += 1
            items = []
            for i in range(start_index, len(stream)):
                ms, seq, data = stream[i]
                data_items = []
                for field, value in data.items():
                    data_items.append(field)
                    data_items.append(value)
                id = f"{ms}-{seq}"
                items.append([id, data_items])
            if items:
                keys_items.append([key, items])

        if keys_items or block is None:
            return keys_items

        async with self._lock:
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            waiter = Waiter(future, keys)
            for key in keys:
                self._waiters[key].append(waiter)

        try:
            if block == 0:
                return await future
            return await asyncio.wait_for(future, block)
        except asyncio.TimeoutError:
            async with self._lock:
                self._deactivate_waiter(waiter)
            return None
        except asyncio.CancelledError:
            async with self._lock:
                self._deactivate_waiter(waiter)
            raise

    def _pop_active_waiter(self, key: str):
        waiters_q = self._waiters.get(key)
        while waiters_q:
            waiter = waiters_q.popleft()
            if waiter.active and not waiter.future.done():
                return waiter
        return None

    def _deactivate_waiter(self, waiter: Waiter):
        waiter.active = False
        waiter.future.cancel()

    def _finish_waiter(self, waiter: Waiter, result):
        waiter.active = False
        waiter.future.set_result(result)
