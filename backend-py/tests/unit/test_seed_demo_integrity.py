"""Kiểm tra dữ liệu mẫu database/seed_demo.sql thỏa các ràng buộc BCNF đợt 2.

Seed được nạp trong MySQL, ở đây chỉ chèn lại các câu INSERT vào SQLite (bảng không kiểu)
để đối chiếu dữ liệu bằng truy vấn.
"""

import re
import sqlite3
from pathlib import Path

import pytest

SEED_FILE = Path(__file__).resolve().parents[3] / "database" / "seed_demo.sql"
TRIGGER_FILE = SEED_FILE.with_name("trigger.sql")


@pytest.fixture(scope="module")
def seed_text() -> str:
    if not SEED_FILE.exists():
        pytest.skip(f"Không tìm thấy {SEED_FILE}")
    return SEED_FILE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def seed_db(seed_text):
    db = sqlite3.connect(":memory:")
    pattern = re.compile(r"INSERT INTO `(\w+)` \(([^)]*)\) VALUES(.*?);\s*\n", re.S)
    for table, cols, values in pattern.findall(seed_text):
        cols = cols.replace("`", "")
        db.execute(f"CREATE TABLE IF NOT EXISTS {table} ({cols})")
        db.execute(f"INSERT INTO {table} ({cols}) VALUES {values.replace(chr(92) + chr(39), chr(39) * 2)}")
    yield db
    db.close()


def _count(db, sql: str) -> int:
    return db.execute(sql).fetchone()[0]


def test_package_bookings_match_enrollment_owner(seed_db):
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM bookings b LEFT JOIN enrollments e ON e.id = b.enrollment_id "
        "WHERE b.enrollment_id IS NOT NULL AND (e.id IS NULL OR e.student_id <> b.student_id)",
    ) == 0
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM bookings WHERE (booking_type = 'TRIAL' AND enrollment_id IS NOT NULL) "
        "OR (booking_type = 'PACKAGE' AND enrollment_id IS NULL)",
    ) == 0


def test_booking_slot_belongs_to_enrollment_pt(seed_db):
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM bookings b JOIN availability_slots s ON s.id = b.slot_id "
        "JOIN enrollments e ON e.id = b.enrollment_id JOIN courses c ON c.id = e.course_id "
        "WHERE s.pt_id <> c.pt_id",
    ) == 0


def test_cancellations_respect_chk_cancel_actor(seed_db):
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM cancellations WHERE NOT ("
        "(cancelled_by_role = 'SYSTEM' AND cancelled_by_id IS NULL) OR "
        "(cancelled_by_role IN ('STUDENT', 'PT', 'ADMIN') AND cancelled_by_id IS NOT NULL))",
    ) == 0


def test_cancelled_by_is_the_real_actor(seed_db):
    # Người hủy vai trò PT phải là user sở hữu slot (không phải pt_profiles.id)
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM cancellations c JOIN bookings b ON b.id = c.booking_id "
        "JOIN availability_slots s ON s.id = b.slot_id JOIN pt_profiles p ON p.id = s.pt_id "
        "WHERE c.cancelled_by_role = 'PT' AND c.cancelled_by_id <> p.user_id",
    ) == 0
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM cancellations c JOIN bookings b ON b.id = c.booking_id "
        "WHERE c.cancelled_by_role = 'STUDENT' AND c.cancelled_by_id <> b.student_id",
    ) == 0


def test_pt_locations_are_unique(seed_db):
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM (SELECT pt_id, LOWER(location_name) FROM pt_locations "
        "GROUP BY 1, 2 HAVING COUNT(*) > 1)",
    ) == 0


def test_reviews_only_on_completed_bookings(seed_db):
    assert _count(
        seed_db,
        "SELECT COUNT(*) FROM reviews r JOIN bookings b ON b.id = r.booking_id WHERE b.status <> 'COMPLETED'",
    ) == 0


def test_seed_syncs_rating_and_checks_foreign_keys(seed_text):
    assert "TRUNCATE TABLE `pt_locations`" in seed_text
    assert "ĐỒNG BỘ CHỈ SỐ ĐÁNH GIÁ" in seed_text
    # Khóa ngoại phải được bật lại TRƯỚC các câu INSERT để MySQL kiểm tra FK ghép khi nạp
    fk_on = seed_text.index("SET FOREIGN_KEY_CHECKS = 1;")
    assert fk_on < seed_text.index("INSERT INTO `users`")


def test_trigger_file_drops_legacy_integrity_trigger():
    if not TRIGGER_FILE.exists():
        pytest.skip(f"Không tìm thấy {TRIGGER_FILE}")
    text = TRIGGER_FILE.read_text(encoding="utf-8")
    assert "DROP TRIGGER IF EXISTS `trg_bookings_check_student_integrity`;" in text
    assert "CREATE TRIGGER `trg_bookings_check_student_integrity`" not in text
