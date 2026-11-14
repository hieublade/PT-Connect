package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RequestEvidenceRequest {

    @NotBlank(message = "Đối tượng yêu cầu bằng chứng không được để trống (BOTH, PT, STUDENT)")
    private String target; // BOTH, PT, STUDENT

    @NotBlank(message = "Nội dung yêu cầu bằng chứng không được để trống")
    private String note;
}
