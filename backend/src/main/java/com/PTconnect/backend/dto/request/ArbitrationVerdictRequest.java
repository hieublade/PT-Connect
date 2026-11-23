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
    private String verdictType;

    private String customNote;

    private String verdictReason;

    private Boolean bypass48hWaiting;
}

