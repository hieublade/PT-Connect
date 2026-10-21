package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.response.PendingPTResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.service.IAdminPTService;
import com.PTconnect.backend.service.IUserService;
import com.PTconnect.backend.util.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping({"/api/v1/admin", "/api/admin"})
@RequiredArgsConstructor
public class AdminController {

    private final IUserService userService;
    private final IAdminPTService adminPTService;

    @GetMapping("/users")
    public ResponseEntity<ApiResponse<List<UserDTO>>> getUsers(
            @RequestParam(required = false) Role role) {
        List<UserDTO> users = (role != null)
                ? userService.getUsersByRole(role)
                : userService.getAllUsers();
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách người dùng thành công", users));
    }

    @GetMapping("/pt/pending")
    public ResponseEntity<ApiResponse<List<PendingPTResponse>>> getPendingPTs() {
        List<PendingPTResponse> pendingList = adminPTService.getPendingPTs();
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách PT chờ duyệt thành công", pendingList));
    }

    @PutMapping("/pt/{id}/approve")
    public ResponseEntity<ApiResponse<PTProfileResponse>> approvePT(@PathVariable Long id) {
        PTProfileResponse response = adminPTService.approvePT(id);
        return ResponseEntity.ok(ApiResponse.success("Phê duyệt hồ sơ Huấn luyện viên thành công", response));
    }

    @PutMapping("/pt/{id}/reject")
    public ResponseEntity<ApiResponse<PTProfileResponse>> rejectPT(@PathVariable Long id) {
        PTProfileResponse response = adminPTService.rejectPT(id);
        return ResponseEntity.ok(ApiResponse.success("Từ chối hồ sơ Huấn luyện viên thành công", response));
    }
}
