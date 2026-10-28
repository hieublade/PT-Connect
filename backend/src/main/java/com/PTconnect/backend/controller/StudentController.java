package com.PTconnect.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Controller cho cac endpoint danh rieng cho STUDENT (Hoc vien).
 */
@RestController
@RequestMapping("/api/v1/student")
public class StudentController {

    @GetMapping("/dashboard")
    public ResponseEntity<Map<String, String>> dashboard(Authentication auth) {
        String email = (auth != null) ? auth.getName() : "unknown";
        return ResponseEntity.ok(Map.of(
                "page", "Student Dashboard",
                "user", email
        ));
    }
}
