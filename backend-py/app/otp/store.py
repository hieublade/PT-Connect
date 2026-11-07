import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.clock import now_local


@dataclass
class OtpEntry:
    code: str
    expires_at: datetime

    def is_expired(self) -> bool:
        return now_local() > self.expires_at


class InMemoryOtpStore:
    DEFAULT_EXPIRY_MINUTES = 30

    def __init__(self):
        self._storage: dict[int, OtpEntry] = {}
        self._lock = threading.Lock()

    def generate_otp(self, booking_id: int, expiry_minutes: int = DEFAULT_EXPIRY_MINUTES) -> str:
        code = str(secrets.randbelow(900000) + 100000)
        expires_at = now_local() + timedelta(minutes=expiry_minutes)
        with self._lock:
            self._storage[booking_id] = OtpEntry(code=code, expires_at=expires_at)
        return code

    def get_active_otp(self, booking_id: int) -> tuple[str, datetime] | None:
        with self._lock:
            entry = self._storage.get(booking_id)
            if entry is not None:
                if not entry.is_expired():
                    return entry.code, entry.expires_at
                del self._storage[booking_id]
        return None

    def validate_otp(self, booking_id: int, input_otp: str | None) -> bool:
        if booking_id is None or not input_otp or not input_otp.strip():
            return False

        with self._lock:
            entry = self._storage.get(booking_id)
            if entry is None:
                return False

            if entry.is_expired():
                del self._storage[booking_id]
                return False

            return entry.code == input_otp.strip()

    def clear_otp(self, booking_id: int) -> None:
        with self._lock:
            self._storage.pop(booking_id, None)


otp_store = InMemoryOtpStore()
