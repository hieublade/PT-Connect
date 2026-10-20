"""
PT-Connect: Bộ kiểm thử tích hợp tự động API Xác thực & Phân quyền (Auth & RBAC)
Phụ trách theo Milestone 3: Thành
Mục tiêu kiểm thử:
  1. Đăng ký Student hợp lệ (201 Created)
  2. Đăng ký PT hợp lệ (201 Created, trạng thái PENDING)
  3. Đăng ký email trùng (400 / 409)
  4. Đăng ký số điện thoại trùng (400 / 409)
  5. Đăng ký email không hợp lệ (400 Bad Request)
  6. Đăng ký mật khẩu < 6 ký tự (400 Bad Request)
  7. Đăng nhập thành công với tài khoản mẫu (200 OK, trả về JWT)
  8. Đăng nhập thất bại do sai mật khẩu (401 Unauthorized)
  9. Đăng nhập thất bại do email không tồn tại (401 Unauthorized)
  10. Lấy thông tin tài khoản GET /auth/me thành công khi có token (200 OK)
  11. Lấy thông tin tài khoản GET /auth/me thất bại khi không có token (401 Unauthorized)
  12. Phân quyền RBAC: Token Student gọi API Admin bị từ chối (403 Forbidden)
  13. Phân quyền RBAC: Token PT gọi API Admin bị từ chối (403 Forbidden)
  14. Phân quyền RBAC: Token Admin gọi API Admin thành công (200 OK)
"""

import os
import time
import uuid
import pytest
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8080").rstrip("/")
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ME_URL = f"{BASE_URL}/api/v1/auth/me"
ADMIN_ENDPOINT_URL = f"{BASE_URL}/api/admin/users"

# Dữ liệu tài khoản mẫu được seed sẵn từ database/init.sql
DEMO_PASSWORD = "Password123@"
STUDENT_DEMO_EMAIL = "student.a@ptconnect.vn"
STUDENT_DEMO_PHONE = "0900000001"
PT_DEMO_EMAIL = "pt.hoangc@ptconnect.vn"
ADMIN_DEMO_EMAIL = "admin@ptconnect.vn"


def generate_unique_contact():
    """Tạo email và phone ngẫu nhiên không trùng lặp cho các ca test đăng ký."""
    unique_suffix = f"{int(time.time())}{uuid.uuid4().hex[:4]}"
    test_email = f"user_{unique_suffix}@ptconnect-test.vn"
    # Giới hạn phone 10 số bắt đầu bằng 09
    test_phone = f"09{unique_suffix[-8:]}"
    return test_email, test_phone


class TestAuthenticationAndRbac:
    """Bộ kiểm thử tích hợp các kịch bản Auth & RBAC cho hệ thống PT-Connect."""

    def test_01_register_student_success(self):
        """Ca 1: Đăng ký tài khoản Student hợp lệ -> Mong đợi HTTP 201 Created."""
        email, phone = generate_unique_contact()
        payload = {
            "fullName": "Kiểm Thử Viên Student",
            "email": email,
            "password": "Password123@",
            "phone": phone,
            "role": "STUDENT"
        }
        response = requests.post(REGISTER_URL, json=payload)
        assert response.status_code == 201, f"Expected 201 Created but got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "data" in data, "Response body thiếu trường 'data'"
        auth_data = data["data"]
        assert auth_data.get("token"), "Token JWT không được rỗng"
        assert auth_data.get("tokenType") == "Bearer"
        assert auth_data.get("user", {}).get("role") == "STUDENT"
        assert auth_data.get("user", {}).get("status") == "ACTIVE"

    def test_02_register_pt_success(self):
        """Ca 2: Đăng ký tài khoản PT hợp lệ -> Mong đợi HTTP 201, trạng thái PENDING."""
        email, phone = generate_unique_contact()
        payload = {
            "fullName": "Huấn Luyện Viên Mới",
            "email": email,
            "password": "Password123@",
            "phone": phone,
            "role": "PT",
            "bio": "HLV thể hình có chứng chỉ NASM",
            "experienceYears": 3,
            "availableLocations": "Quận Cầu Giấy, Hà Nội"
        }
        response = requests.post(REGISTER_URL, json=payload)
        assert response.status_code == 201, f"Expected 201 Created but got {response.status_code}: {response.text}"
        
        data = response.json()
        auth_data = data.get("data", {})
        assert auth_data.get("token"), "Token JWT không được rỗng"
        assert auth_data.get("user", {}).get("role") == "PT"
        assert auth_data.get("user", {}).get("status") == "PENDING"

    def test_03_register_duplicate_email(self):
        """Ca 3: Đăng ký với email đã tồn tại -> Mong đợi HTTP 400 hoặc 409."""
        _, phone = generate_unique_contact()
        payload = {
            "fullName": "Student Trùng Email",
            "email": STUDENT_DEMO_EMAIL,  # Email đã có trong hệ thống
            "password": "Password123@",
            "phone": phone,
            "role": "STUDENT"
        }
        response = requests.post(REGISTER_URL, json=payload)
        assert response.status_code in [400, 409], f"Expected 400 or 409 but got {response.status_code}: {response.text}"

    def test_04_register_duplicate_phone(self):
        """Ca 4: Đăng ký với số điện thoại đã tồn tại -> Mong đợi HTTP 400 hoặc 409."""
        email, _ = generate_unique_contact()
        payload = {
            "fullName": "Student Trùng SĐT",
            "email": email,
            "password": "Password123@",
            "phone": STUDENT_DEMO_PHONE,  # SĐT của student.a đã có trong hệ thống (0900000001)
            "role": "STUDENT"
        }
        response = requests.post(REGISTER_URL, json=payload)
        assert response.status_code in [400, 409], f"Expected 400 or 409 but got {response.status_code}: {response.text}"

    def test_05_register_invalid_email(self):
        """Ca 5: Đăng ký với email sai định dạng -> Mong đợi HTTP 400 Bad Request."""
        _, phone = generate_unique_contact()
        payload = {
            "fullName": "Student Sai Email",
            "email": "dinh_dang_email_khong_hop_le",
            "password": "Password123@",
            "phone": phone,
            "role": "STUDENT"
        }
        response = requests.post(REGISTER_URL, json=payload)
        assert response.status_code == 400, f"Expected 400 Bad Request but got {response.status_code}: {response.text}"

    def test_06_register_short_password(self):
        """Ca 6: Đăng ký mật khẩu < 6 ký tự -> Mong đợi HTTP 400 Bad Request."""
        email, phone = generate_unique_contact()
        payload = {
            "fullName": "Student Pass Ngan",
            "email": email,
            "password": "12345",  # Mật khẩu 5 ký tự (< 6)
            "phone": phone,
            "role": "STUDENT"
        }
        response = requests.post(REGISTER_URL, json=payload)
        assert response.status_code == 400, f"Expected 400 Bad Request but got {response.status_code}: {response.text}"

    def test_07_login_student_success(self):
        """Ca 7: Đăng nhập thành công với Student -> Mong đợi HTTP 200, JWT token hợp lệ."""
        payload = {
            "email": STUDENT_DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        response = requests.post(LOGIN_URL, json=payload)
        assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}: {response.text}"
        
        data = response.json()
        auth_data = data.get("data", {})
        assert auth_data.get("token"), "Thiếu JWT token"
        assert auth_data.get("user", {}).get("role") == "STUDENT"
        assert auth_data.get("user", {}).get("email") == STUDENT_DEMO_EMAIL

    def test_08_login_invalid_password(self):
        """Ca 8: Đăng nhập sai mật khẩu -> Mong đợi HTTP 401 Unauthorized."""
        payload = {
            "email": STUDENT_DEMO_EMAIL,
            "password": "SaiMatKhauHoanToan123!"
        }
        response = requests.post(LOGIN_URL, json=payload)
        assert response.status_code == 401, f"Expected 401 Unauthorized but got {response.status_code}: {response.text}"

    def test_09_login_nonexistent_user(self):
        """Ca 9: Đăng nhập với email không tồn tại -> Mong đợi HTTP 401 Unauthorized."""
        payload = {
            "email": "tai_khoan_ma_khong_ton_tai@ptconnect.vn",
            "password": DEMO_PASSWORD
        }
        response = requests.post(LOGIN_URL, json=payload)
        assert response.status_code == 401, f"Expected 401 Unauthorized but got {response.status_code}: {response.text}"

    def test_10_get_me_authenticated(self):
        """Ca 10: Gọi GET /auth/me kèm Bearer Token -> Mong đợi HTTP 200 OK."""
        # 1. Đăng nhập lấy token
        login_res = requests.post(LOGIN_URL, json={
            "email": STUDENT_DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        token = login_res.json()["data"]["token"]

        # 2. Gọi GET /auth/me
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(ME_URL, headers=headers)
        assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}: {response.text}"
        
        user_info = response.json().get("data", {})
        assert user_info.get("email") == STUDENT_DEMO_EMAIL
        assert user_info.get("role") == "STUDENT"

    def test_11_get_me_unauthenticated(self):
        """Ca 11: Gọi GET /auth/me không có Token -> Mong đợi HTTP 401 Unauthorized."""
        response = requests.get(ME_URL)
        assert response.status_code == 401, f"Expected 401 Unauthorized but got {response.status_code}: {response.text}"

    def test_12_rbac_student_forbidden_admin_api(self):
        """Ca 12: Phân quyền RBAC: Student gọi API Admin -> Mong đợi HTTP 403 Forbidden."""
        # 1. Lấy token của Student
        login_res = requests.post(LOGIN_URL, json={
            "email": STUDENT_DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        student_token = login_res.json()["data"]["token"]

        # 2. Student cố tình gọi API Admin
        headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(ADMIN_ENDPOINT_URL, headers=headers)
        assert response.status_code == 403, (
            f"Expected 403 Forbidden khi Student gọi API Admin nhưng nhận {response.status_code}: {response.text}"
        )

    def test_13_rbac_pt_forbidden_admin_api(self):
        """Ca 13: Phân quyền RBAC: PT gọi API Admin -> Mong đợi HTTP 403 Forbidden."""
        # 1. Lấy token của PT
        login_res = requests.post(LOGIN_URL, json={
            "email": PT_DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        pt_token = login_res.json()["data"]["token"]

        # 2. PT cố tình gọi API Admin
        headers = {"Authorization": f"Bearer {pt_token}"}
        response = requests.get(ADMIN_ENDPOINT_URL, headers=headers)
        assert response.status_code == 403, (
            f"Expected 403 Forbidden khi PT gọi API Admin nhưng nhận {response.status_code}: {response.text}"
        )

    def test_14_rbac_admin_allowed_admin_api(self):
        """Ca 14: Phân quyền RBAC: Admin gọi API Admin -> Mong đợi HTTP 200 OK."""
        # 1. Lấy token của Admin
        login_res = requests.post(LOGIN_URL, json={
            "email": ADMIN_DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        admin_token = login_res.json()["data"]["token"]

        # 2. Admin gọi API Admin
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(ADMIN_ENDPOINT_URL, headers=headers)
        assert response.status_code == 200, (
            f"Expected 200 OK khi Admin gọi API Admin nhưng nhận {response.status_code}: {response.text}"
        )
