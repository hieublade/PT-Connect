"""
PT-Connect: Bộ kiểm thử tích hợp tự động API Chức năng PT & Admin Phê Duyệt
Phụ trách theo Milestone 4: Thành
Mục tiêu kiểm thử:
  1. Đăng ký tài khoản PT mới (201 Created, verificationStatus = PENDING)
  2. Admin xem danh sách PT chờ duyệt GET /api/v1/admin/pt/pending (200 OK)
  3. Admin duyệt PT thành công PUT /api/v1/admin/pt/{id}/approve (200 OK, VERIFIED, ACTIVE)
  4. Lấy thông tin hồ sơ cá nhân PT GET /api/v1/pt/profile (200 OK)
  5. Cập nhật hồ sơ PT hợp lệ PUT /api/v1/pt/profile (200 OK)
  6. Cập nhật hồ sơ PT với kinh nghiệm âm (< 0) -> 400 Bad Request
  7. Cập nhật hồ sơ PT với địa điểm trống -> 400 Bad Request
  8. Tạo khóa học mới hợp lệ POST /api/v1/pt/courses (201 Created)
  9. Tạo khóa học với số buổi <= 0 -> 400 Bad Request
  10. Tạo khóa học với giá âm (< 0) -> 400 Bad Request
  11. Lấy danh sách khóa học của PT GET /api/v1/pt/courses (200 OK)
  12. Cập nhật trạng thái khóa học sang INACTIVE PUT /api/v1/pt/courses/{id} (200 OK)
  13. Tạo khung giờ rảnh (Slot) hợp lệ POST /api/v1/pt/slots (201 Created, AVAILABLE)
  14. Tạo slot có thời gian bắt đầu trong quá khứ -> 400 Bad Request
  15. Tạo slot có thời gian kết thúc <= thời gian bắt đầu -> 400 Bad Request
  16. Tạo slot bị trùng hoặc chồng lấn thời gian với slot đã có -> 400 Bad Request
  17. Lấy danh sách slot của PT GET /api/v1/pt/slots (200 OK)
  18. Xóa slot AVAILABLE thành công DELETE /api/v1/pt/slots/{id} (200 OK)
  19. Admin từ chối phê duyệt PT PUT /api/v1/admin/pt/{id}/reject (200 OK, REJECTED)
"""

import os
import time
import uuid
from datetime import datetime, timedelta
import pytest
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8080").rstrip("/")
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
PT_PROFILE_URL = f"{BASE_URL}/api/v1/pt/profile"
PT_COURSES_URL = f"{BASE_URL}/api/v1/pt/courses"
PT_SLOTS_URL = f"{BASE_URL}/api/v1/pt/slots"
ADMIN_PENDING_PT_URL = f"{BASE_URL}/api/v1/admin/pt/pending"
ADMIN_APPROVE_PT_URL = f"{BASE_URL}/api/v1/admin/pt/{{id}}/approve"
ADMIN_REJECT_PT_URL = f"{BASE_URL}/api/v1/admin/pt/{{id}}/reject"

DEMO_PASSWORD = "Password123@"
ADMIN_EMAIL = "admin@ptconnect.vn"
PT_DEMO_EMAIL = "pt.hoangc@ptconnect.vn"


def generate_unique_contact():
    """Tạo email và phone ngẫu nhiên không trùng lặp."""
    unique_suffix = f"{int(time.time())}{uuid.uuid4().hex[:4]}"
    test_email = f"pt_{unique_suffix}@ptconnect-test.vn"
    test_phone = f"09{unique_suffix[-8:]}"
    return test_email, test_phone


def get_token(email: str, password: str = DEMO_PASSWORD) -> str:
    """Đăng nhập và lấy Bearer token."""
    res = requests.post(LOGIN_URL, json={"email": email, "password": password})
    if res.status_code != 200:
        pytest.fail(f"Không thể đăng nhập tài khoản {email}: {res.text}")
    data = res.json()
    return data["data"]["token"]


class TestMilestone4PTAndAdmin:
    """Bộ kiểm thử tích hợp các chức năng của PT và Admin Phê Duyệt theo Milestone 4."""

    @pytest.fixture(autouse=True)
    def setup_tokens(self):
        """Khởi tạo token Admin và token PT đã được seed sẵn."""
        self.admin_token = get_token(ADMIN_EMAIL)
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Token PT demo đã có sẵn trong init.sql (pt.hoangc@ptconnect.vn)
        self.demo_pt_token = get_token(PT_DEMO_EMAIL)
        self.demo_pt_headers = {"Authorization": f"Bearer {self.demo_pt_token}"}

    def test_01_register_pt_and_admin_approval_flow(self):
        """Ca 1: Đăng ký PT mới -> Chờ duyệt -> Admin duyệt thành công -> PT đăng nhập và xem hồ sơ."""
        email, phone = generate_unique_contact()
        reg_payload = {
            "fullName": "Huấn Luyện Viên Tự Động",
            "email": email,
            "password": DEMO_PASSWORD,
            "phone": phone,
            "role": "PT",
            "bio": "HLV cử tạ chuyên nghiệp",
            "experienceYears": 4,
            "availableLocations": "FitZone Thanh Xuân",
            "locationPricingNote": "Không phụ thu",
            "certificateUrls": '["https://cdn.ptconnect.vn/certs/c1.pdf"]'
        }

        # 1. Đăng ký PT mới
        reg_res = requests.post(REGISTER_URL, json=reg_payload)
        assert reg_res.status_code == 201, f"Đăng ký PT thất bại: {reg_res.text}"
        pt_user_id = reg_res.json()["data"]["user"]["id"]

        # 2. Admin lấy danh sách PT pending
        pending_res = requests.get(ADMIN_PENDING_PT_URL, headers=self.admin_headers)
        assert pending_res.status_code == 200
        pending_list = pending_res.json()["data"]

        target_pt = next((p for p in pending_list if p["userId"] == pt_user_id), None)
        assert target_pt is not None, f"Không tìm thấy PT userId={pt_user_id} trong danh sách pending"
        pt_profile_id = target_pt["id"]

        # 3. Admin duyệt PT
        approve_url = ADMIN_APPROVE_PT_URL.format(id=pt_profile_id)
        app_res = requests.put(approve_url, headers=self.admin_headers)
        assert app_res.status_code == 200
        app_data = app_res.json()["data"]
        assert app_data["verificationStatus"] == "VERIFIED"
        assert app_data["userStatus"] == "ACTIVE"

        # 4. PT mới đăng nhập và gọi GET /api/v1/pt/profile
        new_pt_token = get_token(email)
        new_pt_headers = {"Authorization": f"Bearer {new_pt_token}"}

        profile_res = requests.get(PT_PROFILE_URL, headers=new_pt_headers)
        assert profile_res.status_code == 200
        prof = profile_res.json()["data"]
        assert prof["fullName"] == "Huấn Luyện Viên Tự Động"
        assert prof["experienceYears"] == 4
        assert prof["verificationStatus"] == "VERIFIED"

    def test_02_update_pt_profile_validation(self):
        """Ca 2: Cập nhật hồ sơ PT hợp lệ và kiểm tra các ca lỗi validate (400 Bad Request)."""
        # Cập nhật hợp lệ
        valid_payload = {
            "bio": "Bio đã được cập nhật bởi pytest",
            "experienceYears": 7,
            "availableLocations": "Cali Cầu Giấy; FitZone Hà Đông",
            "locationPricingNote": "Phụ thu 15% tại nhà",
            "certificateUrls": '["https://cdn.ptconnect.vn/certs/c2.pdf"]'
        }
        res_ok = requests.put(PT_PROFILE_URL, json=valid_payload, headers=self.demo_pt_headers)
        assert res_ok.status_code == 200
        assert res_ok.json()["data"]["experienceYears"] == 7
        assert res_ok.json()["data"]["bio"] == "Bio đã được cập nhật bởi pytest"

        # Lỗi: experienceYears < 0
        invalid_exp = valid_payload.copy()
        invalid_exp["experienceYears"] = -2
        res_exp = requests.put(PT_PROFILE_URL, json=invalid_exp, headers=self.demo_pt_headers)
        assert res_exp.status_code == 400, "Kinh nghiệm âm phải trả về 400"

        # Lỗi: availableLocations trống
        invalid_loc = valid_payload.copy()
        invalid_loc["availableLocations"] = "   "
        res_loc = requests.put(PT_PROFILE_URL, json=invalid_loc, headers=self.demo_pt_headers)
        assert res_loc.status_code == 400, "Địa điểm trống phải trả về 400"

    def test_03_create_and_manage_courses(self):
        """Ca 3: Tạo khóa học, kiểm tra validate 400, xem danh sách và cập nhật trạng thái."""
        # Tạo hợp lệ
        course_payload = {
            "title": f"Khóa Test Pytest {int(time.time())}",
            "description": "Mô tả khóa tập tăng cơ",
            "totalSessions": 15,
            "validityDays": 45,
            "basePrice": 4500000.0
        }
        create_res = requests.post(PT_COURSES_URL, json=course_payload, headers=self.demo_pt_headers)
        assert create_res.status_code == 201
        course_data = create_res.json()["data"]
        course_id = course_data["id"]
        assert course_data["totalSessions"] == 15
        assert course_data["status"] == "ACTIVE"

        # Lỗi: totalSessions <= 0
        inv_sessions = course_payload.copy()
        inv_sessions["totalSessions"] = 0
        res_s = requests.post(PT_COURSES_URL, json=inv_sessions, headers=self.demo_pt_headers)
        assert res_s.status_code == 400

        # Lỗi: basePrice < 0
        inv_price = course_payload.copy()
        inv_price["basePrice"] = -50000.0
        res_p = requests.post(PT_COURSES_URL, json=inv_price, headers=self.demo_pt_headers)
        assert res_p.status_code == 400

        # Xem danh sách khóa học
        list_res = requests.get(PT_COURSES_URL, headers=self.demo_pt_headers)
        assert list_res.status_code == 200
        courses = list_res.json()["data"]
        assert any(c["id"] == course_id for c in courses)

        # Chuyển trạng thái sang INACTIVE
        update_payload = course_payload.copy()
        update_payload["status"] = "INACTIVE"
        up_res = requests.put(f"{PT_COURSES_URL}/{course_id}", json=update_payload, headers=self.demo_pt_headers)
        assert up_res.status_code == 200
        assert up_res.json()["data"]["status"] == "INACTIVE"

    def test_04_create_and_manage_slots(self):
        """Ca 4: Tạo slot giờ rảnh, kiểm tra các quy tắc nghiệp vụ slot và xóa slot AVAILABLE."""
        # 1. Tạo slot hợp lệ (ngày mai, 14:00 - 15:00)
        target_date = datetime.now() + timedelta(days=2)
        start_time = target_date.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        slot_payload = {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:00"),
            "endTime": end_time.strftime("%Y-%m-%dT%H:%M:00")
        }
        res_create = requests.post(PT_SLOTS_URL, json=slot_payload, headers=self.demo_pt_headers)
        assert res_create.status_code == 201
        created_slot = res_create.json()["data"]
        slot_id = created_slot["id"]
        assert created_slot["status"] == "AVAILABLE"

        # 2. Lỗi: Tạo slot trong quá khứ -> 400 Bad Request
        past_start = datetime.now() - timedelta(days=2)
        past_payload = {
            "startTime": past_start.strftime("%Y-%m-%dT%H:%M:00"),
            "endTime": (past_start + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:00")
        }
        res_past = requests.post(PT_SLOTS_URL, json=past_payload, headers=self.demo_pt_headers)
        assert res_past.status_code == 400, "Slot quá khứ phải trả về 400"

        # 3. Lỗi: Giờ kết thúc <= giờ bắt đầu -> 400 Bad Request
        inv_end_payload = {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:00"),
            "endTime": (start_time - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:00")
        }
        res_end = requests.post(PT_SLOTS_URL, json=inv_end_payload, headers=self.demo_pt_headers)
        assert res_end.status_code == 400, "Giờ kết thúc <= bắt đầu phải trả về 400"

        # 4. Lỗi: Trùng hoặc chồng lấn giờ -> 400 Bad Request
        overlap_payload = {
            "startTime": (start_time + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:00"),
            "endTime": (end_time + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:00")
        }
        res_overlap = requests.post(PT_SLOTS_URL, json=overlap_payload, headers=self.demo_pt_headers)
        assert res_overlap.status_code == 400, "Chồng lấn slot phải trả về 400"

        # 5. Xem danh sách slots
        list_res = requests.get(PT_SLOTS_URL, headers=self.demo_pt_headers)
        assert list_res.status_code == 200
        slots = list_res.json()["data"]
        assert any(s["id"] == slot_id for s in slots)

        # 6. Xóa slot AVAILABLE thành công
        del_res = requests.delete(f"{PT_SLOTS_URL}/{slot_id}", headers=self.demo_pt_headers)
        assert del_res.status_code == 200

    def test_05_admin_reject_pt_flow(self):
        """Ca 5: Admin từ chối duyệt PT (status chuyển sang REJECTED)."""
        email, phone = generate_unique_contact()
        reg_payload = {
            "fullName": "PT Bị Từ Chối",
            "email": email,
            "password": DEMO_PASSWORD,
            "phone": phone,
            "role": "PT",
            "experienceYears": 1,
            "availableLocations": "Hà Đông"
        }
        reg_res = requests.post(REGISTER_URL, json=reg_payload)
        assert reg_res.status_code == 201
        pt_user_id = reg_res.json()["data"]["user"]["id"]

        # Admin lấy pending
        pending_res = requests.get(ADMIN_PENDING_PT_URL, headers=self.admin_headers)
        pending_list = pending_res.json()["data"]
        target_pt = next(p for p in pending_list if p["userId"] == pt_user_id)
        pt_profile_id = target_pt["id"]

        # Admin từ chối
        reject_url = ADMIN_REJECT_PT_URL.format(id=pt_profile_id)
        rej_res = requests.put(reject_url, headers=self.admin_headers)
        assert rej_res.status_code == 200
        assert rej_res.json()["data"]["verificationStatus"] == "REJECTED"
        assert rej_res.json()["data"]["userStatus"] == "PENDING"
