package com.PTconnect.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Controller cho cac endpoint danh rieng cho PT (HLV).
 */
@RestController
@RequestMapping({"/api/v1/pt", "/api/pt"})
public class PTController {

    @GetMapping("/courses")
    public ResponseEntity<Map<String, String>> courses(Authentication auth) {
        String email = (auth != null) ? auth.getName() : "unknown";
        return ResponseEntity.ok(Map.of(
                "page", "PT Course Management",
                "user", email
        ));
    }
}
