"""Small helpers shared by the app, the drawn pictures and the Word export."""
import math


def num(value):
    """Return value as a finite float, or None if it isn't a usable number."""
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def is_abnormal(test: dict) -> bool:
    """True if the test's current status is one of its abnormal statuses."""
    status = str(test.get("status") or "").strip()
    return bool(status) and status in [str(x) for x in test.get("abnormal_statuses") or []]


def recommendation_text(test: dict) -> str:
    """Recommendation to show for this test: only for an abnormal status, else ''."""
    if not is_abnormal(test):
        return ""
    return str(test.get("recommendation") or "").strip() or "Doctor's recommended follow-up to appear here"
