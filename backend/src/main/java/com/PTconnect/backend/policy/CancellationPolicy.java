package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.Role;

import java.time.LocalDateTime;

public interface CancellationPolicy {

    CancellationCalculationResult calculate(Booking booking, LocalDateTime cancelTime, String reason, String evidenceUrl);

    Role getSupportedRole();
}

