from app.models.enums import Role
from app.policies.admin import AdminCancellationPolicy
from app.policies.base import BaseCancellationPolicy
from app.policies.pt import PtCancellationPolicy
from app.policies.student import StudentCancellationPolicy


class CancellationPolicyFactory:
    def __init__(self):
        self.policies: dict[Role, BaseCancellationPolicy] = {
            Role.STUDENT: StudentCancellationPolicy(),
            Role.PT: PtCancellationPolicy(),
            Role.ADMIN: AdminCancellationPolicy(),
        }

    def get_policy(self, role: Role | str) -> BaseCancellationPolicy:
        if role is None:
            raise ValueError("Role không được để trống khi chọn chính sách hủy")

        if isinstance(role, str):
            try:
                role = Role(role.strip().upper())
            except Exception:
                raise ValueError(f"Không tìm thấy chính sách hủy phù hợp cho role: {role}")

        policy = self.policies.get(role)
        if not policy:
            raise ValueError(f"Không tìm thấy chính sách hủy phù hợp cho role: {role}")
        return policy


cancellation_policy_factory = CancellationPolicyFactory()
