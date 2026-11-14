package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import com.PTconnect.backend.entity.enums.Role;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;

/**
 * Hiện thực chính sách hủy lịch dành cho Học viên (StudentCancellationPolicy).
 * Triển khai chính sách:
 * - Khi ca PENDING: hoàn buổi, không đền bù.
 * - Khi ca đã được PT duyệt (CONFIRMED):
 *   + Hủy trước >= 24h: hoàn buổi vào hợp đồng nhưng đền bù 50% tiền buổi cho PT (phạt trừ ví học viên).
 *   + Hủy sát giờ (< 24h): mất buổi tập, đền bù 100% tiền buổi học cho Huấn luyện viên.
 */
@Component
public class StudentCancellationPolicy extends BaseCancellationPolicy {

    public static final double ADVANCE_NOTICE_HOURS = 24.0;
    public static final BigDecimal ADVANCE_COMPENSATION_RATE = BigDecimal.valueOf(0.50); // 50%
    public static final BigDecimal LATE_COMPENSATION_RATE = BigDecimal.valueOf(1.00);    // 100%

    @Override
    public Role getSupportedRole() {
        return Role.STUDENT;
    }

    @Override
    public CancellationCalculationResult calculate(
            Booking booking,
            LocalDateTime cancelTime,
            String reason,
            String evidenceUrl
    ) {
        BigDecimal sessionFee = booking.getSessionFee() != null ? booking.getSessionFee() : BigDecimal.ZERO;

        // 1. Trường hợp học thử (TRIAL)
        if (booking.getBookingType() == BookingType.TRIAL) {
            return CancellationCalculationResult.builder()
                    .restoreSession(false)
                    .refundAmount(BigDecimal.ZERO)
                    .compensationAmount(BigDecimal.ZERO)
                    .penaltyAmount(BigDecimal.ZERO)
                    .hoursBeforeSession(calculateHoursBefore(booking, cancelTime))
                    .explanation("Học viên hủy buổi học thử miễn phí (TRIAL). Khung giờ được giải phóng, không có buổi để hoàn.")
                    .build();
        }

        BigDecimal hoursBefore = calculateHoursBefore(booking, cancelTime);

        // 2. Ca tập còn đang chờ duyệt (PENDING): Luôn hoàn buổi, không đền bù
        if (booking.getStatus() == BookingStatus.PENDING) {
            return CancellationCalculationResult.builder()
                    .restoreSession(true)
                    .refundAmount(sessionFee)
                    .compensationAmount(BigDecimal.ZERO)
                    .penaltyAmount(BigDecimal.ZERO)
                    .hoursBeforeSession(hoursBefore)
                    .explanation("Học viên hủy ca tập khi đang chờ duyệt (PENDING). Hoàn trả 1 buổi tập vào hợp đồng, không phát sinh đền bù.")
                    .build();
        }

        // 3. Ca tập đã CONFIRMED (PT đã duyệt) và hủy trước >= 24 giờ
        if (hoursBefore.doubleValue() >= ADVANCE_NOTICE_HOURS) {
            BigDecimal compensation = sessionFee.multiply(ADVANCE_COMPENSATION_RATE).setScale(2, RoundingMode.HALF_UP);
            return CancellationCalculationResult.builder()
                    .restoreSession(true)
                    .refundAmount(sessionFee)
                    .compensationAmount(compensation)
                    .penaltyAmount(compensation)
                    .hoursBeforeSession(hoursBefore)
                    .explanation("Học viên hủy ca tập đã được PT duyệt (trước >= 24 giờ). Hoàn lại 1 buổi tập vào hợp đồng và đền bù 50% ("
                            + compensation.toBigInteger() + " ₫) cho Huấn luyện viên vì đã duyệt và giữ chỗ.")
                    .build();
        }

        // 4. Ca tập đã CONFIRMED (PT đã duyệt) và hủy sát giờ (< 24 giờ)
        BigDecimal compensation = sessionFee.multiply(LATE_COMPENSATION_RATE).setScale(2, RoundingMode.HALF_UP);
        return CancellationCalculationResult.builder()
                .restoreSession(false)
                .refundAmount(BigDecimal.ZERO)
                .compensationAmount(compensation)
                .penaltyAmount(BigDecimal.ZERO)
                .hoursBeforeSession(hoursBefore)
                .explanation("Học viên hủy ca tập đã được PT duyệt sát giờ (< 24 giờ). Học viên bị trừ mất buổi tập và đền bù tiền buổi học ("
                        + compensation.toBigInteger() + " ₫) vào ví Huấn luyện viên (Nền tảng khấu trừ 10% phí điều phối & trọng tài).")
                .build();
    }
}
