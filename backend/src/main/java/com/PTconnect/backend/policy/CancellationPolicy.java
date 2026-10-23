package com.PTconnect.backend.policy;

import com.PTconnect.backend.entity.Booking;

import java.time.LocalDateTime;

/**
 * Interface chính sách hủy lịch (Milestone 7).
 * Minh chứng tính ĐA HÌNH (Polymorphism) theo mẫu thiết kế Strategy.
 * Service chỉ tương tác qua interface này mà không phụ thuộc vào lớp cài đặt cụ thể.
 */
public interface CancellationPolicy {

    /**
     * Tính toán quyền lợi và nghĩa vụ tài chính khi hủy đơn đặt lịch.
     *
     * @param booking     Đơn đặt lịch cần hủy
     * @param cancelTime  Thời điểm thực hiện thao tác hủy
     * @param reason      Lý do hủy
     * @param evidenceUrl Bằng chứng đính kèm (nếu có)
     * @return Kết quả tính toán chính sách
     */
    CancellationCalculationResult calculate(Booking booking, LocalDateTime cancelTime, String reason, String evidenceUrl);

    /**
     * Vai trò mà chính sách này phục vụ (STUDENT, PT, ADMIN).
     */
    String getSupportedRole();
}
