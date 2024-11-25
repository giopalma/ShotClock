import sqlite3


class DatabaseConnection:
    _instance = None

    # Viene utilizzato __new__ perchè è un singleton
    def __new__(cls, debug=False):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if debug:
                cls._instance.connection = sqlite3.connect(
                    ":memory:",
                )
            else:
                cls._instance.connection = sqlite3.connect("database.db")
        return cls._instance

    def get_connection(self):
        return self._instance.connection
