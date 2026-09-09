from __future__ import annotations

import asyncio
import threading
from typing import TYPE_CHECKING

from resp import build_array

if TYPE_CHECKING:
    from client import Client  # noqa: TC004


class Channels:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self.channels: dict[str, set] = {}
        self._initialized = True

    async def subscribe(self, client: Client, channel_names: list[str]):
        writer: asyncio.StreamWriter = client.writer

        for channel_name in channel_names:
            if channel_name not in self.channels:
                self.channels[channel_name] = set()

            channel = self.channels.get(channel_name)
            channel.add(writer)
            client.subscriptions.add(channel_name)
            response = build_array(
                ["subscribe", channel_name, len(client.subscriptions)]
            )
            writer.write(response.encode())

        await writer.drain()

    async def unsubscribe(self, client: Client, channel_names: list[str]):
        writer: asyncio.StreamWriter = client.writer

        if channel_names:
            for channel_name in channel_names:
                if channel_name in self.channels:
                    channel = self.channels.get(channel_name)
                    channel.discard(writer)
                    client.subscriptions.discard(channel_name)

                    if not channel:
                        self.channels.pop(channel_name)

                response = build_array(
                    ["unsubscribe", channel_name, len(client.subscriptions)]
                )
                writer.write(response.encode())

        else:
            for channel_name in client.subscriptions:
                channel = self.channels.get(channel_name)
                channel.discard(writer)

                response = build_array(
                    ["unsubscribe", channel_name, len(client.subscriptions)]
                )
                writer.write(response.encode())

        await writer.drain()

    async def publish(self, channel_name: str, message: str):
        channel: set[asyncio.StreamWriter] = self.channels.get(channel_name)
        encoded_response = build_array(["message", channel_name, message]).encode()

        published_count = 0

        if channel is None:
            return published_count

        dead_writers = []
        for sub_writer in channel:
            try:
                sub_writer.write(encoded_response)

                if sub_writer.is_closing():
                    dead_writers.append(sub_writer)
                    continue

                asyncio.create_task(sub_writer.drain())
                published_count += 1
            except (ConnectionResetError, OSError, BrokenPipeError):
                dead_writers.append(sub_writer)

        for dead_writer in dead_writers:
            channel.discard(dead_writer)

            try:
                dead_writer.close()
            except Exception:  # noqa: BLE001, S110
                pass

        if not channel:
            self.channels.pop(channel_name)

        return published_count
