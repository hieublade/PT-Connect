package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Attendance;
import com.PTconnect.backend.entity.enums.AttendanceStatus;
import com.PTconnect.backend.entity.enums.VerificationMethod;
import lombok.*;

import java.time.LocalDateTime;

/**
 * DTO phản hồi trạng thái chi tiết của việc điểm danh hai phía (Milestone 7).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AttendanceResponse {

    private Long id;
    private Long bookingId;
    private LocalDateTime checkInTime;
    private LocalDateTime checkOutTime;
    private VerificationMethod verificationMethod;
    private Boolean studentConfirmed;
    private Boolean ptConfirmed;
    private AttendanceStatus status;
    private boolean fullyConfirmed;

    public static AttendanceResponse fromEntity(Attendance attendance) {
        if (attendance == null) {
            return null;
        }

        return AttendanceResponse.builder()
                .id(attendance.getId())
                .bookingId(attendance.getBooking() != null ? attendance.getBooking().getId() : null)
                .checkInTime(attendance.getCheckInTime())
                .checkOutTime(attendance.getCheckOutTime())
                .verificationMethod(attendance.getVerificationMethod())
                .studentConfirmed(attendance.getStudentConfirmed())
                .ptConfirmed(attendance.getPtConfirmed())
                .status(attendance.getStatus())
                .fullyConfirmed(attendance.isFullyConfirmed())
                .build();
    }
}
