import json
from pathlib import Path
from typing import Any, Dict

DB_FILE = Path("data/db.json")


def read_db() -> Dict[str, Any]:
    """Read data from the JSON database."""
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return {}


def write_db(data: Dict[str, Any]) -> None:
    """Write data to the JSON database."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
