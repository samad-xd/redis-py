from itertools import islice

from resp import build_bulk_string, build_simple_string


class Executor:
    def __init__(self):
        self.routes = {}

    def __call__(self, route_name):
        def decorator(func):
            self.routes[route_name] = func
            return func

        return decorator

    async def execute(self, client, command_parts, *args, **kwargs):
        command = command_parts[0].upper()

        if command in self.routes:
            func = self.routes[command]
            await func(client, command_parts, *args, **kwargs)
        else:
            raise ValueError(f"Unknown command: {command}")


executor = Executor()


@executor("PING")
async def ping(client, *args):
    response = build_simple_string("PONG")
    await client.write_response(response)


@executor("ECHO")
async def echo(client, command_parts: list[str]):
    response = build_bulk_string(" ".join(islice(command_parts, 1, None)))
    await client.write_response(response)
