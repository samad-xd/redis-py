import asyncio
from resp import parse_data, build_error, RESPParseError, build_simple_string


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connected to {addr}")

    try:
        while True:
            try:
                args = await parse_data(reader)

                if args is None:
                    print(f"Client {addr} connection closed")
                    break

                if not args:
                    response = build_error("ERR", "empty command")
                else:
                    response = build_simple_string("OK")

                writer.write(response.encode())
                await writer.drain()

            except RESPParseError as e:
                response = build_error("ERR", f"Protocol error: {e}")
                writer.write(response.encode())
                await writer.drain()
                break

            except Exception as e:
                response = build_error("ERR", e)
                writer.write(response.encode())
                await writer.drain()

    except ConnectionResetError:
        print(f"Connection {addr} forcibly disconnected")

    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(
        client_connected_cb=handle_client, host="localhost", port=6379
    )
    print("Server Started")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down server")
