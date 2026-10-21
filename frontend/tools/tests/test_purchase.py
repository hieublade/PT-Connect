"""
PT-Connect: Bộ kiểm thử tích hợp tự động API Chức năng Student (Học viên) & Mua Khóa Học
Phụ trách theo Milestone 5: Thành
Mục tiêu kiểm thử:
  1. Học viên xem danh sách PT công khai GET /api/v1/pt-profiles (Chỉ trả VERIFIED và ACTIVE)
  2. DTO công khai PTPublicDTO không làm lộ chứng chỉ nhạy cảm (certificateUrls)
  3. Tìm kiếm PT theo tên GET /api/v1/pt-profiles?name=
  4. Tìm kiếm với tên không tồn tại trả mảng rỗng []
  5. Xem chi tiết hồ sơ PT GET /api/v1/pt-profiles/{id}
  6. Xem danh sách khóa học ACTIVE của PT GET /api/v1/pt-profiles/{id}/courses
  7. Xem danh sách slot rảnh AVAILABLE trong tương lai GET /api/v1/pt-profiles/{id}/slots
  8. Xem thông tin ví và lịch sử giao dịch GET /api/v1/wallet
  9. Nạp tiền vào ví với số tiền <= 0 -> 400 Bad Request
  10. Nạp tiền vào ví hợp lệ POST /api/v1/wallet/topup (200 OK, số dư tăng)
  11. Mua khóa học khi ví không đủ tiền -> 400 Bad Request (Kiểm tra Rollback Transaction không trừ tiền)
  12. Mua khóa học khi đủ tiền POST /api/v1/enrollments (201 Created):
      - Trừ ví đúng giá khóa học (final_price)
      - Tạo bản ghi enrollments (remaining_sessions = total_sessions)
      - Tạo bản ghi payments (PURCHASE_PACKAGE, SUCCESS)
  13. Xem danh sách khóa học của tôi GET /api/v1/enrollments/my
  14. Tải file hợp đồng PDF điện tử GET /api/v1/enrollments/{id}/contract (200 OK, application/pdf)
  15. Kiểm tra phân quyền: Không có token / Sai quyền gọi API Student
"""

import os
import time
import uuid
import pytest
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8080").rstrip("/")
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
PT_PROFILES_URL = f"{BASE_URL}/api/v1/pt-profiles"
WALLET_URL = f"{BASE_URL}/api/v1/wallet"
WALLET_TOPUP_URL = f"{BASE_URL}/api/v1/wallet/topup"
ENROLLMENTS_URL = f"{BASE_URL}/api/v1/enrollments"
MY_ENROLLMENTS_URL = f"{BASE_URL}/api/v1/enrollments/my"

DEMO_PASSWORD = "Password123@"
STUDENT_DEMO_EMAIL = "student.a@ptconnect.vn"
PT_DEMO_EMAIL = "pt.hoangc@ptconnect.vn"


def generate_unique_student():
    """Tạo thông tin học viên ngẫu nhiên phục vụ kiểm thử cô lập."""
    unique_suffix = f"{int(time.time())}{uuid.uuid4().hex[:4]}"
    test_email = f"student_{unique_suffix}@ptconnect-test.vn"
    test_phone = f"08{unique_suffix[-8:]}"
    return test_email, test_phone


def get_token(email: str, password: str = DEMO_PASSWORD) -> str:
    """Đăng nhập và lấy Bearer token."""
    res = requests.post(LOGIN_URL, json={"email": email, "password": password})
    if res.status_code != 200:
        pytest.fail(f"Không thể đăng nhập tài khoản {email}: {res.text}")
    data = res.json()
    return data["data"]["token"]


def register_new_student():
    """Đăng ký tài khoản học viên mới kèm ví số dư 0."""
    email, phone = generate_unique_student()
    payload = {
        "fullName": "Học Viên Test M5",
        "email": email,
        "password": DEMO_PASSWORD,
        "phone": phone,
        "role": "STUDENT"
    }
    res = requests.post(REGISTER_URL, json=payload)
    assert res.status_code == 201, f"Đăng ký thất bại: {res.text}"
    token = res.json()["data"]["token"]
    return email, token


class TestMilestone5StudentFlow:
    """Bộ kiểm thử tích hợp các chức năng Student & Mua khóa học Milestone 5."""

    @pytest.fixture(autouse=True)
    def setup_tokens(self):
        """Khởi tạo token cho các vai trò."""
        self.student_token = get_token(STUDENT_DEMO_EMAIL)
        self.student_headers = {"Authorization": f"Bearer {self.student_token}"}
        self.pt_token = get_token(PT_DEMO_EMAIL)
        self.pt_headers = {"Authorization": f"Bearer {self.pt_token}"}

    def test_01_get_pt_profiles_verified_active_only(self):
        """Output 1: Lấy danh sách PT công khai, chỉ hiển thị PT VERIFIED và ACTIVE."""
        res = requests.get(PT_PROFILES_URL, headers=self.student_headers)
        assert res.status_code == 200, f"Lỗi gọi GET /pt-profiles: {res.text}"
        data = res.json()
        assert data["status"] == 200
        profiles = data["data"]
        assert isinstance(profiles, list)
        assert len(profiles) > 0, "Phải có ít nhất 1 PT mẫu đã VERIFIED"

        for p in profiles:
            assert p.get("verificationStatus") == "VERIFIED", "Chỉ trả PT đã được duyệt"
            # Kiểm tra phân tách DTO (Hưng): PTPublicDTO không được lộ chứng chỉ
            assert "certificateUrls" not in p or p.get("certificateUrls") is None, "PTPublicDTO không được lộ chứng chỉ"
            assert "passwordHash" not in p, "Không được lộ mật khẩu"

    def test_02_search_pt_profiles_by_name(self):
        """Output 2: Tìm kiếm theo tên trả danh sách đã lọc, hoặc rỗng nếu không tìm thấy."""
        # 1. Tìm thấy PT với từ khóa 'Hoang'
        res_found = requests.get(f"{PT_PROFILES_URL}?name=Hoang", headers=self.student_headers)
        assert res_found.status_code == 200
        pts = res_found.json()["data"]
        assert len(pts) >= 1
        assert any("hoang" in p["fullName"].lower() for p in pts)

        # 2. Tìm với từ khóa không tồn tại -> Trả mảng rỗng []
        res_empty = requests.get(f"{PT_PROFILES_URL}?name=TenKhongTonTai_XYZ999", headers=self.student_headers)
        assert res_empty.status_code == 200
        empty_pts = res_empty.json()["data"]
        assert isinstance(empty_pts, list)
        assert len(empty_pts) == 0, "Tìm kiếm không khớp phải trả danh sách rỗng"

    def test_03_get_pt_detail_courses_and_slots(self):
        """Output 3: Xem hồ sơ chi tiết PT, danh sách khóa học ACTIVE và slot AVAILABLE tương lai."""
        # Lấy PT đầu tiên
        res = requests.get(PT_PROFILES_URL, headers=self.student_headers)
        pt_id = res.json()["data"][0]["id"]

        # 1. Chi tiết hồ sơ
        res_detail = requests.get(f"{PT_PROFILES_URL}/{pt_id}", headers=self.student_headers)
        assert res_detail.status_code == 200
        detail = res_detail.json()["data"]
        assert detail["id"] == pt_id
        assert "bio" in detail
        assert "availableLocations" in detail

        # 2. Khóa học ACTIVE của PT
        res_courses = requests.get(f"{PT_PROFILES_URL}/{pt_id}/courses", headers=self.student_headers)
        assert res_courses.status_code == 200
        courses = res_courses.json()["data"]
        assert isinstance(courses, list)
        for c in courses:
            assert c["status"] == "ACTIVE", "Chỉ trả khóa học ACTIVE"
            assert c["basePrice"] > 0
            assert c["totalSessions"] > 0

        # 3. Slot AVAILABLE trong tương lai
        res_slots = requests.get(f"{PT_PROFILES_URL}/{pt_id}/slots", headers=self.student_headers)
        assert res_slots.status_code == 200
        slots = res_slots.json()["data"]
        assert isinstance(slots, list)
        for s in slots:
            assert s["status"] == "AVAILABLE", "Chỉ trả slot AVAILABLE"

    def test_04_wallet_view_and_topup(self):
        """Xem ví và nạp tiền (mô phỏng) với kiểm tra ràng buộc số tiền."""
        # 1. Xem ví
        res_w = requests.get(WALLET_URL, headers=self.student_headers)
        assert res_w.status_code == 200
        w_data = res_w.json()["data"]
        initial_balance = float(w_data["balance"])
        assert initial_balance >= 0

        # 2. Nạp tiền âm hoặc bằng 0 -> 400 Bad Request
        res_neg = requests.post(WALLET_TOPUP_URL, json={"amount": -50000}, headers=self.student_headers)
        assert res_neg.status_code == 400, "Nạp số tiền âm phải trả 400 Bad Request"

        res_zero = requests.post(WALLET_TOPUP_URL, json={"amount": 0}, headers=self.student_headers)
        assert res_zero.status_code == 400, "Nạp 0 VND phải trả 400 Bad Request"

        # 3. Nạp tiền hợp lệ
        topup_amount = 2000000.0  # 2 triệu VND
        res_topup = requests.post(
            WALLET_TOPUP_URL,
            json={"amount": topup_amount, "paymentMethod": "BANK_TRANSFER"},
            headers=self.student_headers
        )
        assert res_topup.status_code == 200
        topup_res = res_topup.json()["data"]
        assert topup_res["status"] == "SUCCESS"
        assert topup_res["paymentType"] == "TOPUP"
        assert topup_res["transactionRef"].startswith("TXN_TOPUP_")

        # 4. Kiểm tra số dư ví đã tăng chính xác
        res_w_after = requests.get(WALLET_URL, headers=self.student_headers)
        new_balance = float(res_w_after.json()["data"]["balance"])
        assert new_balance == pytest.approx(initial_balance + topup_amount, rel=1e-2)

    def test_05_purchase_course_insufficient_balance_rollback(self):
        """Kiểm tra mua khóa khi thiếu tiền -> 400 Bad Request, Rollback ví và không tạo hợp đồng rác."""
        # Tạo học viên mới với ví số dư 0 VND
        _, new_student_token = register_new_student()
        new_headers = {"Authorization": f"Bearer {new_student_token}"}

        # Lấy khóa học mẫu (Gói Giảm Mỡ Chuyên Sâu giá 10,800,000 VND)
        res_pts = requests.get(PT_PROFILES_URL, headers=new_headers)
        pt_id = res_pts.json()["data"][0]["id"]
        res_courses = requests.get(f"{PT_PROFILES_URL}/{pt_id}/courses", headers=new_headers)
        course = res_courses.json()["data"][0]
        course_id = course["id"]

        # Thử mua khi số dư ví là 0 -> Bắt buộc 400 Bad Request
        payload = {
            "courseId": course_id,
            "trainingLocation": "Cali Fitness Cầu Giấy",
            "paymentMethod": "WALLET"
        }
        res_buy = requests.post(ENROLLMENTS_URL, json=payload, headers=new_headers)
        assert res_buy.status_code == 400, f"Thiếu tiền phải trả 400: {res_buy.text}"
        assert "không đủ" in res_buy.json()["message"].lower()

        # Chứng minh Rollback: Số dư ví không đổi (vẫn 0 VND)
        res_w = requests.get(WALLET_URL, headers=new_headers)
        assert float(res_w.json()["data"]["balance"]) == 0.0

        # Chứng minh không có hợp đồng rác nào được tạo
        res_my = requests.get(MY_ENROLLMENTS_URL, headers=new_headers)
        assert len(res_my.json()["data"]) == 0

    def test_06_purchase_course_success_atomic_transaction(self):
        """Output 4: Mua khóa thành công trong 1 Transaction (trừ ví, tạo enrollment, payment, hợp đồng PDF)."""
        # Tạo học viên mới
        _, new_student_token = register_new_student()
        new_headers = {"Authorization": f"Bearer {new_student_token}"}

        # Lấy khóa học cần mua
        res_pts = requests.get(PT_PROFILES_URL, headers=new_headers)
        pt_id = res_pts.json()["data"][0]["id"]
        res_courses = requests.get(f"{PT_PROFILES_URL}/{pt_id}/courses", headers=new_headers)
        course = res_courses.json()["data"][0]
        course_id = course["id"]
        course_price = float(course["basePrice"])
        course_sessions = course["totalSessions"]

        # Nạp tiền vừa đủ + dư một ít vào ví
        topup_amount = course_price + 500000.0
        res_top = requests.post(WALLET_TOPUP_URL, json={"amount": topup_amount}, headers=new_headers)
        assert res_top.status_code == 200

        # Thực hiện mua khóa học
        payload = {
            "courseId": course_id,
            "trainingLocation": "Phòng tập FitZone số 12 Cầu Giấy",
            "paymentMethod": "WALLET"
        }
        res_buy = requests.post(ENROLLMENTS_URL, json=payload, headers=new_headers)
        assert res_buy.status_code == 201, f"Mua khóa thành công phải trả 201 Created: {res_buy.text}"
        enroll_data = res_buy.json()["data"]

        # Kiểm tra chi tiết hợp đồng
        enrollment_id = enroll_data["id"]
        assert enroll_data["finalPrice"] == course_price
        assert enroll_data["totalSessions"] == course_sessions
        assert enroll_data["remainingSessions"] == course_sessions, "Kho buổi ban đầu remaining = total"
        assert enroll_data["status"] == "ACTIVE"
        assert enroll_data["trainingLocation"] == "Phòng tập FitZone số 12 Cầu Giấy"

        # 1. Kiểm tra ví bị trừ đúng final_price
        res_w = requests.get(WALLET_URL, headers=new_headers)
        remaining_balance = float(res_w.json()["data"]["balance"])
        assert remaining_balance == pytest.approx(500000.0, rel=1e-2)

        # 2. Kiểm tra có dòng payment PURCHASE_PACKAGE
        txns = res_w.json()["data"]["transactions"]
        buy_txns = [t for t in txns if t["paymentType"] == "PURCHASE_PACKAGE"]
        assert len(buy_txns) == 1
        assert buy_txns[0]["status"] == "SUCCESS"
        assert float(buy_txns[0]["amount"]) == course_price

        # 3. Kiểm tra danh sách khóa học của tôi
        res_my = requests.get(MY_ENROLLMENTS_URL, headers=new_headers)
        assert res_my.status_code == 200
        my_list = res_my.json()["data"]
        assert len(my_list) >= 1
        assert my_list[0]["id"] == enrollment_id

        # 4. Kiểm tra tải hợp đồng PDF điện tử
        res_contract = requests.get(f"{ENROLLMENTS_URL}/{enrollment_id}/contract", headers=new_headers)
        assert res_contract.status_code == 200
        assert "application/pdf" in res_contract.headers.get("Content-Type", "")
        assert len(res_contract.content) > 100, "File PDF hợp đồng không được rỗng"
        assert res_contract.content.startswith(b"%PDF"), "Dữ liệu trả về phải là định dạng PDF chuẩn"
