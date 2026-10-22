from typing import Any, Dict, List, Optional
from api.client import api_client


class BookingApi:
    """API Client cho các chức năng Đặt lịch và Quản lý Booking (Milestone 6)."""

    @staticmethod
    def create_booking(
        slot_id: int,
        booking_type: str = "PACKAGE",
        enrollment_id: Optional[int] = None,
        student_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Học viên đặt lịch tập (POST /api/v1/bookings).
        - slot_id: ID của khung giờ AVAILABLE
        - booking_type: "PACKAGE" hoặc "TRIAL"
        - enrollment_id: ID hợp đồng khóa học (bắt buộc nếu là PACKAGE)
        - student_note: Ghi chú của học viên
        """
        payload = {
            "slotId": slot_id,
            "bookingType": booking_type,
            "enrollmentId": enrollment_id,
            "studentNote": student_note
        }
        return api_client.post("/api/v1/bookings", json=payload)

    @staticmethod
    def get_my_bookings(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách booking của học viên hiện tại (GET /api/v1/bookings/my)."""
        params = {}
        if status:
            params["status"] = status
        res = api_client.get("/api/v1/bookings/my", params=params)
        return res if isinstance(res, list) else []

    @staticmethod
    def get_booking_by_id(booking_id: int) -> Dict[str, Any]:
        """Xem chi tiết một đơn đặt lịch (GET /api/v1/bookings/{id})."""
        return api_client.get(f"/api/v1/bookings/{booking_id}")

    @staticmethod
    def get_pt_bookings(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Huấn luyện viên xem danh sách booking ca tập của mình (GET /api/v1/pt/bookings)."""
        params = {}
        if status:
            params["status"] = status
        res = api_client.get("/api/v1/pt/bookings", params=params)
        return res if isinstance(res, list) else []

    @staticmethod
    def confirm_booking(booking_id: int) -> Dict[str, Any]:
        """Huấn luyện viên xác nhận đơn đặt lịch (PUT /api/v1/pt/bookings/{id}/confirm)."""
        return api_client.put(f"/api/v1/pt/bookings/{booking_id}/confirm")

    @staticmethod
    def reject_booking(booking_id: int, reason: str) -> Dict[str, Any]:
        """Huấn luyện viên từ chối đơn đặt lịch kèm lý do (PUT /api/v1/pt/bookings/{id}/reject)."""
        payload = {"reason": reason}
        return api_client.put(f"/api/v1/pt/bookings/{booking_id}/reject", json=payload)
