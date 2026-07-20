from executor import executor
from resp import build_error, parse_data, build_simple_string
from storage import Store
from exceptions import RESPParseError, WrongTypeError, ValidationError


class Client:
    def __init__(self):
        self.selected_db = 0
        self.store = Store()

    def change_db(self, db_index):
        if self.store.exists(db_index):
            self.selected_db = db_index
        else:
            raise ValidationError("selected db does not exist")

    @property
    def db(self):
        return self.store.get_db(self.selected_db)

    async def handle_incoming_messages(self, reader, writer, addr):
        while True:
            try:
                args = await parse_data(reader)

                if args is None:
                    print(f"Client {addr} connection closed")
                    break

                if not args:
                    response = build_error("ERR", "empty command")
                else:
                    if args[0] == "SELECT":
                        self.change_db(int(args[1]))
                        response = build_simple_string("OK")
                    else:
                        response = await executor.execute(self.db, args)

                if response:
                    writer.write(response.encode())
                    await writer.drain()

            except ValidationError as e:
                response = build_error("ERR", e)
                writer.write(response.encode())
                await writer.drain()

            except RESPParseError as e:
                response = build_error("ERR", f"Protocol error: {e}")
                writer.write(response.encode())
                await writer.drain()
                break

            except WrongTypeError as e:
                response = build_error("WRONGTYPE", e)
                writer.write(response.encode())
                await writer.drain()

            except Exception as e:
                print(e)
                response = build_error("SERVERERROR", str(e))
                writer.write(response.encode())
                await writer.drain()
