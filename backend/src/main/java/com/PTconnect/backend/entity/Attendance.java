package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.AttendanceStatus;
import com.PTconnect.backend.entity.enums.VerificationMethod;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "attendance")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Attendance {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 1-1 với bookings (booking_id UNIQUE)
    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "booking_id", nullable = false, unique = true)
    private Booking booking;

    @Column(name = "check_in_time", nullable = false)
    private LocalDateTime checkInTime;

    @Column(name = "check_out_time")
    private LocalDateTime checkOutTime;

    @Enumerated(EnumType.STRING)
    @Column(name = "verification_method", nullable = false)
    @Builder.Default
    private VerificationMethod verificationMethod = VerificationMethod.OTP;

    @Column(name = "student_confirmed", nullable = false)
    @Builder.Default
    private Boolean studentConfirmed = false;

    @Column(name = "pt_confirmed", nullable = false)
    @Builder.Default
    private Boolean ptConfirmed = false;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private AttendanceStatus status = AttendanceStatus.PRESENT;

    // OTP được quản lý trong bộ nhớ / Service runtime (OtpUtil), không lưu trực tiếp vào bảng DB
    @Transient
    private String otpCode;

    @Transient
    private LocalDateTime otpExpiresAt;

    // Phương thức kiểm tra điểm danh 2 phía hoàn tất
    public boolean isFullyConfirmed() {
        return Boolean.TRUE.equals(this.studentConfirmed) && Boolean.TRUE.equals(this.ptConfirmed);
    }
}
