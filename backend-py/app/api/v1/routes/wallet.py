from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.core.responses import ok_response
from app.models.enums import Role
from app.models.user import User
from app.schemas.requests.wallet import TopupRequest
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("")
def get_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WalletService(db)
    res = service.get_wallet(current_user.email)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy thông tin ví thành công",
    )


@router.post("/topup")
def topup(
    request: TopupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.STUDENT)),
):
    service = WalletService(db)
    res = service.topup(current_user.email, request)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Nạp tiền vào ví thành công",
    )
