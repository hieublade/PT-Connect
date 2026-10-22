package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

/**
 * DTO yêu cầu từ chối lịch ca tập của PT kèm lý do (Milestone 6 - Huy).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RejectBookingRequest {

    @NotBlank(message = "Lý do từ chối không được để trống")
    @Size(max = 500, message = "Lý do từ chối không được vượt quá 500 ký tự")
    private String reason;
}
