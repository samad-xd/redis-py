from exceptions import RESPParseError, ValidationError, WrongTypeError
from executor import executor
from resp import build_error, parse_incoming_data
from storage import Store


class Client:
    def __init__(self):
        self.selected_db = 0
        self.store = Store()
        self._subscribed = False

    def change_db(self, db_index):
        if self.store.exists(db_index):
            self.selected_db = db_index
        else:
            raise ValidationError("selected db does not exist")

    async def write_response(self, response):
        self.writer.write(response.encode())
        await self.writer.drain()

    @property
    def db(self):
        return self.store.get_db(self.selected_db)

    async def handle_incoming_messages(self, reader, writer, addr):
        self.reader = reader
        self.writer = writer

        while True:
            try:
                args = await parse_incoming_data(reader)

                if args is None:
                    print(f"Client {addr} connection closed")
                    break

                if not args:
                    response = build_error("ERR", "empty command")

                await executor.execute(self, args)

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

            except Exception as e:  # noqa: BLE001
                print(e)
                response = build_error("SERVERERROR", str(e))
                writer.write(response.encode())
                await writer.drain()
