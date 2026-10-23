package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.BookingType;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;

/**
 * Hiện thực chính sách hủy lịch dành cho Quản trị viên (AdminCancellationPolicy).
 * Áp dụng trong các trường hợp bất khả kháng hoặc can thiệp khiếu nại (Milestone 7).
 */
@Component
public class AdminCancellationPolicy implements CancellationPolicy {

    @Override
    public String getSupportedRole() {
        return "ADMIN";
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

        String evidenceNote = (evidenceUrl != null && !evidenceUrl.isBlank())
                ? " (Có kèm bằng chứng: " + evidenceUrl + ")"
                : "";

        return CancellationCalculationResult.builder()
                .restoreSession(isPackage)
                .refundAmount(isPackage ? sessionFee : BigDecimal.ZERO)
                .compensationAmount(BigDecimal.ZERO)
                .penaltyAmount(BigDecimal.ZERO)
                .hoursBeforeSession(hoursBefore)
                .explanation("Quản trị viên hủy do sự cố bất khả kháng" + evidenceNote + ". Khôi phục 1 buổi cho học viên, không phạt hay đền bù.")
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
