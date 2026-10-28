package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.Booking;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;

/**
 * Lớp cơ sở trừu tượng cho các chính sách hủy ca tập (Milestone 7).
 * Tuân thủ nguyên tắc DRY: Tái sử dụng logic tính toán thời gian hủy trước ca tập.
 */
public abstract class BaseCancellationPolicy implements CancellationPolicy {

    /**
     * Tính số giờ còn lại từ thời điểm hủy tới khi ca tập bắt đầu.
     *
     * @param booking    Đơn đặt lịch
     * @param cancelTime Thời điểm hủy
     * @return Số giờ còn lại làm tròn 2 chữ số thập phân, hoặc BigDecimal.ZERO nếu quá khứ
     */
    protected BigDecimal calculateHoursBefore(Booking booking, LocalDateTime cancelTime) {
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
