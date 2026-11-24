package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.StudentCheckInRequest;
import com.PTconnect.backend.dto.response.AttendanceResponse;
import com.PTconnect.backend.dto.response.StartAttendanceResponse;

public interface IAttendanceService {

    StartAttendanceResponse startAttendance(String ptEmail, Long bookingId, boolean bypassTimeCheck);

    default StartAttendanceResponse startAttendance(String ptEmail, Long bookingId) {
        return startAttendance(ptEmail, bookingId, false);
    }

    AttendanceResponse studentCheckIn(String studentEmail, Long bookingId, StudentCheckInRequest request);

    AttendanceResponse ptConfirmAttendance(String ptEmail, Long bookingId);

    AttendanceResponse markAbsent(String ptEmail, Long bookingId, String reason);

    AttendanceResponse getAttendanceByBookingId(String userEmail, Long bookingId);
}

