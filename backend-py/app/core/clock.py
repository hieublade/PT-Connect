from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

try:
    VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:
    VN_TZ = timezone(timedelta(hours=7))


def now_local() -> datetime:
    """Return current naive datetime in Vietnam local time."""
    return datetime.now(VN_TZ).replace(tzinfo=None)


def today_local() -> date:
    """Return current date in Vietnam local time."""
    return datetime.now(VN_TZ).date()
