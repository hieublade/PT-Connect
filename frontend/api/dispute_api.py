from typing import Any, Dict, List, Optional
from api.client import api_client


class DisputeApi:
    """API Client cho Trọng tài khiếu nại & giải quyết tranh chấp (Dispute Resolution)."""

    @staticmethod
    def create_dispute(
        booking_id: int,
        dispute_type: str,
        reason: str,
        evidence_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Tạo khiếu nại mới cho ca tập (POST /api/v1/disputes)."""
        payload = {
            "bookingId": booking_id,
            "disputeType": dispute_type,
            "reason": reason,
            "evidenceUrl": evidence_url,
        }
        return api_client.post("/api/v1/disputes", json=payload)

    @staticmethod
    def list_disputes(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách khiếu nại (GET /api/v1/disputes)."""
        params = {}
        if status:
            params["status"] = status
        res = api_client.get("/api/v1/disputes", params=params)
        return res if isinstance(res, list) else []

    @staticmethod
    def get_dispute(dispute_id: int) -> Dict[str, Any]:
        """Xem chi tiết một khiếu nại (GET /api/v1/disputes/{id})."""
        return api_client.get(f"/api/v1/disputes/{dispute_id}")

    @staticmethod
    def submit_counter(
        dispute_id: int,
        counter_argument: str,
        counter_evidence_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Bên bị khiếu nại gửi phản biện & bằng chứng đối chứng (POST /api/v1/disputes/{id}/counter)."""
        payload = {
            "counterArgument": counter_argument,
            "counterEvidenceUrl": counter_evidence_url,
        }
        return api_client.post(f"/api/v1/disputes/{dispute_id}/counter", json=payload)

    @staticmethod
    def request_evidence(dispute_id: int, admin_notes: str) -> Dict[str, Any]:
        """Admin yêu cầu bổ sung bằng chứng (thời hạn 48h) (POST /api/v1/disputes/{id}/request-evidence)."""
        payload = {"adminNotes": admin_notes}
        return api_client.post(f"/api/v1/disputes/{dispute_id}/request-evidence", json=payload)

    @staticmethod
    def resolve_dispute(dispute_id: int, action: str, admin_notes: str) -> Dict[str, Any]:
        """Admin đưa ra phán quyết trọng tài kèm lý do bắt buộc (POST /api/v1/disputes/{id}/resolve)."""
        payload = {
            "action": action,
            "adminNotes": admin_notes,
        }
        return api_client.post(f"/api/v1/disputes/{dispute_id}/resolve", json=payload)

    @staticmethod
    def upload_evidence(file_bytes: bytes, filename: str) -> str:
        """Tải lên file ảnh bằng chứng đối chứng và trả về đường dẫn URL."""
        files = {"file": (filename, file_bytes, "image/jpeg")}
        res = api_client.post_files("/api/v1/disputes/upload-evidence", files=files)
        if isinstance(res, dict) and "url" in res:
            return res["url"]
        return "/static/uploads/" + filename

