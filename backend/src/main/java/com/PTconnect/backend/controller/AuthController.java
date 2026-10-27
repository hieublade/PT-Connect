package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.LoginRequest;
import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.dto.response.AuthResponse;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.service.IAuthService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping({"/api/v1/auth", "/auth"})
@RequiredArgsConstructor
public class AuthController {

    private final IAuthService authService;

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<AuthResponse>> register(@Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Đăng ký tài khoản thành công", response));
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody LoginRequest request) {
        AuthResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success("Đăng nhập thành công", response));
    }

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<UserDTO>> getMe(Authentication authentication) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        UserDTO userDTO = authService.getMe(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin tài khoản thành công", userDTO));
    }
}
