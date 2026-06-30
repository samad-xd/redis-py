from resp import build_bulk_string


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
            return self.routes[command](command_parts[1:], *args, **kwargs)
        raise ValueError(f"Unknown command: {command}")


executor = Executor()


@executor("ECHO")
def get(command_parts):
    return build_bulk_string(" ".join(command_parts))
