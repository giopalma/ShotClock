import sqlite3


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect("database.db")
        return cls._instance

    def get_connection(self):
        return self._instance.connection
