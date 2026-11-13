package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateDisputeRequest {

    @NotNull(message = "Mã ca tập (bookingId) không được để trống")
    private Long bookingId;

    @NotBlank(message = "Loại khiếu nại không được để trống")
    private String disputeType; // PT_ABSENT, LATE_CANCEL_STUDENT, OTP_PREMATURE, QUALITY_ISSUE, OTHER

    private String disputeTypeLabel;

    private String severity; // HIGH, MEDIUM, LOW

    @NotBlank(message = "Vui lòng nhập tường trình chi tiết sự việc")
    private String statement;

    private String evidenceNote;
}
