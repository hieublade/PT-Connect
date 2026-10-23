from typing import Any, Dict, List, Optional
from api.client import api_client


class PTApi:
    """Các hàm gọi API cho Huấn luyện viên cá nhân (PT) - Milestone 4."""

    @staticmethod
    def get_profile() -> Dict[str, Any]:
        """Xem hồ sơ cá nhân của PT (kèm chứng chỉ, điểm đánh giá)."""
        return api_client.get("/api/v1/pt/profile")

    @staticmethod
    def update_profile(data: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật thông tin hồ sơ PT (bio, kinh nghiệm, địa điểm, ghi chú, chứng chỉ)."""
        return api_client.put("/api/v1/pt/profile", json=data)

    @staticmethod
    def get_courses() -> List[Dict[str, Any]]:
        """Lấy danh sách các khóa học của PT."""
        res = api_client.get("/api/v1/pt/courses")
        return res if isinstance(res, list) else []

    @staticmethod
    def create_course(data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo khóa học mới (tiêu đề, mô tả, số buổi, thời hạn, giá gốc)."""
        return api_client.post("/api/v1/pt/courses", json=data)

    @staticmethod
    def update_course(course_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật khóa học hoặc thay đổi trạng thái (ACTIVE / INACTIVE)."""
        return api_client.put(f"/api/v1/pt/courses/{course_id}", json=data)

    @staticmethod
    def delete_course(course_id: int) -> None:
        """Xóa khóa học (chỉ thành công nếu khóa học chưa có hợp đồng)."""
        api_client.delete(f"/api/v1/pt/courses/{course_id}")

    @staticmethod
    def get_slots() -> List[Dict[str, Any]]:
        """Lấy danh sách các khung giờ rảnh (slots) của PT."""
        res = api_client.get("/api/v1/pt/slots")
        return res if isinstance(res, list) else []

    @staticmethod
    def create_slot(start_time: Any, end_time: Optional[str] = None) -> Dict[str, Any]:
        """Tạo khung giờ rảnh mới (hỗ trợ cả 2 tham số hoặc truyền dictionary payload)."""
        if isinstance(start_time, dict):
            payload = start_time
        else:
            payload = {
                "startTime": start_time,
                "endTime": end_time
            }
        return api_client.post("/api/v1/pt/slots", json=payload)

    @staticmethod
    def delete_slot(slot_id: int) -> None:
        """Xóa khung giờ rảnh (chỉ thành công nếu slot AVAILABLE và chưa có booking)."""
        api_client.delete(f"/api/v1/pt/slots/{slot_id}")
