package com.PTconnect.backend.util;

import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.exception.UnauthorizedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

public final class SecurityUtils {

    private SecurityUtils() {

    }

    public static String getCurrentUserEmail() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return getCurrentUserEmail(auth);
    }

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

