package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewVerdictRequest {

    @NotBlank(message = "Quyết định xử lý không được để trống (REMOVE, KEEP, REQUEST_EVIDENCE)")
    private String decision;

    @NotBlank(message = "Lý do / Ghi chú phán quyết của Quản trị viên không được để trống")
    private String adminNote;
}

