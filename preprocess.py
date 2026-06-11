"""Data loading and cleanup helpers for the hostel weekly menu chatbot."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "menu.csv"


def normalize_text(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def load_menu(path: Path | str = DATA_PATH) -> list[dict]:
    menu_path = Path(path)
    if not menu_path.exists():
        raise FileNotFoundError(f"Menu data not found: {menu_path}")

    entries: list[dict] = []
    with menu_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            entries.append(
                {
                    "day": row["day"].strip().title(),
                    "meal": row["meal"].strip().title(),
                    "foods": [food.strip() for food in row["foods"].split(",") if food.strip()],
                    "notes": row.get("notes", "").strip(),
                    "available": normalize_text(row.get("available", "yes")) in {"yes", "true", "1"},
                }
            )
    return entries


def available_items(entries: list[dict]) -> list[dict]:
    return [entry for entry in entries if entry.get("available", True)]


def item_text(entry: dict) -> str:
    return normalize_text(
        f"{entry['day']} {entry['meal']} {' '.join(entry['foods'])} {entry.get('notes', '')}"
    )
