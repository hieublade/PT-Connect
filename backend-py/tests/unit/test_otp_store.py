from datetime import timedelta

from app.core.clock import now_local
from app.otp.store import InMemoryOtpStore, OtpEntry


def test_otp_generation_and_verification():
    store = InMemoryOtpStore()
    otp = store.generate_otp(101)
    assert len(otp) == 6
    assert otp.isdigit()

    # Wrong OTP
    assert store.validate_otp(101, "000000") is False

    # Right OTP
    assert store.validate_otp(101, otp) is True


def test_otp_expiration():
    store = InMemoryOtpStore()
    past_time = now_local() - timedelta(minutes=35)
    with store._lock:
        store._storage[102] = OtpEntry(code="123456", expires_at=past_time)

    # Should expire since TTL is 30 mins
    assert store.validate_otp(102, "123456") is False


def test_otp_clear():
    store = InMemoryOtpStore()
    store.generate_otp(103)
    assert store.get_active_otp(103) is not None
    store.clear_otp(103)
    assert store.get_active_otp(103) is None
