package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.enums.AttendanceStatus;
import lombok.*;

import java.time.LocalDateTime;

/**
 * DTO phản hồi khi Huấn luyện viên mở phiên điểm danh và nhận mã OTP (Milestone 7).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StartAttendanceResponse {

    private Long attendanceId;
    private Long bookingId;
    private String otpCode;
    private LocalDateTime checkInTime;
    private LocalDateTime expiresAt;
    private AttendanceStatus status;
    private String message;
}
