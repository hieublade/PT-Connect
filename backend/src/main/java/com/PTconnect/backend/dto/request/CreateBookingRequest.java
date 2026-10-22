package com.PTconnect.backend.dto.request;

import com.PTconnect.backend.entity.enums.BookingType;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;

/**
 * DTO yêu cầu đặt lịch ca tập (Milestone 6 - Huy).
 * Hỗ trợ đặt theo gói (PACKAGE) hoặc học thử (TRIAL).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateBookingRequest {

    @NotNull(message = "Mã khung giờ (slotId) không được để trống")
    private Long slotId;

    @Builder.Default
    private BookingType bookingType = BookingType.PACKAGE;

    // Bắt buộc nếu bookingType == PACKAGE; NULL nếu là TRIAL
    private Long enrollmentId;

    @Size(max = 255, message = "Ghi chú không được vượt quá 255 ký tự")
    private String studentNote;
}
