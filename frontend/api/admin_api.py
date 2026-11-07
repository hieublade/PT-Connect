from typing import Any, Dict, List, Optional
from api.client import api_client


class AdminApi:
    """Các hàm gọi API cho Quản trị viên (Admin) - Milestone 4 & Milestone 8."""

    @staticmethod
    def get_pending_pts() -> List[Dict[str, Any]]:
        """Lấy danh sách các Huấn luyện viên (PT) đang chờ xét duyệt (PENDING)."""
        res = api_client.get("/api/v1/admin/pt/pending")
        return res if isinstance(res, list) else []

    @staticmethod
    def approve_pt(pt_profile_id: int) -> Dict[str, Any]:
        """Phê duyệt hồ sơ PT (chuyển sang VERIFIED và ACTIVE)."""
        return api_client.put(f"/api/v1/admin/pt/{pt_profile_id}/approve")

    @staticmethod
    def reject_pt(pt_profile_id: int) -> Dict[str, Any]:
        """Từ chối hồ sơ PT (chuyển sang REJECTED)."""
        return api_client.put(f"/api/v1/admin/pt/{pt_profile_id}/reject")

    @staticmethod
    def get_users(role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách tài khoản người dùng theo vai trò."""
        endpoint = f"/api/v1/admin/users?role={role}" if role else "/api/v1/admin/users"
        res = api_client.get(endpoint)
        return res if isinstance(res, list) else []

    @staticmethod
    def update_user_status(user_id: int, status: str) -> Dict[str, Any]:
        """Khóa hoặc mở khóa tài khoản người dùng (ACTIVE / SUSPENDED)."""
        return api_client.put(f"/api/v1/admin/users/{user_id}/status", json={"status": status})

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Lấy số liệu thống kê tổng hợp (tổng Học viên, PT, Bookings, Doanh thu)."""
        res = api_client.get("/api/v1/admin/statistics")
        return res if isinstance(res, dict) else {}

    @staticmethod
    def get_bookings() -> List[Dict[str, Any]]:
        """Lấy toàn bộ dữ liệu booking cho phân tích dữ liệu Pandas."""
        res = api_client.get("/api/v1/admin/bookings")
        return res if isinstance(res, list) else []

    @staticmethod
    def get_payments() -> List[Dict[str, Any]]:
        """Lấy toàn bộ dữ liệu thanh toán cho phân tích doanh thu Pandas."""
        res = api_client.get("/api/v1/admin/payments")
        return res if isinstance(res, list) else []
