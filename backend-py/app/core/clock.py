from datetime import date, datetime
from zoneinfo import ZoneInfo

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def now_local() -> datetime:
    """Return current naive datetime in Vietnam local time."""
    return datetime.now(VN_TZ).replace(tzinfo=None)


def today_local() -> date:
    """Return current date in Vietnam local time."""
    return datetime.now(VN_TZ).date()
