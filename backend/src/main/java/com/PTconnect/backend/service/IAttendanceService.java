package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.StudentCheckInRequest;
import com.PTconnect.backend.dto.response.AttendanceResponse;
import com.PTconnect.backend.dto.response.StartAttendanceResponse;

/**
 * Service xử lý toàn bộ luồng Điểm danh ca tập xác thực hai phía bằng mã OTP (Milestone 7).
 * Phụ trách bởi: Huy.
 */
public interface IAttendanceService {

    /**
     * Huấn luyện viên bắt đầu buổi tập, khởi tạo phiên điểm danh và sinh mã OTP 6 số.
     */
    StartAttendanceResponse startAttendance(String ptEmail, Long bookingId);

    /**
     * Học viên nhập mã OTP 6 số nhận từ Huấn luyện viên để xác nhận có mặt (student_confirmed = true).
     */
    AttendanceResponse studentCheckIn(String studentEmail, Long bookingId, StudentCheckInRequest request);

    /**
     * Huấn luyện viên xác nhận điểm danh kết thúc buổi tập (pt_confirmed = true).
     * Khi cả 2 phía hoàn tất -> booking chuyển sang COMPLETED.
     */
    AttendanceResponse ptConfirmAttendance(String ptEmail, Long bookingId);

    /**
     * Huấn luyện viên đánh dấu học viên vắng mặt (ABSENT).
     * Buổi tập vẫn bị tính và booking chuyển sang COMPLETED.
     */
    AttendanceResponse markAbsent(String ptEmail, Long bookingId, String reason);

    /**
     * Xem thông tin phiên điểm danh của đơn đặt lịch.
     */
    AttendanceResponse getAttendanceByBookingId(String userEmail, Long bookingId);
}
