"""Command-line entry point for training and chatting."""
from __future__ import annotations

import argparse

from src.recommender import WeeklyMenuRecommender
from src.train_embeddings import save_index
from src.utils import init_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Hostel Weekly Food Chatbot")
    parser.add_argument("--train", action="store_true", help="rebuild the menu search index")
    parser.add_argument("--init-db", action="store_true", help="sync CSV menu into SQLite database")
    parser.add_argument("--ask", help="ask one question from the terminal")
    args = parser.parse_args()

    if args.train:
        print(f"Saved index: {save_index()}")

    bot = WeeklyMenuRecommender()

    if args.init_db:
        print(f"Initialized database: {init_database(bot.menu())}")

    if args.ask:
        print(bot.answer(args.ask))
        return

    if not any([args.train, args.init_db]):
        print('Run `python app.py` for the web app, or use `python main.py --ask "what is monday menu"`.')


if __name__ == "__main__":
    main()
