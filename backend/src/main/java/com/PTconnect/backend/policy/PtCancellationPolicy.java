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
 * Hiện thực chính sách hủy lịch dành cho Huấn luyện viên (PtCancellationPolicy).
 * Triển khai chính sách:
 * - Khi ca PENDING: PT từ chối, hoàn 1 buổi cho học viên, không phạt.
 * - Khi ca CONFIRMED và PT hủy trước >= 24h: hoàn 1 buổi cho học viên, không phạt.
 * - Khi ca CONFIRMED và PT hủy sát giờ (< 24h): hoàn 1 buổi cho học viên, đền bù 100% tiền 1 buổi học vào ví học viên và phạt 100% trừ ví PT.
 */
@Component
public class PtCancellationPolicy extends BaseCancellationPolicy {

    public static final double ADVANCE_NOTICE_HOURS = 24.0;
    public static final BigDecimal COMPENSATION_RATE = BigDecimal.valueOf(1.00); // 100% (Tiền 1 buổi học)
    public static final BigDecimal PENALTY_RATE = BigDecimal.valueOf(1.00);      // 100% (Tiền 1 buổi học)

    @Override
    public Role getSupportedRole() {
        return Role.PT;
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
                .explanation("Huấn luyện viên hủy ca tập đã duyệt sát giờ (< 24 giờ). Hoàn trả 1 buổi tập cho học viên, đền bù 100% tiền 1 buổi học ("
                        + compensation.toBigInteger() + " ₫) vào ví Học viên và phạt trừ "
                        + penalty.toBigInteger() + " ₫ từ ví Huấn luyện viên.")
                .build();
    }
}
