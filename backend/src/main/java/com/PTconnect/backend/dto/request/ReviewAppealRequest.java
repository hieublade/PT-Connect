package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

/**
 * DTO Huấn luyện viên gửi bản phản biện/giải trình cho đánh giá tiêu cực (1-3 sao).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewAppealRequest {

    @NotBlank(message = "Nội dung phản biện giải trình không được để trống")
    private String ptAppeal;

    private String ptEvidence;
}
