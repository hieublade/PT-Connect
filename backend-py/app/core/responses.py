from typing import Any, Generic, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.clock import now_local

T = TypeVar("T")


def format_timestamp() -> str:
    """Format current local time as yyyy-MM-dd'T'HH:mm:ss'Z' to match Spring Boot Jackson pattern."""
    return now_local().strftime("%Y-%m-%dT%H:%M:%SZ")


class ApiResponse(BaseModel, Generic[T]):
    timestamp: str = Field(default_factory=format_timestamp)
    status: int
    message: str
    data: T | None = None

    @classmethod
    def success(cls, data: T | None = None, message: str = "Lấy dữ liệu thành công") -> "ApiResponse[T]":
        return cls(status=200, message=message, data=data)

    @classmethod
    def created(cls, data: T | None = None, message: str = "Tạo mới thành công") -> "ApiResponse[T]":
        return cls(status=201, message=message, data=data)

    @classmethod
    def error(cls, status: int, message: str) -> "ApiResponse[None]":
        return cls(status=status, message=message, data=None)


def ok_response(
    data: Any = None,
    message: str = "Lấy dữ liệu thành công",
    status_code: int = 200,
    body_status: int | None = None,
) -> JSONResponse:
    envelope = ApiResponse(
        status=body_status if body_status is not None else status_code,
        message=message,
        data=data,
    )
    return JSONResponse(
        content=envelope.model_dump(mode="json", by_alias=True),
        status_code=status_code,
    )


def created_response(
    data: Any = None,
    message: str = "Tạo mới thành công",
    status_code: int = 201,
    body_status: int | None = None,
) -> JSONResponse:
    envelope = ApiResponse(
        status=body_status if body_status is not None else status_code,
        message=message,
        data=data,
    )
    return JSONResponse(
        content=envelope.model_dump(mode="json", by_alias=True),
        status_code=status_code,
    )


def error_response(
    message: str,
    status_code: int = 400,
    body_status: int | None = None,
) -> JSONResponse:
    envelope = ApiResponse(
        status=body_status if body_status is not None else status_code,
        message=message,
        data=None,
    )
    return JSONResponse(
        content=envelope.model_dump(mode="json", by_alias=True),
        status_code=status_code,
    )
