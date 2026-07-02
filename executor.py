from resp import build_bulk_string, build_simple_string


class Executor:
    def __init__(self):
        self.routes = {}

    def __call__(self, route_name):
        def decorator(func):
            self.routes[route_name] = func
            return func

        return decorator

    def execute(self, command_parts, *args, **kwargs):
        command = command_parts[0].upper()
        if command in self.routes:
            func = self.routes[command]
            return func(command_parts[1:], *args, **kwargs)
        raise ValueError(f"Unknown command: {command}")


executor = Executor()


@executor("PING")
def ping(*args, **kwargs):
    return build_simple_string("PONG")


@executor("ECHO")
def echo(command_parts):
    return build_bulk_string(" ".join(command_parts))
