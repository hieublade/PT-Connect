package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.UpdateAvatarRequest;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.service.IUserService;
import com.PTconnect.backend.util.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping({"/api/v1/users", "/api/users"})
@RequiredArgsConstructor
public class UserController {

    private final IUserService userService;

    private String getCurrentUserEmail(Authentication auth) {
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException("Chưa đăng nhập");
        }
        Object principal = auth.getPrincipal();
        if (principal instanceof User user) {
            return user.getEmail();
        }
        if (principal instanceof String email) {
            return email;
        }
        return auth.getName();
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<UserDTO>>> getUsers(
            @RequestParam(required = false) Role role) {
        List<UserDTO> users = (role != null)
                ? userService.getUsersByRole(role)
                : userService.getAllUsers();
        return ResponseEntity.ok(ApiResponse.success(users));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<UserDTO>> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(ApiResponse.success(userService.getUserById(id)));
    }

    @PutMapping("/avatar")
    public ResponseEntity<ApiResponse<UserDTO>> updateAvatar(
            Authentication authentication,
            @Valid @RequestBody UpdateAvatarRequest request) {
        String email = getCurrentUserEmail(authentication);
        UserDTO updated = userService.updateAvatar(email, request.getAvatarUrl());
        return ResponseEntity.ok(ApiResponse.success("Cập nhật ảnh đại diện thành công", updated));
    }
}
