from typing import Any, Dict, Optional
import streamlit as st
from api.client import ApiException, api_client


class AuthApi:
    """Các hàm gọi API Xác thực (Authentication) tới Backend."""

    @staticmethod
    def login(email: str, password: str) -> Dict[str, Any]:
        """
        Đăng nhập vào hệ thống bằng Email và Mật khẩu.
        Trả về dict gồm: token, tokenType, user (UserDTO).
        """
        payload = {
            "email": email.strip(),
            "password": password
        }
        try:
            return api_client.post("/api/v1/auth/login", json=payload)
        except ApiException as e:
            if e.status_code == 404:
                return api_client.post("/auth/login", json=payload)
            raise e

    @staticmethod
    def register(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Đăng ký tài khoản mới (Học viên STUDENT hoặc PT).
        Payload gồm: fullName, email, password, phone, role, và các trường mở rộng nếu là PT.
        """
        clean_payload = {k: v for k, v in payload.items() if v is not None and v != ""}
        try:
            return api_client.post("/api/v1/auth/register", json=clean_payload)
        except ApiException as e:
            if e.status_code == 404:
                return api_client.post("/auth/register", json=clean_payload)
            raise e

    @staticmethod
    def get_me() -> Dict[str, Any]:
        """
        Lấy thông tin người dùng hiện tại dựa trên Bearer Token trong header.
        """
        try:
            return api_client.get("/api/v1/auth/me")
        except ApiException as e:
            if e.status_code == 404:
                return api_client.get("/auth/me")
            raise e

    @staticmethod
    def update_avatar(avatar_url: str) -> Dict[str, Any]:
        """Cập nhật URL ảnh đại diện của người dùng (PUT /api/v1/users/avatar)."""
        payload = {"avatarUrl": avatar_url.strip()}
        try:
            res = api_client.put("/api/v1/users/avatar", json=payload)
        except ApiException as e:
            if e.status_code == 404:
                res = api_client.put("/users/avatar", json=payload)
            else:
                raise e

        # Đồng bộ lại user trong st.session_state
        if st.session_state.get("user") and isinstance(res, dict):
            st.session_state["user"]["avatarUrl"] = res.get("avatarUrl", avatar_url)
        return res


# ===================================================================
# Helper Functions quản lý Session State trong Streamlit
# ===================================================================

def save_auth_session(auth_data: Dict[str, Any]) -> None:
    """Lưu token và thông tin user vào st.session_state."""
    token = auth_data.get("token")
    user = auth_data.get("user")
    st.session_state["token"] = token
    st.session_state["user"] = user
    st.session_state["logged_in"] = True


def clear_auth_session() -> None:
    """Đăng xuất, xóa token và thông tin phiên làm việc khỏi st.session_state."""
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)
    st.session_state["logged_in"] = False


def get_current_user() -> Optional[Dict[str, Any]]:
    """Lấy thông tin user hiện tại từ st.session_state."""
    return st.session_state.get("user")


def is_authenticated() -> bool:
    """Kiểm tra xem người dùng hiện tại đã đăng nhập hợp lệ hay chưa."""
    return bool(st.session_state.get("logged_in") and st.session_state.get("token"))
