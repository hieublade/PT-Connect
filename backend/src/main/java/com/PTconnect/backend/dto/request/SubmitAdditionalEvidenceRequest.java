package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SubmitAdditionalEvidenceRequest {

    @NotBlank(message = "Nội dung bằng chứng bổ sung không được để trống")
    private String evidence;
}
