from typing import Any, Dict, List, Optional
from api.client import api_client


class StudentApi:
    """Các hàm gọi API cho Học viên (Student) - Milestone 5."""

    @staticmethod
    def get_pt_profiles(name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách PT đã duyệt (VERIFIED & ACTIVE), hỗ trợ tìm kiếm theo tên."""
        params = {}
        if name and name.strip():
            params["name"] = name.strip()
        res = api_client.get("/api/v1/pt-profiles", params=params)
        return res if isinstance(res, list) else []

    @staticmethod
    def get_pt_profile(pt_id: int) -> Dict[str, Any]:
        """Xem hồ sơ công khai của một PT (không có chứng chỉ)."""
        return api_client.get(f"/api/v1/pt-profiles/{pt_id}")

    @staticmethod
    def get_pt_courses(pt_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách các khóa học ACTIVE của một PT."""
        res = api_client.get(f"/api/v1/pt-profiles/{pt_id}/courses")
        return res if isinstance(res, list) else []

    @staticmethod
    def get_pt_slots(pt_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách các khung giờ rảnh AVAILABLE trong tương lai của một PT."""
        res = api_client.get(f"/api/v1/pt-profiles/{pt_id}/slots")
        return res if isinstance(res, list) else []

    @staticmethod
    def get_wallet() -> Dict[str, Any]:
        """Xem thông tin ví và lịch sử giao dịch của người dùng hiện tại."""
        return api_client.get("/api/v1/wallet")

    @staticmethod
    def topup_wallet(amount: float, payment_method: str = "BANK_TRANSFER") -> Dict[str, Any]:
        """Nạp tiền mô phỏng vào ví."""
        payload = {
            "amount": amount,
            "paymentMethod": payment_method
        }
        return api_client.post("/api/v1/wallet/topup", json=payload)

    @staticmethod
    def purchase_course(course_id: int, training_location: str, payment_method: str = "WALLET") -> Dict[str, Any]:
        """Mua khóa học, kích hoạt Transaction trừ ví, tạo enrollment, payment và hợp đồng."""
        payload = {
            "courseId": course_id,
            "trainingLocation": training_location,
            "paymentMethod": payment_method
        }
        return api_client.post("/api/v1/enrollments", json=payload)

    @staticmethod
    def get_my_enrollments() -> List[Dict[str, Any]]:
        """Lấy danh sách hợp đồng khóa học của học viên hiện tại."""
        res = api_client.get("/api/v1/enrollments/my")
        return res if isinstance(res, list) else []

    @staticmethod
    def download_contract(enrollment_id: int) -> bytes:
        """Tải file PDF hợp đồng điện tử."""
        return api_client.get_raw(f"/api/v1/enrollments/{enrollment_id}/contract")
