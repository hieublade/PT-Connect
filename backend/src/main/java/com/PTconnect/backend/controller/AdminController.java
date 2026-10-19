package com.PTconnect.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Endpoint dành riêng cho ADMIN.
 * SecurityConfig đảm bảo chỉ ROLE_ADMIN truy cập được /api/admin/**.
 */
@RestController
@RequestMapping("/api/admin")
public class AdminController {

    /**
     * GET /api/admin/users
     * Trả về danh sách người dùng hệ thống — chỉ ROLE_ADMIN mới vào được.
     */
    @GetMapping("/users")
    public ResponseEntity<Map<String, String>> users(Authentication auth) {
        String email = (auth != null) ? auth.getName() : "unknown";
        return ResponseEntity.ok(Map.of(
                "page", "Admin User Management",
                "user", email
        ));
    }
}
