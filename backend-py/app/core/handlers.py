import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.alias_generators import to_camel
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    AppError,
)
from app.core.responses import error_response

logger = logging.getLogger(__name__)


def format_validation_error(exc: RequestValidationError) -> str:
    """Format Pydantic validation errors to match Spring Boot MethodArgumentNotValidException: '<field>: <message>'."""
    errors = exc.errors()
    if not errors:
        return "Dữ liệu đầu vào không hợp lệ"

    first_err = errors[0]
    loc = first_err.get("loc", [])
    if loc:
        # Get the field name, skipping 'body', 'query', etc. if possible
        raw_field = str(loc[-1])
        field_name = to_camel(raw_field)
    else:
        field_name = "field"

    msg = first_err.get("msg", "Dữ liệu không hợp lệ")
    if msg.startswith("Value error, "):
        msg = msg[len("Value error, ") :]

    return f"{field_name}: {msg}"


class IllegalStateException(RuntimeError):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning("AppError at %s: [%s] %s", request.url.path, exc.status_code, exc.message)
        return error_response(message=exc.message, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        msg = format_validation_error(exc)
        logger.warning("Validation error at %s: %s", request.url.path, msg)
        return error_response(message=msg, status_code=400)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.error("Database integrity error at %s: %s", request.url.path, exc)
        # Check if booking conflict
        orig_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        if "uq_active_slot" in orig_msg:
            return error_response(
                message="Khung giờ này vừa có người khác đặt trước, vui lòng chọn khung giờ khác",
                status_code=409,
            )
        return error_response(
            message="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc hệ thống!",
            status_code=409,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        logger.warning("ValueError at %s: %s", request.url.path, exc)
        return error_response(message=str(exc), status_code=400)

    @app.exception_handler(IllegalStateException)
    async def illegal_state_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.warning("Illegal state at %s: %s", request.url.path, exc)
        return error_response(message=str(exc), status_code=400)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.warning("HTTPException at %s: [%s] %s", request.url.path, exc.status_code, exc.detail)
        detail = str(exc.detail) if exc.detail else "Lỗi hệ thống"
        if exc.status_code == 401:
            return error_response(message=detail if detail != "Unauthorized" else "Chưa đăng nhập", status_code=401)
        if exc.status_code == 403:
            return error_response(message="Bạn không có quyền truy cập tài nguyên này", status_code=403)
        return error_response(message=detail, status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception at %s: %s", request.url.path, exc, exc_info=True)
        return error_response(message=str(exc) or "Lỗi hệ thống nội bộ", status_code=500)
