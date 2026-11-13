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

/**
 * Controller phục vụ toàn bộ luồng Điểm danh ca tập xác thực hai phía bằng mã OTP (Milestone 7).
 * Hỗ trợ các endpoint tương thích với cả mobile/web và React frontend.
 */
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/attendance")
public class AttendanceController {

    private final IAttendanceService attendanceService;

    /**
     * Mở phiên điểm danh và sinh mã OTP 6 số
     * Hỗ trợ các route:
     * - POST /api/v1/attendance/{bookingId}/start
     * - POST /api/v1/attendance/bookings/{bookingId}/otp/generate (React frontend)
     * - POST /api/v1/attendance/{bookingId}/otp/generate
     */
    @PostMapping({"/{bookingId}/start", "/bookings/{bookingId}/otp/generate", "/{bookingId}/otp/generate"})
    public ResponseEntity<ApiResponse<StartAttendanceResponse>> startAttendance(
            Authentication authentication,
            @PathVariable Long bookingId) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        StartAttendanceResponse response = attendanceService.startAttendance(email, bookingId);
        return ResponseEntity.ok(ApiResponse.success("Mở phiên điểm danh thành công", response));
    }

    /**
     * Nhập mã OTP 6 số để xác nhận điểm danh
     * Hỗ trợ các route:
     * - POST /api/v1/attendance/{bookingId}/student-checkin
     * - POST /api/v1/attendance/bookings/{bookingId}/otp/verify (React frontend)
     * - POST /api/v1/attendance/{bookingId}/otp/verify
     */
    @PostMapping({"/{bookingId}/student-checkin", "/bookings/{bookingId}/otp/verify", "/{bookingId}/otp/verify"})
    public ResponseEntity<ApiResponse<AttendanceResponse>> studentCheckIn(
            Authentication authentication,
            @PathVariable Long bookingId,
            @Valid @RequestBody StudentCheckInRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.studentCheckIn(email, bookingId, request);
        return ResponseEntity.ok(ApiResponse.success("Xác nhận điểm danh thành công", response));
    }

    /**
     * Huấn luyện viên xác nhận hoàn tất buổi tập (POST /api/v1/attendance/{bookingId}/pt-confirm)
     */
    @PostMapping("/{bookingId}/pt-confirm")
    public ResponseEntity<ApiResponse<AttendanceResponse>> ptConfirmAttendance(
            Authentication authentication,
            @PathVariable Long bookingId) {
        String ptEmail = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.ptConfirmAttendance(ptEmail, bookingId);
        return ResponseEntity.ok(ApiResponse.success("Huấn luyện viên xác nhận điểm danh thành công", response));
    }

    /**
     * Huấn luyện viên đánh dấu học viên vắng mặt (POST /api/v1/attendance/{bookingId}/absent)
     */
    @PostMapping("/{bookingId}/absent")
    public ResponseEntity<ApiResponse<AttendanceResponse>> markAbsent(
            Authentication authentication,
            @PathVariable Long bookingId,
            @RequestParam(required = false, defaultValue = "Học viên không có mặt tại buổi tập") String reason) {
        String ptEmail = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.markAbsent(ptEmail, bookingId, reason);
        return ResponseEntity.ok(ApiResponse.success("Đã ghi nhận học viên vắng mặt (buổi tập vẫn được tính)", response));
    }

    /**
     * Xem trạng thái điểm danh của đơn đặt lịch (GET /api/v1/attendance/{bookingId})
     */
    @GetMapping("/{bookingId}")
    public ResponseEntity<ApiResponse<AttendanceResponse>> getAttendance(
            Authentication authentication,
            @PathVariable Long bookingId) {
        String userEmail = SecurityUtils.getCurrentUserEmail(authentication);
        AttendanceResponse response = attendanceService.getAttendanceByBookingId(userEmail, bookingId);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin điểm danh thành công", response));
    }
}
