package com.PTconnect.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Endpoint công khai — không yêu cầu xác thực.
 * Dùng cho health-check và các route không cần đăng nhập.
 */
@RestController
@RequestMapping("/api/public")
public class PublicController {

    /**
     * GET /api/public/health
     * Trả về 200 OK cho bất kỳ caller nào (kể cả anonymous).
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "PT-Connect Backend"
        ));
    }
}
