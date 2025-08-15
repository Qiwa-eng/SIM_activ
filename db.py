import json
import os

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_balance(user_id: int) -> float:
    data = load_db()
    return data.get(str(user_id), {}).get("balance", 0.0)

def add_balance(user_id: int, amount: float) -> None:
    data = load_db()
    user = data.setdefault(str(user_id), {"balance": 0.0})
    user["balance"] += amount
    save_db(data)

def deduct_balance(user_id: int, amount: float) -> None:
    data = load_db()
    user = data.setdefault(str(user_id), {"balance": 0.0})
    user["balance"] = max(0.0, user["balance"] - amount)
    save_db(data)
