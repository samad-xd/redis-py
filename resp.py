from exceptions import RESPParseError


async def parse_data(reader):
    line = await reader.readline()

    if not line:
        return None

    if not line.startswith(b"*"):
        raise RESPParseError("Expected RESP array starting with '*'")

    if not line.endswith(b"\r\n"):
        raise RESPParseError("Invalid RESP line ending")

    try:
        length = int(line[1:-2])
    except ValueError:
        raise RESPParseError("Invalid array length")

    args = []

    for _ in range(length):
        line = await reader.readline()

        if not line.startswith(b"$"):
            raise RESPParseError("Expected RESP bulk string starting with '$'")

        if not line.endswith(b"\r\n"):
            raise RESPParseError("Invalid RESP line ending")

        try:
            string_length = int(line[1:-1])
        except ValueError:
            raise RESPParseError("Invalid bulk string length")

        arg = await reader.readexactly(string_length)

        crlf = await reader.readexactly(2)

        if crlf != b"\r\n":
            raise RESPParseError("Bulk String missing CRLF terminator")

        args.append(arg.decode())

    return args


def build_simple_string(string):
    return f"+{string}\r\n"


def build_integer(num):
    return f":{num}\r\n"


def build_error(kind, error_message):
    return f"-{kind} {error_message}\r\n"


def build_bulk_string(string):
    if string is None:
        return "$-1\r\n"
    return f"${len(string)}\r\n{string}\r\n"


def build_array(data):
    if isinstance(data, list):
        return f"*{len(data)}\r\n{''.join(build_array(item) for item in data)}"
    elif isinstance(data, int):
        return build_integer(data)
    return build_bulk_string(data)
