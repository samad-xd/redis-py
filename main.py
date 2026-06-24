import asyncio


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connected to {addr}")

    try:
        while True:
            data = await reader.read(1024)

            if not data:
                print(f"Client {addr} connection closed")
                break

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
