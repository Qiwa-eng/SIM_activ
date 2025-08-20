import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

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


def _ensure_db() -> Dict[str, Any]:
    """Return DB content ensuring required top-level keys exist."""
    data = read_db()
    data.setdefault("ads", [])
    data.setdefault("reviews", [])
    return data


def add_ad(
    user_id: int,
    title: str,
    text: str,
    tags: List[str],
    photo: str | None,
    user_name: str | None,
) -> None:
    """Append a new advertisement with extended fields for the given user."""

    data = _ensure_db()
    ads = data["ads"]
    ads.append(
        {
            "id": len(ads) + 1,
            "user_id": user_id,
            "user_name": user_name,
            "title": title,
            "text": text,
            "tags": tags,
            "photo": photo,
        }
    )
    write_db(data)


def get_ads() -> List[Dict[str, Any]]:
    """Return list of all advertisements."""
    return read_db().get("ads", [])


def get_user_ads(user_id: int) -> List[Dict[str, Any]]:
    """Return ads posted by the specified user."""
    return [ad for ad in get_ads() if ad["user_id"] == user_id]


def get_ad(ad_id: int) -> Dict[str, Any] | None:
    """Return single ad by its identifier."""
    for ad in get_ads():
        if ad["id"] == ad_id:
            return ad
    return None


def search_ads(keyword: str) -> List[Dict[str, Any]]:
    """Return ads whose text, title or tags contain the keyword."""
    keyword = keyword.lower()
    result: List[Dict[str, Any]] = []
    for ad in get_ads():
        in_text = keyword in ad["text"].lower()
        in_title = keyword in ad["title"].lower()
        in_tags = any(keyword in tag.lower() for tag in ad["tags"])
        if in_text or in_title or in_tags:
            result.append(ad)
    return result


def update_ad(ad_id: int, fields: Dict[str, Any]) -> None:
    """Update advertisement fields by identifier."""
    data = _ensure_db()
    for ad in data["ads"]:
        if ad["id"] == ad_id:
            ad.update(fields)
            break
    write_db(data)


def add_review(from_user: int, to_user: int, text: str) -> None:
    """Store a new review for a user."""
    data = _ensure_db()
    data["reviews"].append({"from": from_user, "to": to_user, "text": text})
    write_db(data)


def get_user_reputation(user_id: int) -> int:
    """Return number of reviews received by the user."""
    data = read_db()
    return sum(1 for r in data.get("reviews", []) if r["to"] == user_id)


def get_top_users(limit: int = 3) -> List[Tuple[int, int]]:
    """Return top users by reputation as list of tuples (user_id, score)."""
    data = read_db()
    counts = Counter(r["to"] for r in data.get("reviews", []))
    return counts.most_common(limit)
