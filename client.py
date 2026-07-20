import shlex
import socket
import threading
import time


def build_RESP_array(command):
    parts = shlex.split(command)
    return f"*{len(parts)}\r\n{'\r\n'.join([f'${len(part)}\r\n{part}' for part in parts])}\r\n"


def send_command(client, command):
    client.send(build_RESP_array(command).encode())


def receive_data(client):
    return client.recv(1024)


def take_commands(client):
    while True:
        command = input("").strip()
        send_command(client, command)


def print_responses(client):
    while True:
        try:
            data = client.recv(1024)
            if not data:
                print("Connection closed by server.")
                break
            print(data)
        except ConnectionResetError:
            print("Connection reset.")
            break


def main():
    try:
        client = socket.create_connection(("localhost", 6379))

        threading.Thread(target=take_commands, args=(client,), daemon=True).start()
        threading.Thread(target=print_responses, args=(client,), daemon=True).start()

        while True:
            time.sleep(1)

    except ConnectionRefusedError:
        print("Could not connect to the server.")


if __name__ == "__main__":
    main()
