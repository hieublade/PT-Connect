package com.PTconnect.backend.util;

import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.exception.UnauthorizedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

/**
 * Tiện ích bảo mật dùng chung để trích xuất thông tin người dùng đang đăng nhập từ SecurityContext.
 */
public final class SecurityUtils {

    private SecurityUtils() {
        // Utility class
    }

    /**
     * Lấy email của người dùng hiện tại từ SecurityContextHolder.
     *
     * @return email người dùng
     * @throws UnauthorizedException nếu chưa đăng nhập hoặc principal không hợp lệ
     */
    public static String getCurrentUserEmail() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return getCurrentUserEmail(auth);
    }

    /**
     * Lấy email của người dùng hiện tại từ đối tượng Authentication được truyền vào
     * (hoặc fallback về SecurityContextHolder nếu null).
     *
     * @param auth đối tượng Authentication
     * @return email người dùng
     * @throws UnauthorizedException nếu chưa đăng nhập hoặc principal không hợp lệ
     */
    public static String getCurrentUserEmail(Authentication auth) {
        if (auth == null) {
            auth = SecurityContextHolder.getContext().getAuthentication();
        }
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            throw new UnauthorizedException("Chưa đăng nhập");
        }
        Object principal = auth.getPrincipal();
        if (principal instanceof User user) {
            return user.getEmail();
        }
        if (principal instanceof String email && !"anonymousUser".equals(email)) {
            return email;
        }
        String name = auth.getName();
        if (name != null && !name.isBlank() && !"anonymousUser".equals(name)) {
            return name;
        }
        throw new UnauthorizedException("Chưa đăng nhập");
    }
}
