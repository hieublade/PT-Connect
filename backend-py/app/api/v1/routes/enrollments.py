from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.core.responses import created_response, ok_response
from app.models.enums import Role
from app.models.user import User
from app.schemas.requests.enrollment import PurchaseCourseRequest
from app.services.enrollment_service import EnrollmentService

router = APIRouter(tags=["Enrollments"])


@router.post("/enrollments", status_code=201)
def purchase_course(
    request: PurchaseCourseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.STUDENT)),
):
    service = EnrollmentService(db)
    res = service.purchase_course(current_user.email, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Đăng ký khóa học thành công",
        status_code=201,
    )


# Declare /my before /{id} to prevent path routing conflict
@router.get("/enrollments/my")
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.STUDENT)),
):
    service = EnrollmentService(db)
    enrollments = service.get_my_enrollments(current_user.email)
    return ok_response(
        data=[e.model_dump(mode="json", by_alias=True) for e in enrollments],
        message="Lấy danh sách khóa học của học viên thành công",
    )


@router.get("/enrollments/{id}")
def get_enrollment_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EnrollmentService(db)
    res = service.get_enrollment_by_id(current_user.email, id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy thông tin hợp đồng thành công",
    )


@router.get("/enrollments/{id}/contract")
def get_contract_pdf(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EnrollmentService(db)
    pdf_bytes = service.get_contract_pdf(current_user.email, id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="contract_{id}.pdf"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@router.get("/pt/enrollments")
def get_pt_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PT)),
):
    service = EnrollmentService(db)
    enrollments = service.get_pt_enrollments(current_user.email)
    return ok_response(
        data=[e.model_dump(mode="json", by_alias=True) for e in enrollments],
        message="Lấy danh sách hợp đồng của Huấn luyện viên thành công",
    )
