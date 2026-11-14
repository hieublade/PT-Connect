from decimal import Decimal
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.core.responses import ok_response
from app.models.enums import PaymentMethod, PaymentStatus, PaymentType, Role
from app.models.payment import Payment
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.requests.auth import UpdateUserStatusRequest
from app.schemas.requests.wallet import AdminWithdrawRequest
from app.services.admin_pt_service import AdminPTService
from app.services.admin_statistics_service import AdminStatisticsService
from app.services.user_service import UserService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_roles(Role.ADMIN))],
)


@router.get("/users")
def get_users(
    role: Role | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = UserService(db)
    users = service.get_users_by_role(role) if role is not None else service.get_all_users()
    return ok_response(
        data=[u.model_dump(mode="json", by_alias=True) for u in users],
        message="Lấy danh sách người dùng thành công",
    )


@router.put("/users/{id}/status")
def update_user_status(
    id: int,
    request: UpdateUserStatusRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = UserService(db)
    user = service.update_user_status(id, request.status)
    return ok_response(
        data=user.model_dump(mode="json", by_alias=True),
        message="Cập nhật trạng thái người dùng thành công",
    )


@router.get("/pt/pending")
def get_pending_pts(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminPTService(db)
    pending_list = service.get_pending_pts()
    return ok_response(
        data=[p.model_dump(mode="json", by_alias=True) for p in pending_list],
        message="Lấy danh sách PT chờ duyệt thành công",
    )


@router.put("/pt/{id}/approve")
def approve_pt(
    id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminPTService(db)
    res = service.approve_pt(id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Phê duyệt hồ sơ Huấn luyện viên thành công",
    )


@router.put("/pt/{id}/reject")
def reject_pt(
    id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminPTService(db)
    res = service.reject_pt(id)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Từ chối hồ sơ Huấn luyện viên thành công",
    )


@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    stats = service.get_statistics()
    return ok_response(
        data=stats.model_dump(mode="json", by_alias=True),
        message="Lấy thống kê hệ thống thành công",
    )


@router.get("/bookings/page")
def get_bookings_page(
    page: int = Query(0, ge=0),
    size: int = Query(20, gt=0),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    res = service.get_booking_analytics_page(page, size)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy dữ liệu đặt lịch phân trang thành công",
    )


@router.get("/bookings")
def get_bookings_for_analytics(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    bookings = service.get_booking_analytics()
    return ok_response(
        data=[b.model_dump(mode="json", by_alias=True) for b in bookings],
        message="Lấy dữ liệu đặt lịch cho phân tích thành công",
    )


@router.get("/payments/page")
def get_payments_page(
    page: int = Query(0, ge=0),
    size: int = Query(20, gt=0),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    res = service.get_payment_analytics_page(page, size)
    return ok_response(
        data=res.model_dump(mode="json", by_alias=True),
        message="Lấy dữ liệu thanh toán phân trang thành công",
    )


@router.get("/payments")
def get_payments_for_analytics(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    service = AdminStatisticsService(db)
    payments = service.get_payment_analytics()
    return ok_response(
        data=[p.model_dump(mode="json", by_alias=True) for p in payments],
        message="Lấy dữ liệu thanh toán cho phân tích thành công",
    )


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    from sqlalchemy import text
    stmt = text("SELECT * FROM v_wallet_audit_logs ORDER BY id DESC LIMIT :limit")
    rows = db.execute(stmt, {"limit": limit}).mappings().all()
    data = [
        {
            "id": r["id"],
            "walletId": r["wallet_id"],
            "userId": r["user_id"],
            "fullName": r.get("full_name", ""),
            "oldBalance": float(r["old_balance"]),
            "newBalance": float(r["new_balance"]),
            "oldLockedBalance": float(r["old_locked_balance"]),
            "newLockedBalance": float(r["new_locked_balance"]),
            "changedAmount": float(r["changed_amount"]),
            "changedLockedAmount": float(r["changed_locked_amount"]) if r.get("changed_locked_amount") is not None else 0.0,
            "actionType": r["action_type"],
            "reason": r.get("reason", ""),
            "createdAt": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
        }
        for r in rows
    ]
    return ok_response(data=data, message="Lấy danh sách sổ cái kiểm toán tự động từ MySQL View thành công")


@router.get("/reconciliation")
def get_wallet_reconciliation(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(Role.ADMIN)),
):
    from sqlalchemy import text
    stmt = text("SELECT * FROM v_wallet_reconciliation ORDER BY wallet_id ASC LIMIT 100")
    rows = db.execute(stmt).mappings().all()
    data = [dict(r) for r in rows]
    return ok_response(data=data, message="Lấy dữ liệu đối soát số dư ví từ MySQL View thành công")


@router.get("/wallet")
def get_admin_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        # Nếu chưa có ví admin thì tạo ví
        wallet = Wallet(user_id=current_user.id, balance=Decimal("0.00"), locked_balance=Decimal("0.00"), currency="VND")
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    payments = db.query(Payment).filter(Payment.wallet_id == wallet.id).order_by(Payment.created_at.desc()).all()

    total_fee_collected = (
        db.query(func.coalesce(func.sum(Payment.amount), Decimal("0.00")))
        .filter(Payment.wallet_id == wallet.id, Payment.payment_type == PaymentType.PLATFORM_FEE, Payment.status == PaymentStatus.SUCCESS)
        .scalar()
        or Decimal("0.00")
    )

    total_withdrawn = (
        db.query(func.coalesce(func.sum(Payment.amount), Decimal("0.00")))
        .filter(Payment.wallet_id == wallet.id, Payment.payment_type == PaymentType.WITHDRAWAL, Payment.status == PaymentStatus.SUCCESS)
        .scalar()
        or Decimal("0.00")
    )

    txns = [
        {
            "id": p.id,
            "amount": float(p.amount),
            "paymentType": p.payment_type.value if hasattr(p.payment_type, "value") else str(p.payment_type),
            "paymentMethod": p.payment_method.value if hasattr(p.payment_method, "value") else str(p.payment_method),
            "status": p.status.value if hasattr(p.status, "value") else str(p.status),
            "transactionRef": p.transaction_ref,
            "createdAt": p.created_at.isoformat() if hasattr(p.created_at, "isoformat") else str(p.created_at),
        }
        for p in payments
    ]

    return ok_response(
        data={
            "walletId": wallet.id,
            "balance": float(wallet.balance),
            "lockedBalance": float(wallet.locked_balance),
            "totalPlatformFee": float(total_fee_collected),
            "totalWithdrawn": float(total_withdrawn),
            "transactions": txns,
        },
        message="Lấy thông tin ví doanh thu Admin thành công",
    )


@router.post("/wallet/withdraw")
def withdraw_admin_wallet(
    req: AdminWithdrawRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).with_for_update().first()
    if not wallet:
        raise ResourceNotFoundException("Không tìm thấy ví của Quản trị viên")

    # Quy tắc: Admin không có ràng buộc số dư tối thiểu / ký quỹ như PT và Học viên, có thể rút toàn bộ về 0đ
    if req.amount > wallet.balance:
        raise BadRequestException(f"Số dư ví ({wallet.balance:,.0f} đ) không đủ để rút số tiền {req.amount:,.0f} đ")

    wallet.balance -= req.amount
    db.flush()

    date_prefix = datetime.now().strftime("%Y%m%d%H%M%S")
    short_id = secrets.token_hex(3).upper()
    txn_ref = f"TXN_ADM_WD_{date_prefix}_{short_id}"

    payment = Payment(
        wallet_id=wallet.id,
        enrollment_id=None,
        amount=req.amount,
        payment_type=PaymentType.WITHDRAWAL,
        payment_method=PaymentMethod.BANK_TRANSFER,
        status=PaymentStatus.SUCCESS,
        transaction_ref=txn_ref,
    )
    db.add(payment)
    db.commit()
    db.refresh(wallet)

    return ok_response(
        data={
            "walletId": wallet.id,
            "newBalance": float(wallet.balance),
            "withdrawnAmount": float(req.amount),
            "bankName": req.bank_name,
            "accountNumber": req.account_number,
            "accountHolder": req.account_holder,
            "transactionRef": txn_ref,
            "createdAt": datetime.now().isoformat(),
        },
        message=f"Đã rút thành công {req.amount:,.0f} đ về tài khoản ngân hàng {req.bank_name} - {req.account_number}",
    )
