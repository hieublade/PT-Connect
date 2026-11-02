from fastapi import APIRouter, Depends

from app.core.deps import require_roles
from app.models.enums import Role
from app.models.user import User

router = APIRouter(prefix="/student", tags=["Student"])


@router.get("/dashboard")
def student_dashboard(current_user: User = Depends(require_roles(Role.STUDENT))) -> dict[str, str]:
    return {
        "page": "Student Dashboard",
        "user": current_user.email,
    }
