import socket


def handle_client(conn, addr):
    print(f"Connected to {addr}")

    try:
        while True:
            data = conn.recv(1024)

            if not data:
                print(f"Client {addr} connection closed")
                break

    except ConnectionResetError:
        print(f"Connection {addr} forcibly disconnected")

    finally:
        conn.close()


def main():
    server = socket.create_server(address=("localhost", 6379))
    print("Server Started")

    try:
        conn, addr = server.accept()
        handle_client(conn, addr)

    except KeyboardInterrupt:
        print("Shutting down server")

    finally:
        server.close()


if __name__ == "__main__":
    main()
