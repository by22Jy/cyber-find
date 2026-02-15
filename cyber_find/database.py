import os
import sqlite3


class DatabaseManager:
    def __init__(self, config: dict):
        self.config = config
        self.conn = None
        self.init_database()

    def init_database(self):
        db_path = self.config["database"]["sqlite_path"]

        if db_path:
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.getcwd(), db_path)

            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        else:
            db_path = os.path.join(os.getcwd(), "cyberfind.db")

        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                site_name TEXT NOT NULL,
                url TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                found BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                UNIQUE(username, site_name)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                searches_count INTEGER DEFAULT 0,
                accounts_found INTEGER DEFAULT 0,
                total_time REAL DEFAULT 0
            )
        """
        )

        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
