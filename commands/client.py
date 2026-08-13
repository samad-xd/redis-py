from itertools import islice

from client import Client
from exceptions import ValidationError
from executor import executor
from resp import build_bulk_string, build_simple_string


@executor("PING")
async def ping(client, *args):
    response = build_simple_string("PONG")
    await client.write_response(response)


@executor("ECHO")
async def echo(client, command_parts: list[str]):
    response = build_bulk_string(" ".join(islice(command_parts, 1, None)))
    await client.write_response(response)


@executor("SELECT")
async def select(client: Client, command_parts: list[str]):
    if len(command_parts) != 2:
        raise ValidationError("wrong number of arguments for command")

    try:
        db_index = int(command_parts[1])
    except ValueError:
        raise ValidationError("value is not an integer or out of range")

    client.change_db(db_index)

    response = build_simple_string("OK")
    await client.write_response(response)
