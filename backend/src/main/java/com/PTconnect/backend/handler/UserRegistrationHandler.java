package com.PTconnect.backend.handler;

import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;

/**
 * Interface cho chiến lược khởi tạo và lưu trữ người dùng theo từng Role.
 * Tuân thủ nguyên lý Open-Closed (OCP) và Dependency Inversion (DIP).
 */
public interface UserRegistrationHandler {

    /**
     * Xác định Handler này có hỗ trợ vai trò cụ thể hay không.
     */
    boolean supports(Role role);

    /**
     * Thực hiện tạo User (và Profile đi kèm nếu có) trong cơ sở dữ liệu.
     */
    User register(RegisterRequest request, String encodedPassword);
}
