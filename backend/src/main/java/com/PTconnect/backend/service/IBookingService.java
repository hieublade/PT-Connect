package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateBookingRequest;
import com.PTconnect.backend.dto.request.RejectBookingRequest;
import com.PTconnect.backend.dto.response.BookingResponse;
import com.PTconnect.backend.entity.enums.BookingStatus;

import java.util.List;

/**
 * Service xử lý toàn bộ luồng Booking – Trái tim hệ thống (Milestone 6).
 */
public interface IBookingService {

    boolean canBookSlot(Long slotId, Long studentId);

    void validateBookingRequest(Long slotId, Long studentId, Long enrollmentId);

    BookingResponse createBooking(String studentEmail, CreateBookingRequest request);

    List<BookingResponse> getMyBookings(String studentEmail, BookingStatus status);

    List<BookingResponse> getPTBookings(String ptEmail, BookingStatus status);

    BookingResponse getBookingById(String userEmail, Long bookingId);

    BookingResponse confirmBooking(String ptEmail, Long bookingId);

    BookingResponse rejectBooking(String ptEmail, Long bookingId, RejectBookingRequest request);
}
