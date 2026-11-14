from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.core.responses import created_response, ok_response
from app.models.enums import Role
from app.models.user import User
from app.schemas.requests.review import CreateReviewRequest
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", status_code=201)
def create_review(
    request: CreateReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.STUDENT)),
):
    service = ReviewService(db)
    res = service.create_review(current_user.email, request)
    return created_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Gửi đánh giá ca tập thành công",
        status_code=201,
    )


@router.get("/pt/{pt_id}")
def get_reviews_by_pt_id(
    pt_id: int,
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    reviews = service.get_reviews_by_pt_id(pt_id)
    return ok_response(
        data=[r.model_dump(mode="json", by_alias=True) for r in reviews],
        message="Lấy danh sách đánh giá của Huấn luyện viên thành công",
    )


# /my requires auth in service layer
@router.get("/my")
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReviewService(db)
    reviews = service.get_my_reviews(current_user.email)
    return ok_response(
        data=[r.model_dump(mode="json", by_alias=True) for r in reviews],
        message="Lấy danh sách đánh giá của tôi thành công",
    )


@router.get("/booking/{booking_id}")
def get_review_by_booking_id(
    booking_id: int,
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    review = service.get_review_by_booking_id(booking_id)
    return ok_response(
        data=review.model_dump(mode="json", by_alias=True) if review else None,
        message="Lấy đánh giá của ca tập thành công",
    )
