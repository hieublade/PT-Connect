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
 * Hiện thực chính sách hủy lịch dành cho Huấn luyện viên (PtCancellationPolicy).
 * Triển khai chính xác bảng quy tắc mục 3.11 trong tài liệu đặc tả dự án.
 */
@Component
public class PtCancellationPolicy implements CancellationPolicy {

    public static final double ADVANCE_NOTICE_HOURS = 24.0;
    public static final BigDecimal COMPENSATION_RATE = BigDecimal.valueOf(0.20); // 20%
    public static final BigDecimal PENALTY_RATE = BigDecimal.valueOf(0.20);      // 20%

    @Override
    public String getSupportedRole() {
        return "PT";
    }

    @Override
    public CancellationCalculationResult calculate(
            Booking booking,
            LocalDateTime cancelTime,
            String reason,
            String evidenceUrl
    ) {
        BigDecimal sessionFee = booking.getSessionFee() != null ? booking.getSessionFee() : BigDecimal.ZERO;
        boolean isPackage = booking.getBookingType() == BookingType.PACKAGE;
        BigDecimal hoursBefore = calculateHoursBefore(booking, cancelTime);

        // 1. Trường hợp từ chối lịch PENDING
        if (booking.getStatus() == BookingStatus.PENDING) {
            return CancellationCalculationResult.builder()
                    .restoreSession(isPackage)
                    .refundAmount(isPackage ? sessionFee : BigDecimal.ZERO)
                    .compensationAmount(BigDecimal.ZERO)
                    .penaltyAmount(BigDecimal.ZERO)
                    .hoursBeforeSession(hoursBefore)
                    .explanation("Huấn luyện viên từ chối ca tập khi đang chờ duyệt. Hoàn lại 1 buổi cho học viên, không phạt.")
                    .build();
        }

        // 2. Ca tập đã CONFIRMED và PT hủy trước >= 24 giờ
        if (hoursBefore.doubleValue() >= ADVANCE_NOTICE_HOURS) {
            return CancellationCalculationResult.builder()
                    .restoreSession(isPackage)
                    .refundAmount(isPackage ? sessionFee : BigDecimal.ZERO)
                    .compensationAmount(BigDecimal.ZERO)
                    .penaltyAmount(BigDecimal.ZERO)
                    .hoursBeforeSession(hoursBefore)
                    .explanation("Huấn luyện viên hủy trước giờ tập >= 24 giờ. Hoàn lại 1 buổi cho học viên, không phạt hay đền bù.")
                    .build();
        }

        // 3. Ca tập đã CONFIRMED và PT hủy sát giờ (< 24 giờ)
        BigDecimal compensation = isPackage
                ? sessionFee.multiply(COMPENSATION_RATE).setScale(2, RoundingMode.HALF_UP)
                : BigDecimal.ZERO;
        BigDecimal penalty = isPackage
                ? sessionFee.multiply(PENALTY_RATE).setScale(2, RoundingMode.HALF_UP)
                : BigDecimal.ZERO;

        return CancellationCalculationResult.builder()
                .restoreSession(isPackage)
                .refundAmount(isPackage ? sessionFee : BigDecimal.ZERO)
                .compensationAmount(compensation)
                .penaltyAmount(penalty)
                .hoursBeforeSession(hoursBefore)
                .explanation("Huấn luyện viên hủy sát giờ (< 24 giờ). Hoàn 1 buổi cho học viên, đền bù 20% ("
                        + compensation + " đ) vào ví Học viên và phạt 20% (" + penalty + " đ) trừ từ ví Huấn luyện viên.")
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
