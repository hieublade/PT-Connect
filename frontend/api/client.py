import os
from typing import Any, Dict, Optional
import requests
import streamlit as st


class ApiException(Exception):
    """Ngoại lệ chuẩn hóa cho các lỗi trả về từ Backend API."""

    def __init__(self, message: str, status_code: int = 500, data: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.data = data

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.message}"


class ApiClient:
    """
    HTTP Client giao tiếp với Backend Spring Boot.
    - Tự động gắn Bearer Token từ st.session_state
    - Bóc tách ApiResponse và chuẩn hóa ngoại lệ ApiException
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.getenv("BACKEND_URL", "http://localhost:8080")).rstrip("/")

    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Lấy token từ session_state nếu người dùng đã đăng nhập
        token = None
        try:
            token = st.session_state.get("token")
        except Exception:
            pass

        if token:
            headers["Authorization"] = f"Bearer {token}"

        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            body = response.json()
        except Exception:
            body = None

        # Trả về dữ liệu nếu HTTP status thành công (200 - 299)
        if 200 <= response.status_code < 300:
            if isinstance(body, dict):
                # Format ApiResponse: { status: 200, message: "...", data: {...} }
                if "data" in body and body.get("data") is not None:
                    return body["data"]
                return body
            return body

        # Xử lý phản hồi lỗi từ Backend (4xx, 5xx)
        error_message = f"Máy chủ phản hồi mã lỗi {response.status_code}"
        error_data = None

        if isinstance(body, dict):
            error_message = body.get("message") or body.get("error") or error_message
            error_data = body.get("data")
        elif response.text:
            error_message = response.text.strip()

        raise ApiException(
            message=error_message,
            status_code=response.status_code,
            data=error_data
        )

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            res = requests.get(url, params=params, headers=self._get_headers(headers), timeout=10)
            return self._handle_response(res)
        except requests.ConnectionError:
            raise ApiException(
                "Không thể kết nối đến Backend API (Port 8080). Vui lòng kiểm tra dịch vụ backend đã chạy chưa.",
                status_code=503
            )
        except requests.Timeout:
            raise ApiException("Quá thời gian kết nối đến máy chủ Backend (Timeout 10s).", status_code=504)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            res = requests.post(url, json=json, params=params, headers=self._get_headers(headers), timeout=10)
            return self._handle_response(res)
        except requests.ConnectionError:
            raise ApiException(
                "Không thể kết nối đến Backend API (Port 8080). Vui lòng kiểm tra dịch vụ backend đã chạy chưa.",
                status_code=503
            )
        except requests.Timeout:
            raise ApiException("Quá thời gian kết nối đến máy chủ Backend (Timeout 10s).", status_code=504)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            res = requests.put(url, json=json, params=params, headers=self._get_headers(headers), timeout=10)
            return self._handle_response(res)
        except requests.ConnectionError:
            raise ApiException(
                "Không thể kết nối đến Backend API (Port 8080). Vui lòng kiểm tra dịch vụ backend đã chạy chưa.",
                status_code=503
            )
        except requests.Timeout:
            raise ApiException("Quá thời gian kết nối đến máy chủ Backend (Timeout 10s).", status_code=504)

    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            res = requests.delete(url, params=params, headers=self._get_headers(headers), timeout=10)
            return self._handle_response(res)
        except requests.ConnectionError:
            raise ApiException(
                "Không thể kết nối đến Backend API (Port 8080). Vui lòng kiểm tra dịch vụ backend đã chạy chưa.",
                status_code=503
            )
        except requests.Timeout:
            raise ApiException("Quá thời gian kết nối đến máy chủ Backend (Timeout 10s).", status_code=504)


# Khởi tạo singleton dùng chung
api_client = ApiClient()
