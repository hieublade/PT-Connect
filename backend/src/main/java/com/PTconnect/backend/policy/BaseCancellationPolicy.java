package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.Booking;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;

public abstract class BaseCancellationPolicy implements CancellationPolicy {

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

