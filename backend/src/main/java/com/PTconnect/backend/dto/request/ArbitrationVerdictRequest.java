package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ArbitrationVerdictRequest {

    @NotBlank(message = "Loại phán quyết không được để trống")
    private String verdictType; // REFUND_STUDENT, PAID_PT, FORCE_MAJEURE, DISMISS

    private String customNote;
}
