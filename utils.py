"""Shared utility functions for the hostel weekly menu chatbot."""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "database" / "menu.db"
STOP_WORDS = {
    "a", "an", "and", "are", "available", "can", "for", "give", "hostel", "i",
    "is", "me", "menu", "of", "on", "please", "provide", "served", "show",
    "the", "they", "to", "today", "what", "with", "you",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if word not in STOP_WORDS and len(word) > 1}


def format_entry(entry: dict) -> str:
    foods = ", ".join(entry["foods"])
    return f"{entry['meal']}: {foods}"


def group_by_day(entries: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for entry in entries:
        grouped.setdefault(entry["day"], []).append(entry)
    return grouped


def init_database(entries: list[dict], db_path: Path | str = DB_PATH) -> Path:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE IF EXISTS menu_items")
        connection.execute("DROP TABLE IF EXISTS weekly_menu")
        connection.execute(
            """
            CREATE TABLE weekly_menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                meal TEXT NOT NULL,
                foods TEXT NOT NULL,
                notes TEXT NOT NULL,
                available INTEGER NOT NULL
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO weekly_menu
            (day, meal, foods, notes, available)
            VALUES (:day, :meal, :foods_text, :notes, :available)
            """,
            [
                {
                    **entry,
                    "foods_text": ", ".join(entry["foods"]),
                    "available": int(entry.get("available", True)),
                }
                for entry in entries
            ],
        )
    return path
