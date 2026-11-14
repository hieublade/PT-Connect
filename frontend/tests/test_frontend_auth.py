import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Thêm frontend vào sys.path để import được api module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.client import ApiClient, ApiException
from api.auth_api import AuthApi, save_auth_session, clear_auth_session, get_current_user, is_authenticated


class TestApiClient(unittest.TestCase):
    """Kiểm thử đơn vị cho lớp ApiClient giao tiếp REST API."""

    def test_headers_without_token(self):
        client = ApiClient("http://test-server:8080")
        headers = client._get_headers()
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertNotIn("Authorization", headers)

    def test_headers_with_token(self):
        client = ApiClient("http://test-server:8080")
        with patch("streamlit.session_state", {"token": "test-jwt-token"}):
            headers = client._get_headers()
            self.assertEqual(headers["Authorization"], "Bearer test-jwt-token")

    def test_handle_response_success_with_api_response_data(self):
        client = ApiClient("http://test-server:8080")
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {
            "status": 200,
            "message": "Thành công",
            "data": {"id": 1, "fullName": "Nguyen Van A"}
        }

        result = client._handle_response(mock_res)
        self.assertEqual(result, {"id": 1, "fullName": "Nguyen Van A"})

    def test_handle_response_error_raises_api_exception(self):
        client = ApiClient("http://test-server:8080")
        mock_res = MagicMock()
        mock_res.status_code = 401
        mock_res.json.return_value = {
            "status": 401,
            "message": "Email hoặc mật khẩu không chính xác",
            "data": None
        }

        with self.assertRaises(ApiException) as ctx:
            client._handle_response(mock_res)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Email hoặc mật khẩu không chính xác", str(ctx.exception))


class TestAuthApi(unittest.TestCase):
    """Kiểm thử đơn vị cho AuthApi và các helper quản lý phiên người dùng."""

    @patch("api.auth_api.api_client.post")
    def test_login_success(self, mock_post):
        mock_post.return_value = {
            "token": "fake-jwt",
            "tokenType": "Bearer",
            "user": {"id": 1, "email": "student.a@ptconnect.vn", "role": "STUDENT"}
        }

        result = AuthApi.login("student.a@ptconnect.vn", "Password123@")
        mock_post.assert_called_once_with(
            "/api/v1/auth/login",
            json={"email": "student.a@ptconnect.vn", "password": "Password123@"}
        )
        self.assertEqual(result["token"], "fake-jwt")
        self.assertEqual(result["user"]["role"], "STUDENT")

    @patch("api.auth_api.api_client.post")
    def test_register_payload_cleaning(self, mock_post):
        mock_post.return_value = {
            "token": "fake-jwt",
            "user": {"id": 10, "email": "new@ptconnect.vn", "role": "STUDENT"}
        }

        payload = {
            "fullName": "Test User",
            "email": "new@ptconnect.vn",
            "password": "Password123@",
            "phone": "0988888888",
            "role": "STUDENT",
            "bio": None,
            "availableLocations": ""
        }

        AuthApi.register(payload)
        # Các trường None hoặc "" phải được loại bỏ khỏi payload gửi đi
        expected_cleaned = {
            "fullName": "Test User",
            "email": "new@ptconnect.vn",
            "password": "Password123@",
            "phone": "0988888888",
            "role": "STUDENT"
        }
        mock_post.assert_called_once_with("/api/v1/auth/register", json=expected_cleaned)

    def test_session_state_lifecycle(self):
        fake_state = {}
        with patch("streamlit.session_state", fake_state):
            auth_data = {
                "token": "jwt-12345",
                "user": {"id": 5, "fullName": "Admin", "role": "ADMIN"}
            }

            # 1. Ban đầu chưa đăng nhập
            self.assertFalse(is_authenticated())
            self.assertIsNone(get_current_user())

            # 2. Lưu phiên đăng nhập
            save_auth_session(auth_data)
            self.assertTrue(is_authenticated())
            self.assertEqual(get_current_user(), {"id": 5, "fullName": "Admin", "role": "ADMIN"})
            self.assertEqual(fake_state.get("token"), "jwt-12345")

            # 3. Đăng xuất
            clear_auth_session()
            self.assertFalse(is_authenticated())
            self.assertIsNone(get_current_user())
            self.assertIsNone(fake_state.get("token"))


if __name__ == "__main__":
    unittest.main()
