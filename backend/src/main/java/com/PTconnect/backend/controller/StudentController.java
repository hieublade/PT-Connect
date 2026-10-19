package com.PTconnect.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Endpoint dành riêng cho STUDENT.
 * SecurityConfig đảm bảo chỉ ROLE_STUDENT truy cập được /api/student/**.
 */
@RestController
@RequestMapping("/api/student")
public class StudentController {

    /**
     * GET /api/student/dashboard
     * Trả về thông tin dashboard học viên — chỉ STUDENT mới vào được.
     */
    @GetMapping("/dashboard")
    public ResponseEntity<Map<String, String>> dashboard(Authentication auth) {
        String email = (auth != null) ? auth.getName() : "unknown";
        return ResponseEntity.ok(Map.of(
                "page", "Student Dashboard",
                "user", email
        ));
    }
}
