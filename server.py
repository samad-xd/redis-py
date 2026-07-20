import asyncio

import commands  # noqa -> importing this to register the commands
from arg_parser import parse_args
from client import Client
from storage import Store


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connected to {addr}")

    client_obj = Client()

    try:
        await client_obj.handle_incoming_messages(reader, writer, addr)

    except ConnectionResetError:
        print(f"Connection {addr} forcibly disconnected")

    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    args = parse_args()

    Store(db_count=args.db_count)

    server = await asyncio.start_server(
        client_connected_cb=handle_client, host=args.host, port=args.port
    )
    print(f"Server Started on {args.host}:{args.port}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down server")
