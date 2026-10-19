package com.PTconnect.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Endpoint dành riêng cho PT (Personal Trainer).
 * SecurityConfig đảm bảo chỉ ROLE_PT truy cập được /api/pt/**.
 */
@RestController
@RequestMapping("/api/pt")
public class PTController {

    /**
     * GET /api/pt/courses
     * Trả về danh sách khóa học của PT — chỉ ROLE_PT mới vào được.
     */
    @GetMapping("/courses")
    public ResponseEntity<Map<String, String>> courses(Authentication auth) {
        String email = (auth != null) ? auth.getName() : "unknown";
        return ResponseEntity.ok(Map.of(
                "page", "PT Courses Management",
                "user", email
        ));
    }
}
