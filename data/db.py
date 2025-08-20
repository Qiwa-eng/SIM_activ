import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_FILE = Path(__file__).with_name("db.json")

DEFAULT_DB: Dict[str, Any] = {
    "users": {},
    "settings": {
        "topup_enabled": True,
        "disabled_operators": [],
        "rate": 0.0,
    },
    "invoices": {},
    "next_purchase_id": 1,
}

def load_db() -> Dict[str, Any]:
    if not DB_FILE.exists():
        return json.loads(json.dumps(DEFAULT_DB))
    with DB_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    for k, v in DEFAULT_DB.items():
        if k not in data:
            data[k] = v if not isinstance(v, dict) else json.loads(json.dumps(v))
    return data

def save_db(data: Dict[str, Any]) -> None:
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_user(user_id: int) -> Dict[str, Any]:
    data = load_db()
    user = data["users"].setdefault(
        str(user_id), {"balance": 0.0, "banned": False, "purchases": []}
    )
    save_db(data)
    return user

def get_balance(user_id: int) -> float:
    data = load_db()
    return (
        data["users"].get(str(user_id), {}).get("balance", 0.0)
    )

def add_balance(user_id: int, amount: float) -> None:
    data = load_db()
    user = data["users"].setdefault(
        str(user_id), {"balance": 0.0, "banned": False, "purchases": []}
    )
    user["balance"] += amount
    save_db(data)

def deduct_balance(user_id: int, amount: float) -> None:
    data = load_db()
    user = data["users"].setdefault(
        str(user_id), {"balance": 0.0, "banned": False, "purchases": []}
    )
    user["balance"] = max(0.0, user["balance"] - amount)
    save_db(data)

def set_ban(user_id: int, banned: bool) -> None:
    data = load_db()
    user = data["users"].setdefault(
        str(user_id), {"balance": 0.0, "banned": False, "purchases": []}
    )
    user["banned"] = banned
    save_db(data)

def is_banned(user_id: int) -> bool:
    data = load_db()
    return data["users"].get(str(user_id), {}).get("banned", False)

def get_all_users() -> List[int]:
    data = load_db()
    return [int(uid) for uid in data["users"].keys()]

def add_purchase(user_id: int, info: Dict[str, Any]) -> int:
    data = load_db()
    user = data["users"].setdefault(
        str(user_id), {"balance": 0.0, "banned": False, "purchases": []}
    )
    purchase_id = data.get("next_purchase_id", 1)
    info.update({"id": purchase_id, "status": info.get("status", "pending")})
    user["purchases"].append(info)
    data["next_purchase_id"] = purchase_id + 1
    save_db(data)
    return purchase_id

def update_purchase_status(user_id: int, purchase_id: int, status: str) -> None:
    data = load_db()
    user = data["users"].get(str(user_id))
    if not user:
        return
    for p in user.get("purchases", []):
        if p.get("id") == purchase_id:
            p["status"] = status
            break
    save_db(data)

def get_all_purchases() -> List[Dict[str, Any]]:
    data = load_db()
    res = []
    for uid, udata in data["users"].items():
        for p in udata.get("purchases", []):
            item = p.copy()
            item["user_id"] = int(uid)
            res.append(item)
    return res

def get_purchase_by_id(purchase_id: int) -> Optional[Dict[str, Any]]:
    data = load_db()
    for uid, udata in data["users"].items():
        for p in udata.get("purchases", []):
            if p.get("id") == purchase_id:
                item = p.copy()
                item["user_id"] = int(uid)
                return item
    return None


def get_user_purchases(user_id: int) -> List[Dict[str, Any]]:
    data = load_db()
    user = data["users"].get(str(user_id), {})
    return user.get("purchases", [])

def add_invoice(invoice_id: int, info: Dict[str, Any]) -> None:
    data = load_db()
    data["invoices"][str(invoice_id)] = info
    save_db(data)

def get_invoice(invoice_id: int) -> Optional[Dict[str, Any]]:
    data = load_db()
    return data["invoices"].get(str(invoice_id))

def remove_invoice(invoice_id: int) -> None:
    data = load_db()
    data["invoices"].pop(str(invoice_id), None)
    save_db(data)

def is_topup_enabled() -> bool:
    data = load_db()
    return data["settings"].get("topup_enabled", True)

def set_topup_enabled(value: bool) -> None:
    data = load_db()
    data["settings"]["topup_enabled"] = value
    save_db(data)


def get_rate() -> float:
    data = load_db()
    return data["settings"].get("rate", 0.0)


def set_rate(value: float) -> None:
    data = load_db()
    data["settings"]["rate"] = value
    save_db(data)

def disable_operator(operator: str) -> None:
    data = load_db()
    ops = data["settings"].setdefault("disabled_operators", [])
    if operator not in ops:
        ops.append(operator)
    save_db(data)

def enable_operator(operator: str) -> None:
    data = load_db()
    ops = data["settings"].setdefault("disabled_operators", [])
    if operator in ops:
        ops.remove(operator)
    save_db(data)

def is_operator_enabled(operator: str) -> bool:
    data = load_db()
    ops = data["settings"].get("disabled_operators", [])
    return operator not in ops
