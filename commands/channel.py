from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_integer


@executor("SUBSCRIBE")
async def subscribe(client: Client, command_parts: list[str]):
    if len(command_parts) < 2:
        raise ValidationError("wrong number of arguments for command")

    channel_names = command_parts[1:]

    await client.channels.subscribe(client, channel_names)


@executor("UNSUBSCRIBE")
async def unsubscribe(client: Client, command_parts: list[str]):
    if not command_parts:
        raise ValidationError("wrong number of arguments for command")

    channel_names = []
    if len(command_parts) > 1:
        channel_names = command_parts[1:]

    await client.channels.unsubscribe(client, channel_names)


@executor("PUBLISH")
async def publish(client: Client, command_parts: list[str]):
    if len(command_parts) != 3:
        raise ValidationError("wrong number of arguments for command")

    channel_name = command_parts[1]
    message = command_parts[2]

    published_count = await client.channels.publish(channel_name, message)

    response = build_integer(published_count)
    await client.write_response(response)
