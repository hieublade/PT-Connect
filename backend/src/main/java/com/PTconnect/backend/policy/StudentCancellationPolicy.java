package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;

/**
 * Hiện thực chính sách hủy lịch dành cho Học viên (StudentCancellationPolicy).
 * Triển khai chính xác bảng quy tắc mục 3.11 trong tài liệu đặc tả dự án.
 */
@Component
public class StudentCancellationPolicy implements CancellationPolicy {

    public static final double ADVANCE_NOTICE_HOURS = 24.0;
    public static final BigDecimal COMPENSATION_RATE = BigDecimal.valueOf(0.50); // 50%

    @Override
    public String getSupportedRole() {
        return "STUDENT";
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

        // 2. Ca tập còn đang chờ duyệt (PENDING): Luôn hoàn buổi, không phạt
        if (booking.getStatus() == BookingStatus.PENDING) {
            return CancellationCalculationResult.builder()
                    .restoreSession(true)
                    .refundAmount(sessionFee)
                    .compensationAmount(BigDecimal.ZERO)
                    .penaltyAmount(BigDecimal.ZERO)
                    .hoursBeforeSession(hoursBefore)
                    .explanation("Học viên hủy ca tập khi đang chờ duyệt (PENDING). Hoàn trả 1 buổi tập vào hợp đồng.")
                    .build();
        }

        // 3. Ca tập đã CONFIRMED và hủy trước >= 24 giờ
        if (hoursBefore.doubleValue() >= ADVANCE_NOTICE_HOURS) {
            return CancellationCalculationResult.builder()
                    .restoreSession(true)
                    .refundAmount(sessionFee)
                    .compensationAmount(BigDecimal.ZERO)
                    .penaltyAmount(BigDecimal.ZERO)
                    .hoursBeforeSession(hoursBefore)
                    .explanation("Học viên hủy trước giờ tập >= 24 giờ. Hoàn trả 1 buổi tập vào hợp đồng, không phát sinh chi phí.")
                    .build();
        }

        // 4. Ca tập đã CONFIRMED và hủy sát giờ (< 24 giờ)
        BigDecimal compensation = sessionFee.multiply(COMPENSATION_RATE).setScale(2, RoundingMode.HALF_UP);
        return CancellationCalculationResult.builder()
                .restoreSession(false)
                .refundAmount(BigDecimal.ZERO)
                .compensationAmount(compensation)
                .penaltyAmount(BigDecimal.ZERO)
                .hoursBeforeSession(hoursBefore)
                .explanation("Học viên hủy sát giờ (< 24 giờ). Mất buổi tập, đền bù 50% học phí ca tập (" + compensation + " đ) vào ví Huấn luyện viên.")
                .build();
    }

    private BigDecimal calculateHoursBefore(Booking booking, LocalDateTime cancelTime) {
        if (booking.getSlot() == null || booking.getSlot().getStartTime() == null) {
            return BigDecimal.ZERO;
        }
        LocalDateTime startTime = booking.getSlot().getStartTime();
        LocalDateTime effectiveCancelTime = cancelTime != null ? cancelTime : LocalDateTime.now();

        if (effectiveCancelTime.isAfter(startTime)) {
            return BigDecimal.ZERO;
        }

        long minutes = Duration.between(effectiveCancelTime, startTime).toMinutes();
        double hours = Math.max(0.0, minutes / 60.0);
        return BigDecimal.valueOf(hours).setScale(2, RoundingMode.HALF_UP);
    }
}
