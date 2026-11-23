package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.StudentCheckInRequest;
import com.PTconnect.backend.dto.response.AttendanceResponse;
import com.PTconnect.backend.dto.response.StartAttendanceResponse;
import com.PTconnect.backend.service.IAttendanceService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/attendance")
public class AttendanceController {

    private final IAttendanceService attendanceService;

    @PostMapping({"/{bookingId}/start", "/bookings/{bookingId}/otp/generate", "/{bookingId}/otp/generate"})
    public ResponseEntity<ApiResponse<StartAttendanceResponse>> startAttendance(
            Authentication authentication,
            @PathVariable Long bookingId) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        StartAttendanceResponse response = attendanceService.startAttendance(email, bookingId);
        return ResponseEntity.ok(ApiResponse.success("Mở phiên điểm danh thành công", response));
    }

    @PostMapping({"/{bookingId}/student-checkin", "/bookings/{bookingId}/otp/verify", "/{bookingId}/otp/verify"})
    public ResponseEntity<ApiResponse<AttendanceResponse>> studentCheckIn(
            Authentication authentication,
            @PathVariable Long bookingId,
            @Valid @RequestBody StudentCheckInRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.studentCheckIn(email, bookingId, request);
        return ResponseEntity.ok(ApiResponse.success("Xác nhận điểm danh thành công", response));
    }

    @PostMapping("/{bookingId}/pt-confirm")
    public ResponseEntity<ApiResponse<AttendanceResponse>> ptConfirmAttendance(
            Authentication authentication,
            @PathVariable Long bookingId) {
        String ptEmail = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.ptConfirmAttendance(ptEmail, bookingId);
        return ResponseEntity.ok(ApiResponse.success("Huấn luyện viên xác nhận điểm danh thành công", response));
    }

    @PostMapping("/{bookingId}/absent")
    public ResponseEntity<ApiResponse<AttendanceResponse>> markAbsent(
            Authentication authentication,
            @PathVariable Long bookingId,
            @RequestParam(required = false, defaultValue = "Học viên không có mặt tại buổi tập") String reason) {
        String ptEmail = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.markAbsent(ptEmail, bookingId, reason);
        return ResponseEntity.ok(ApiResponse.success("Đã ghi nhận học viên vắng mặt (buổi tập vẫn được tính)", response));
    }

    @GetMapping("/{bookingId}")
    public ResponseEntity<ApiResponse<AttendanceResponse>> getAttendance(
            Authentication authentication,
            @PathVariable Long bookingId) {
        String userEmail = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.getAttendanceByBookingId(userEmail, bookingId);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin điểm danh thành công", response));
    }
}

