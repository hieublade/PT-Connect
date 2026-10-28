package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.BookingStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Kiểm thử Đóng gói và Chuyển trạng thái Thực thể Booking")
class BookingTest {

    @Test
    @DisplayName("confirm() thành công khi đơn đang ở trạng thái PENDING")
    void confirm_WhenPending_Success() {
        Booking booking = Booking.builder()
                .status(BookingStatus.PENDING)
                .build();

        booking.confirm();

        assertEquals(BookingStatus.CONFIRMED, booking.getStatus());
    }

    @Test
    @DisplayName("confirm() ném lỗi khi đơn không ở trạng thái PENDING (ví dụ: đã CANCELLED)")
    void confirm_WhenNotPending_ThrowsIllegalStateException() {
        Booking booking = Booking.builder()
                .status(BookingStatus.CANCELLED)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, booking::confirm);
        assertTrue(ex.getMessage().contains("PENDING"));
    }

    @Test
    @DisplayName("cancel() thành công khi đơn đang PENDING")
    void cancel_WhenPending_Success() {
        Booking booking = Booking.builder()
                .status(BookingStatus.PENDING)
                .build();

        booking.cancel();

        assertEquals(BookingStatus.CANCELLED, booking.getStatus());
    }

    @Test
    @DisplayName("cancel() thành công khi đơn đang CONFIRMED")
    void cancel_WhenConfirmed_Success() {
        Booking booking = Booking.builder()
                .status(BookingStatus.CONFIRMED)
                .build();

        booking.cancel();

        assertEquals(BookingStatus.CANCELLED, booking.getStatus());
    }

    @Test
    @DisplayName("cancel() ném lỗi khi đơn đã CANCELLED trước đó")
    void cancel_WhenAlreadyCancelled_ThrowsIllegalStateException() {
        Booking booking = Booking.builder()
                .status(BookingStatus.CANCELLED)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, booking::cancel);
        assertTrue(ex.getMessage().contains("CANCELLED trước đó"));
    }

    @Test
    @DisplayName("cancel() ném lỗi khi ca tập đã hoàn thành (COMPLETED)")
    void cancel_WhenCompleted_ThrowsIllegalStateException() {
        Booking booking = Booking.builder()
                .status(BookingStatus.COMPLETED)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, booking::cancel);
        assertTrue(ex.getMessage().contains("COMPLETED"));
    }

    @Test
    @DisplayName("complete() thành công khi ca tập đang CONFIRMED")
    void complete_WhenConfirmed_Success() {
        Booking booking = Booking.builder()
                .status(BookingStatus.CONFIRMED)
                .build();

        booking.complete();

        assertEquals(BookingStatus.COMPLETED, booking.getStatus());
    }

    @Test
    @DisplayName("complete() ném lỗi khi ca tập chưa được duyệt (PENDING)")
    void complete_WhenPending_ThrowsIllegalStateException() {
        Booking booking = Booking.builder()
                .status(BookingStatus.PENDING)
                .build();

        IllegalStateException ex = assertThrows(IllegalStateException.class, booking::complete);
        assertTrue(ex.getMessage().contains("CONFIRMED"));
    }
}
