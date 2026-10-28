package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.UpdateUserStatusRequest;
import com.PTconnect.backend.dto.response.*;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.service.IAdminPTService;
import com.PTconnect.backend.service.IAdminStatisticsService;
import com.PTconnect.backend.service.IUserService;
import com.PTconnect.backend.util.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/admin")
@RequiredArgsConstructor
public class AdminController {

    private final IUserService userService;
    private final IAdminPTService adminPTService;
    private final IAdminStatisticsService adminStatisticsService;

    @GetMapping("/users")
    public ResponseEntity<ApiResponse<List<UserDTO>>> getUsers(
            @RequestParam(required = false) Role role) {
        List<UserDTO> users = (role != null)
                ? userService.getUsersByRole(role)
                : userService.getAllUsers();
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách người dùng thành công", users));
    }

    @PutMapping("/users/{id}/status")
    public ResponseEntity<ApiResponse<UserDTO>> updateUserStatus(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserStatusRequest request) {
        UserDTO updatedUser = userService.updateUserStatus(id, request.getStatus());
        return ResponseEntity.ok(ApiResponse.success("Cập nhật trạng thái người dùng thành công", updatedUser));
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

    @GetMapping("/statistics")
    public ResponseEntity<ApiResponse<AdminStatisticsResponse>> getStatistics() {
        AdminStatisticsResponse stats = adminStatisticsService.getStatistics();
        return ResponseEntity.ok(ApiResponse.success("Lấy thống kê hệ thống thành công", stats));
    }

    @GetMapping("/bookings")
    public ResponseEntity<ApiResponse<List<AdminBookingAnalyticsResponse>>> getBookingsForAnalytics() {
        List<AdminBookingAnalyticsResponse> bookings = adminStatisticsService.getBookingAnalytics();
        return ResponseEntity.ok(ApiResponse.success("Lấy dữ liệu đặt lịch cho phân tích thành công", bookings));
    }

    @GetMapping("/bookings/page")
    public ResponseEntity<ApiResponse<Page<AdminBookingAnalyticsResponse>>> getBookingsPage(Pageable pageable) {
        Page<AdminBookingAnalyticsResponse> page = adminStatisticsService.getBookingAnalytics(pageable);
        return ResponseEntity.ok(ApiResponse.success("Lấy dữ liệu đặt lịch phân trang thành công", page));
    }

    @GetMapping("/payments")
    public ResponseEntity<ApiResponse<List<AdminPaymentAnalyticsResponse>>> getPaymentsForAnalytics() {
        List<AdminPaymentAnalyticsResponse> payments = adminStatisticsService.getPaymentAnalytics();
        return ResponseEntity.ok(ApiResponse.success("Lấy dữ liệu thanh toán cho phân tích thành công", payments));
    }

    @GetMapping("/payments/page")
    public ResponseEntity<ApiResponse<Page<AdminPaymentAnalyticsResponse>>> getPaymentsPage(Pageable pageable) {
        Page<AdminPaymentAnalyticsResponse> page = adminStatisticsService.getPaymentAnalytics(pageable);
        return ResponseEntity.ok(ApiResponse.success("Lấy dữ liệu thanh toán phân trang thành công", page));
    }
}
