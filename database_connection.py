import mysql.connector
from config import DB_CONFIG

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return self.connection
        except mysql.connector.Error as err:
            raise Exception(f"Database connection failed: {err}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.is_connected():
            self.connection.close()