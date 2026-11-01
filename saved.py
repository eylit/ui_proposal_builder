"""Pre-made results for the sample buttons, kept in saved_results.json (made once by make_saved.py)."""
import json
from pathlib import Path

SAVED_PATH = Path(__file__).parent / "saved_results.json"


def saved_key(i: int) -> str:
    return f"sample_{i + 1}"


def load_all() -> dict:
    try:
        data = json.loads(SAVED_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def get_saved(i: int) -> dict | None:
    """The saved {"layout", "proposal", "source"} for sample i, or None if there isn't a usable one."""
    entry = load_all().get(saved_key(i))
    return entry if isinstance(entry, dict) and isinstance(entry.get("layout"), dict) else None


def save_entry(i: int, entry: dict) -> None:
    data = load_all()
    data[saved_key(i)] = entry
    SAVED_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
