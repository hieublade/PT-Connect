package com.PTconnect.backend.dto.request;

import com.PTconnect.backend.entity.enums.BookingType;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;

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

    private Long enrollmentId;

    @Size(max = 255, message = "Ghi chú không được vượt quá 255 ký tự")
    private String studentNote;
}

