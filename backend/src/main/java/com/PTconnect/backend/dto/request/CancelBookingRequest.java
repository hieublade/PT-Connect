package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

/**
 * DTO yêu cầu hủy lịch ca tập (Milestone 7).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CancelBookingRequest {

    @NotBlank(message = "Lý do hủy lịch là bắt buộc")
    private String reason;

    private String evidenceUrl;
}
