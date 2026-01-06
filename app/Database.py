import sqlite3
from pydantic import TypeAdapter

from models.geocode import SimpleLocation


class Database:
    def __init__(self, db_name="app.sqlite"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def setup_db(self):
        with self.connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY
                );
            """)

            con.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    username TEXT PRIMARY KEY,
                    location_json TEXT NOT NULL,
                    FOREIGN KEY (username) REFERENCES users(username)
                );
            """)
    def save_location(self, username: str, location: SimpleLocation):
        location_json = location.model_dump_json()  # Pydantic → JSON string

        with self.connect() as con:
            con.execute(
                "INSERT OR IGNORE INTO users (username) VALUES (?)",
                (username,)
            )

            con.execute(
                "INSERT OR REPLACE INTO locations (username, location_json) VALUES (?, ?)",
                (username, location_json)
            )

    def get_location(self, username: str) -> SimpleLocation | None:
        adapter = TypeAdapter(SimpleLocation)
        with self.connect() as con:
            cur = con.execute(
                "SELECT location_json FROM locations WHERE username = ?",
                (username,)
            )

            row = cur.fetchone()
        if row is None:
            return None

        return adapter.validate_json(row[0])
