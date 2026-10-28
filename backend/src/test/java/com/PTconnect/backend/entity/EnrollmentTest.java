package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Kiểm thử Đóng gói và Quản lý số buổi Thực thể Enrollment")
class EnrollmentTest {

    @Test
    @DisplayName("consumeSession() thành công khi hợp đồng ACTIVE và còn buổi")
    void consumeSession_WhenActiveAndRemainingPositive_Success() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.ACTIVE)
                .totalSessions(10)
                .remainingSessions(5)
                .build();

        enrollment.consumeSession();

        assertEquals(4, enrollment.getRemainingSessions());
    }

    @Test
    @DisplayName("consumeSession() ném lỗi khi hợp đồng không ACTIVE")
    void consumeSession_WhenNotActive_ThrowsIllegalStateException() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.COMPLETED)
                .totalSessions(10)
                .remainingSessions(5)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, enrollment::consumeSession);
        assertTrue(ex.getMessage().contains("ACTIVE"));
    }

    @Test
    @DisplayName("consumeSession() ném lỗi khi số buổi còn lại <= 0")
    void consumeSession_WhenZeroRemaining_ThrowsIllegalStateException() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.ACTIVE)
                .totalSessions(10)
                .remainingSessions(0)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, enrollment::consumeSession);
        assertTrue(ex.getMessage().contains("hết số buổi tập"));
    }

    @Test
    @DisplayName("restoreSession() thành công khi số buổi còn lại nhỏ hơn tổng số buổi")
    void restoreSession_WhenActiveAndLessThanTotal_Success() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.ACTIVE)
                .totalSessions(10)
                .remainingSessions(8)
                .build();

        enrollment.restoreSession();

        assertEquals(9, enrollment.getRemainingSessions());
    }

    @Test
    @DisplayName("restoreSession() ném lỗi khi số buổi còn lại đã đạt tối đa tổng số buổi")
    void restoreSession_WhenAlreadyFull_ThrowsIllegalStateException() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.ACTIVE)
                .totalSessions(10)
                .remainingSessions(10)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, enrollment::restoreSession);
        assertTrue(ex.getMessage().contains("vượt quá tổng số buổi"));
    }

    @Test
    @DisplayName("restoreSession() ném lỗi khi hợp đồng không ACTIVE")
    void restoreSession_WhenNotActive_ThrowsIllegalStateException() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.CANCELLED)
                .totalSessions(10)
                .remainingSessions(5)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, enrollment::restoreSession);
        assertTrue(ex.getMessage().contains("ACTIVE"));
    }

    @Test
    @DisplayName("complete() thành công khi hợp đồng đang ACTIVE")
    void complete_WhenActive_Success() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.ACTIVE)
                .build();

        enrollment.complete();

        assertEquals(EnrollmentStatus.COMPLETED, enrollment.getStatus());
    }

    @Test
    @DisplayName("complete() ném lỗi khi hợp đồng không ở trạng thái ACTIVE")
    void complete_WhenNotActive_ThrowsIllegalStateException() {
        Enrollment enrollment = Enrollment.builder()
                .status(EnrollmentStatus.CANCELLED)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, enrollment::complete);
        assertTrue(ex.getMessage().contains("ACTIVE"));
    }
}
