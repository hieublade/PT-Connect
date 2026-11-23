package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.enums.AttendanceStatus;
import lombok.*;

import java.time.LocalDateTime;

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

    public String getOtp() {
        return this.otpCode;
    }
}

