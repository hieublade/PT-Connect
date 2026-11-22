package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

/**
 * DTO Học viên gửi bằng chứng bổ sung cho đánh giá khi Admin yêu cầu.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewStudentEvidenceRequest {

    @NotBlank(message = "Nội dung hoặc bằng chứng bổ sung không được để trống")
    private String studentEvidence;
}
