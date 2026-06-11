"""Response engine for hostel weekly food schedule questions."""
from __future__ import annotations

import pickle
from datetime import datetime
from pathlib import Path

from src.preprocess import available_items
from src.train_embeddings import MODEL_PATH, build_index
from src.utils import format_entry, group_by_day, tokenize

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEALS = ["Breakfast", "Lunch", "Snacks", "Dinner"]
MEAL_ALIASES = {
    "breakfast": "Breakfast",
    "morning": "Breakfast",
    "lunch": "Lunch",
    "afternoon": "Lunch",
    "snack": "Snacks",
    "snacks": "Snacks",
    "evening": "Snacks",
    "tea": "Snacks",
    "dinner": "Dinner",
    "night": "Dinner",
}


def load_index(model_path: Path | str = MODEL_PATH) -> dict:
    path = Path(model_path)
    if path.exists():
        with path.open("rb") as file:
            return pickle.load(file)
    return build_index()


class WeeklyMenuRecommender:
    def __init__(self) -> None:
        self.index = load_index()
        self.items = available_items(self.index["items"])
        self.food_names = self._food_names()

    def menu(self) -> list[dict]:
        return self.items

    def answer(self, question: str) -> str:
        query = question.strip()
        if not query:
            return "Ask me about any day in the hostel weekly menu, like: What is Monday menu?"

        text = query.lower()
        day = self._day_from_text(text)
        meal = self._meal_from_text(text)

        if "today" in text:
            day = datetime.now().strftime("%A")

        if "tomorrow" in text:
            today_index = DAYS.index(datetime.now().strftime("%A"))
            day = DAYS[(today_index + 1) % len(DAYS)]

        food = self._food_from_text(text)
        if food:
            if day:
                return self._answer_food_availability(food, day)
            return self._answer_food_days(food)

        if day and meal:
            matches = [entry for entry in self.items if entry["day"] == day and entry["meal"] == meal]
            if matches:
                return self._format_day(day, matches, title=f"{day} {meal} menu:")
            return f"I do not have {meal.lower()} details for {day}."

        if day:
            matches = [entry for entry in self.items if entry["day"] == day]
            return self._format_day(day, matches, title=f"{day} hostel menu:")

        if meal:
            matches = [entry for entry in self.items if entry["meal"] == meal]
            return self._format_meal_across_week(meal, matches)

        if any(word in text for word in ["week", "weekly", "all menu", "full menu", "whole week"]):
            return self._format_week()

        matches = self._semantic_search(text)
        if matches:
            return self._format_search(matches)

        return "I can tell hostel food availability by day and meal. Try asking: Monday menu, Friday dinner, today breakfast, or full week menu."

    def _day_from_text(self, text: str) -> str | None:
        for day in DAYS:
            if day.lower() in text:
                return day
        return None

    def _meal_from_text(self, text: str) -> str | None:
        for key, value in MEAL_ALIASES.items():
            if key in text:
                return value
        return None

    def _food_names(self) -> list[str]:
        names = {food.strip().lower() for entry in self.items for food in entry["foods"]}
        return sorted(names, key=len, reverse=True)

    def _food_from_text(self, text: str) -> str | None:
        for food in self.food_names:
            if food in text:
                return food
        query_tokens = tokenize(text)
        for food in self.food_names:
            if query_tokens & tokenize(food):
                return food
        return None

    def _entries_with_food(self, food: str, day: str | None = None) -> list[dict]:
        matches = []
        for entry in self.items:
            if day and entry["day"] != day:
                continue
            if any(food == item.lower() for item in entry["foods"]):
                matches.append(entry)
        return matches

    def _answer_food_availability(self, food: str, day: str) -> str:
        matches = self._entries_with_food(food, day)
        display_food = food.title()
        if matches:
            meals = self._join_words([entry["meal"] for entry in matches])
            return f"Yes, {display_food} is available on {day} for {meals}."

        other_entries = self._entries_with_food(food)
        if not other_entries:
            return f"{display_food} is not available in the weekly hostel menu."

        days = sorted({entry["day"] for entry in other_entries}, key=DAYS.index)
        return f"No, {display_food} is not available on {day}. It is available on {self._join_words(days)}."

    def _answer_food_days(self, food: str) -> str:
        matches = self._entries_with_food(food)
        display_food = food.title()
        if not matches:
            return f"{display_food} is not available in the weekly hostel menu."

        lines = [f"{display_food} is available on:"]
        for entry in sorted(matches, key=lambda item: (DAYS.index(item["day"]), MEALS.index(item["meal"]))):
            lines.append(f"{entry['day']} {entry['meal']}")
        return "\n".join(lines)

    def _join_words(self, words: list[str]) -> str:
        if len(words) <= 1:
            return "".join(words)
        return f"{', '.join(words[:-1])} and {words[-1]}"

    def _semantic_search(self, text: str) -> list[dict]:
        query_tokens = tokenize(text)
        scored = []
        for document in self.index["documents"]:
            score = len(query_tokens & document["tokens"])
            if score:
                scored.append((score, document["item"]))
        scored.sort(key=lambda pair: (-pair[0], DAYS.index(pair[1]["day"]), MEALS.index(pair[1]["meal"])))
        return [item for _, item in scored[:6]]

    def _format_day(self, day: str, entries: list[dict], title: str) -> str:
        if not entries:
            return f"No hostel menu is available for {day}."
        ordered = sorted(entries, key=lambda entry: MEALS.index(entry["meal"]))
        lines = [title]
        lines.extend(format_entry(entry) for entry in ordered)
        return "\n".join(lines)

    def _format_meal_across_week(self, meal: str, entries: list[dict]) -> str:
        if not entries:
            return f"No {meal.lower()} menu is available."
        ordered = sorted(entries, key=lambda entry: DAYS.index(entry["day"]))
        lines = [f"{meal} menu for the whole week:"]
        lines.extend(f"{entry['day']}: {', '.join(entry['foods'])}" for entry in ordered)
        return "\n".join(lines)

    def _format_week(self) -> str:
        grouped = group_by_day(self.items)
        lines = ["Full weekly hostel menu:"]
        for day in DAYS:
            entries = grouped.get(day, [])
            if entries:
                lines.append("")
                lines.append(day)
                lines.extend(format_entry(entry) for entry in sorted(entries, key=lambda entry: MEALS.index(entry["meal"])))
        return "\n".join(lines)

    def _format_search(self, entries: list[dict]) -> str:
        lines = ["I found these matching hostel menu entries:"]
        for entry in entries:
            lines.append(f"{entry['day']} {format_entry(entry)}")
        return "\n".join(lines)
