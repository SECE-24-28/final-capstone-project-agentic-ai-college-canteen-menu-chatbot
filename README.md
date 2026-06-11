# Hostel Weekly Food Chatbot

A full Flask project for a hostel-style weekly food menu assistant. The chatbot answers questions like "What is Monday menu?", "What is Friday dinner?", "What is today's breakfast?", and "Show full week menu".

## Project Structure

```text
clg_canteen_AI_Chatbot/
|-- data/
|   `-- menu.csv
|-- database/
|   `-- menu.db
|-- models/
|   `-- menu_index.pkl
|-- src/
|   |-- __init__.py
|   |-- preprocess.py
|   |-- recommender.py
|   |-- train_embeddings.py
|   `-- utils.py
|-- static/
|   |-- css/style.css
|   `-- js/app.js
|-- templates/
|   `-- index.html
|-- .env
|-- .python-version
|-- app.py
|-- main.py
|-- pyproject.toml
|-- README.md
`-- requirements.txt
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --train --init-db
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Terminal Usage

```powershell
python main.py --ask "what is monday menu"
python main.py --ask "what is friday dinner"
python main.py --ask "show full week menu"
```

## Features

- Weekly hostel menu loaded from `data/menu.csv`
- Day-wise breakfast, lunch, snacks, and dinner schedule
- Answers natural questions about any day or meal
- Supports today and tomorrow queries
- Pickle-based searchable menu index in `models/menu_index.pkl`
- SQLite menu sync in `database/menu.db`
- Flask API endpoints: `/api/menu`, `/chat`, `/ask`, `/api/chat`
- Responsive frontend with quick prompts and day filtering
