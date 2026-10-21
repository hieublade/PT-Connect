package com.PTconnect.backend.service;

import com.PTconnect.backend.entity.Booking;

public interface IBookingService {

    boolean canBookSlot(Long slotId, Long studentId);

    void validateBookingRequest(Long slotId, Long studentId, Long enrollmentId);
}
