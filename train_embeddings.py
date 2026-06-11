"""Build a tiny searchable menu index for the chatbot."""
from __future__ import annotations

import pickle
from pathlib import Path

from src.preprocess import DATA_PATH, available_items, item_text, load_menu
from src.utils import tokenize

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "models" / "menu_index.pkl"


def build_index(data_path: Path | str = DATA_PATH) -> dict:
    items = available_items(load_menu(data_path))
    documents = []
    for item in items:
        documents.append({"item": item, "tokens": tokenize(item_text(item))})
    return {"items": items, "documents": documents}


def save_index(model_path: Path | str = MODEL_PATH) -> Path:
    output_path = Path(model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file:
        pickle.dump(build_index(), file)
    return output_path


if __name__ == "__main__":
    saved_path = save_index()
    print(f"Menu index saved to {saved_path}")
