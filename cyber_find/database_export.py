"""
Database Export Module - Сохранение результатов в базу данных
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import SearchResult


class DatabaseExporter:
    """Экспорт результатов поиска в SQLite БД"""

    def __init__(self, db_path: str = "cyberfind_results.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация БД со схемой"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mode TEXT,
                    total_results INTEGER,
                    search_time REAL
                )
                """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER NOT NULL,
                    site_name TEXT NOT NULL,
                    profile_url TEXT,
                    status_code INTEGER,
                    found BOOLEAN,
                    confidence REAL,
                    metadata JSON,
                    FOREIGN KEY(search_id) REFERENCES searches(id)
                )
                """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    first_search TIMESTAMP,
                    last_search TIMESTAMP,
                    total_searches INTEGER DEFAULT 0,
                    total_accounts_found INTEGER DEFAULT 0
                )
                """)

            conn.commit()

    def save_search(
        self,
        username: str,
        results: List[SearchResult],
        mode: str = "standard",
        search_time: float = 0.0,
    ) -> Optional[int]:
        """Сохранить результаты поиска в БД"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Обновить/создать запись пользователя
            cursor.execute(
                """
                INSERT INTO users (username, first_search, last_search, total_searches)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(username) DO UPDATE SET
                    last_search = CURRENT_TIMESTAMP,
                    total_searches = total_searches + 1
                """,
                (username, datetime.now(), datetime.now()),
            )

            # Сохранить поиск
            cursor.execute(
                """
                INSERT INTO searches (username, mode, total_results, search_time)
                VALUES (?, ?, ?, ?)
                """,
                (username, mode, len(results), search_time),
            )
            search_id = cursor.lastrowid

            # Сохранить результаты
            found_count = 0
            for result in results:
                cursor.execute(
                    """
                    INSERT INTO results (search_id, site_name, profile_url, status_code, found, confidence, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        search_id,
                        result.site,
                        result.url,
                        result.status_code,
                        result.found,
                        result.confidence,
                        json.dumps(result.metadata or {}),
                    ),
                )
                if result.found:
                    found_count += 1

            # Обновить счётчик найденных аккаунтов
            cursor.execute(
                """
                UPDATE users SET total_accounts_found = total_accounts_found + ?
                WHERE username = ?
                """,
                (found_count, username),
            )

            conn.commit()
            return search_id

    def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Получить профиль пользователя со всей статистикой"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,),
            )
            user = cursor.fetchone()

            if not user:
                return None

            cursor.execute(
                "SELECT * FROM searches WHERE username = ? ORDER BY search_date DESC",
                (username,),
            )
            searches = cursor.fetchall()

            return {
                "username": user["username"],
                "first_search": user["first_search"],
                "last_search": user["last_search"],
                "total_searches": user["total_searches"],
                "total_accounts_found": user["total_accounts_found"],
                "searches": [dict(s) for s in searches],
            }

    def get_search_results(self, search_id: int) -> List[Dict[str, Any]]:
        """Получить результаты конкретного поиска"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM results WHERE search_id = ?
                ORDER BY found DESC, confidence DESC
                """,
                (search_id,),
            )
            results = cursor.fetchall()

            return [
                {
                    **dict(r),
                    "metadata": json.loads(r["metadata"]),
                }
                for r in results
            ]

    def export_to_csv(self, username: str, output_file: str):
        """Экспортировать результаты в CSV"""
        import csv

        profile = self.get_user_profile(username)
        if not profile:
            raise ValueError(f"User {username} not found")

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "site_name",
                    "profile_url",
                    "status_code",
                    "found",
                    "confidence",
                ],
            )
            writer.writeheader()

            for search in profile["searches"]:
                results = self.get_search_results(search["id"])
                for result in results:
                    writer.writerow(
                        {
                            "site_name": result["site_name"],
                            "profile_url": result["profile_url"],
                            "status_code": result["status_code"],
                            "found": result["found"],
                            "confidence": result["confidence"],
                        }
                    )
