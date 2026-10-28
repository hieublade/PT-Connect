package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.UpdateAvatarRequest;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.service.IUserService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final IUserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<UserDTO>> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(ApiResponse.success(userService.getUserById(id)));
    }

    @PutMapping("/avatar")
    public ResponseEntity<ApiResponse<UserDTO>> updateAvatar(
            Authentication authentication,
            @Valid @RequestBody UpdateAvatarRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        UserDTO updated = userService.updateAvatar(email, request.getAvatarUrl());
        return ResponseEntity.ok(ApiResponse.success("Cập nhật ảnh đại diện thành công", updated));
    }
}
