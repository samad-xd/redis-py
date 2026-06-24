import socket
import threading


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
    server.settimeout(1)
    print("Server Started")

    try:
        while True:
            try:
                conn, addr = server.accept()

            except socket.timeout:
                continue

            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    except KeyboardInterrupt:
        print("Shutting down server")

    finally:
        server.close()


if __name__ == "__main__":
    main()
