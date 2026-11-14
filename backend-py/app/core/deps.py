import logging
from collections.abc import Callable, Generator

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import jwt_service
from app.db.session import SessionLocal
from app.models.enums import Role
from app.models.user import User

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session with autoflush and proper closing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_optional_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None, alias="Authorization"),
) -> User | None:
    """Extract authenticated user if Authorization Bearer header is present and valid."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:].strip()
    if not token:
        return None

    try:
        if jwt_service.is_token_expired(token):
            logger.warning("JWT validation failed: Token expired")
            return None

        email = jwt_service.extract_email(token)
        if not email:
            logger.warning("JWT validation failed: Missing email claim")
            return None

        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception as e:
        logger.warning("JWT validation failed: %s", e)
        return None


def get_current_user(
    user: User | None = Depends(get_optional_user),
) -> User:
    """Enforce authentication, raising 401 if user is anonymous."""
    if user is None:
        raise UnauthorizedException("Chưa đăng nhập")
    return user


def require_roles(*roles: Role | str) -> Callable[..., User]:
    """Dependency factory ensuring current user has one of the required roles."""
    expected_roles = {r.value if isinstance(r, Role) else str(r) for r in roles}

    def role_dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role_val = current_user.role.value if isinstance(current_user.role, Role) else str(current_user.role)
        if user_role_val not in expected_roles:
            logger.warning(
                "[ACCESS DENIED] user='%s' endpoint='%s' reason='Missing required role %s (has %s)' — 403 Forbidden",
                current_user.email,
                request.url.path,
                expected_roles,
                user_role_val,
            )
            raise ForbiddenException("Bạn không có quyền truy cập tài nguyên này")
        return current_user

    return role_dependency
