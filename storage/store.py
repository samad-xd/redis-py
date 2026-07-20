from .database import Database


class Store:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_count=16):
        if hasattr(self, "_initialized"):
            return
        self.dbs: list[Database] = [Database() for _ in range(db_count)]
        self._initialized = True

    def get_db(self, index):
        return self.dbs[index]

    def clear_db(self, index):
        self.dbs[index].clear_db()

    def size(self, index):
        return self.dbs[index].db_size()

    def exists(self, index):
        return index >= 0 and index < len(self.dbs)
