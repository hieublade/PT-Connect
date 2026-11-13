package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CounterStatementRequest {

    @NotBlank(message = "Nội dung phản biện đối chứng không được để trống")
    private String counterStatement;
}
