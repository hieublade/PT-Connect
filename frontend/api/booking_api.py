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

    # -------------------------------------------------------------
    # Milestone 7: Hủy lịch & Chính sách bồi thường
    # -------------------------------------------------------------

    @staticmethod
    def preview_cancel_booking(booking_id: int) -> Dict[str, Any]:
        """Xem trước quyền lợi hoàn/đền bù khi hủy lịch (GET /api/v1/bookings/{id}/cancel-preview)."""
        return api_client.get(f"/api/v1/bookings/{booking_id}/cancel-preview")

    @staticmethod
    def cancel_booking(
        booking_id: int,
        reason: str,
        evidence_url: Optional[str] = None,
        is_pt: bool = False
    ) -> Dict[str, Any]:
        """
        Thực hiện hủy ca tập theo chính sách bồi thường (PUT /api/v1/bookings/{id}/cancel hoặc /api/v1/pt/bookings/{id}/cancel).
        """
        payload = {"reason": reason, "evidenceUrl": evidence_url}
        endpoint = f"/api/v1/pt/bookings/{booking_id}/cancel" if is_pt else f"/api/v1/bookings/{booking_id}/cancel"
        return api_client.put(endpoint, json=payload)

    # -------------------------------------------------------------
    # Milestone 7: Điểm danh hai phía bằng OTP
    # -------------------------------------------------------------

    @staticmethod
    def start_attendance(booking_id: int) -> Dict[str, Any]:
        """Huấn luyện viên mở phiên điểm danh và lấy mã OTP 6 số (POST /api/v1/attendance/{bookingId}/start)."""
        return api_client.post(f"/api/v1/attendance/{booking_id}/start")

    @staticmethod
    def student_checkin(booking_id: int, otp_code: str) -> Dict[str, Any]:
        """Học viên nhập mã OTP 6 số để xác nhận có mặt (POST /api/v1/attendance/{bookingId}/student-checkin)."""
        payload = {"otpCode": otp_code}
        return api_client.post(f"/api/v1/attendance/{booking_id}/student-checkin", json=payload)

    @staticmethod
    def pt_confirm_attendance(booking_id: int) -> Dict[str, Any]:
        """Huấn luyện viên bấm hoàn tất buổi tập (POST /api/v1/attendance/{bookingId}/pt-confirm)."""
        return api_client.post(f"/api/v1/attendance/{booking_id}/pt-confirm")

    @staticmethod
    def mark_absent(booking_id: int, reason: str = "Học viên vắng mặt") -> Dict[str, Any]:
        """Huấn luyện viên đánh dấu học viên vắng mặt (POST /api/v1/attendance/{bookingId}/absent)."""
        params = {"reason": reason}
        return api_client.post(f"/api/v1/attendance/{booking_id}/absent", params=params)

    @staticmethod
    def get_attendance(booking_id: int) -> Optional[Dict[str, Any]]:
        """Xem thông tin điểm danh của ca tập (GET /api/v1/attendance/{bookingId})."""
        try:
            return api_client.get(f"/api/v1/attendance/{booking_id}")
        except Exception:
            return None

    # -------------------------------------------------------------
    # Milestone 7: Đánh giá & Nhận xét Huấn luyện viên
    # -------------------------------------------------------------

    @staticmethod
    def create_review(booking_id: int, rating: int, comment: Optional[str] = None) -> Dict[str, Any]:
        """Học viên gửi đánh giá 1-5 sao cho ca tập đã hoàn thành (POST /api/v1/reviews)."""
        payload = {
            "bookingId": booking_id,
            "rating": rating,
            "comment": comment
        }
        return api_client.post("/api/v1/reviews", json=payload)

    @staticmethod
    def get_booking_review(booking_id: int) -> Optional[Dict[str, Any]]:
        """Lấy đánh giá đã gửi cho ca tập (GET /api/v1/reviews/booking/{bookingId})."""
        try:
            res = api_client.get(f"/api/v1/reviews/booking/{booking_id}")
            if isinstance(res, dict):
                if "data" in res and ("status" in res or "message" in res):
                    res = res.get("data")
                if isinstance(res, dict) and (res.get("id") or res.get("rating")):
                    return res
                return None
            return None
        except Exception:
            return None

    @staticmethod
    def get_pt_reviews(pt_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách đánh giá của Huấn luyện viên (GET /api/v1/reviews/pt/{ptId})."""
        try:
            res = api_client.get(f"/api/v1/reviews/pt/{pt_id}")
            return res if isinstance(res, list) else []
        except Exception:
            return []

