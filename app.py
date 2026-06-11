"""Flask web app for the Hostel Weekly Food Chatbot."""
from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from src.recommender import WeeklyMenuRecommender
from src.utils import init_database

app = Flask(__name__)
recommender = WeeklyMenuRecommender()
init_database(recommender.menu())


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/menu")
def api_menu():
    return jsonify({"menu": recommender.menu()})


@app.post("/chat")
@app.post("/ask")
@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = payload.get("message") or payload.get("query") or payload.get("question") or ""
    return jsonify({"response": recommender.answer(question)})


if __name__ == "__main__":
    app.run(debug=True)
