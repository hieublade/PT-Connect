package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.UpdateAvatarRequest;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.service.IUserService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final IUserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<UserDTO>> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(ApiResponse.success(userService.getUserById(id)));
    }

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<UserDTO>> getCurrentUser(Authentication authentication) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        UserDTO user = userService.getUserByEmail(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin tài khoản thành công", user));
    }

    @PutMapping({"/profile", "/me"})
    public ResponseEntity<ApiResponse<UserDTO>> updateProfile(
            Authentication authentication,
            @Valid @RequestBody com.PTconnect.backend.dto.request.UpdateProfileRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        UserDTO updated = userService.updateProfile(email, request);
        return ResponseEntity.ok(ApiResponse.success("Cập nhật thông tin hồ sơ thành công", updated));
    }

    @PutMapping({"/avatar", "/me/avatar"})
    public ResponseEntity<ApiResponse<UserDTO>> updateAvatar(
            Authentication authentication,
            @Valid @RequestBody UpdateAvatarRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        UserDTO updated = userService.updateAvatar(email, request.getAvatarUrl());
        return ResponseEntity.ok(ApiResponse.success("Cập nhật ảnh đại diện thành công", updated));
    }

    @PostMapping(value = {"/avatar/upload", "/me/avatar/upload"}, consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<UserDTO>> uploadAvatar(
            Authentication authentication,
            @RequestParam("file") MultipartFile file) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        UserDTO updated = userService.uploadAvatar(email, file);
        return ResponseEntity.ok(ApiResponse.success("Tải ảnh đại diện lên thành công", updated));
    }
}
