class AppError(Exception):
    status_code: int = 400
    message: str = "Đã xảy ra lỗi"

    def __init__(self, message: str | None = None, status_code: int | None = None):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundException(AppError):
    status_code = 404
    message = "Không tìm thấy tài nguyên"


class BookingConflictException(AppError):
    status_code = 409
    message = "Xung đột lịch đặt"


class InsufficientBalanceException(AppError):
    status_code = 400
    message = "Số dư khả dụng không đủ"


class UnauthorizedException(AppError):
    status_code = 401
    message = "Chưa đăng nhập"


class BadRequestException(AppError):
    status_code = 400
    message = "Yêu cầu không hợp lệ"


class ForbiddenException(AppError):
    status_code = 403
    message = "Bạn không có quyền truy cập tài nguyên này"


# Aliases for convenience
NotFound = ResourceNotFoundException
Conflict = BookingConflictException
BadRequest = BadRequestException
Unauthorized = UnauthorizedException
Forbidden = ForbiddenException
